#!/usr/bin/env python3
"""Repository-only DeepSeek APK audit. Emits compact, privacy-safe evidence indexes."""
from __future__ import annotations
import argparse, collections, gzip, hashlib, json, pathlib, re, shutil, struct, subprocess, zipfile, xml.etree.ElementTree as ET

# Covers the largest complete positive value-edge inventory in the audited 2.7.1–2.7.5 APKs.
# If a future build exceeds this bound, the summary remains truncated and Kotlin refuses DATA_FLOW evidence.
MAX_INTERPROCEDURAL_VALUE_EDGES = 400_000

ROUTES = (
    "/api/v0/chat/completion", "/api/v0/chat/regenerate", "/api/v0/chat/continue",
    "/api/v0/chat/edit_message", "/api/v0/chat/resume_stream",
    "/api/v0/chat/create_pow_challenge", "/api/v0/chat/stop_stream",
    "/api/v0/chat/history_messages", "/api/v0/chat/message_feedback",
)
ANCHORS = {
    "request_route": ROUTES,
    "pow": ("PowCalculator", "DeepSeekHashV1", "X-DS-PoW-Response", "X-DS-Challenge-Response", "create_pow_challenge"),
    "sse_transport": ("text/event-stream", "ByteReadChannel", "readUTF8Line", "x-ds-sse-heartbeat-timeout-secs"),
    "sse_dispatch": ("DeltaCommand", "update_session", "update_parent_message", "auto_tts_capability", "check_client_update"),
    "flow_coroutine": ("kotlinx.coroutines.flow.Flow", "Continuation", "emit", "collect"),
    "serialization": ("kotlinx.serialization", "SerialDescriptor", "serializer", "SerializersModule"),
    "agent_tool": ("ToolOpenFragment", "ToolFindFragment", "SearchFragment", "tool_calls", "tool_use", "MCP"),
    "session": ("conversation_id", "session_id", "message_id", "history_messages", "resume_stream"),
    "prompt_pipeline": ("system_prompt", "systemPrompt", "custom_instructions", "customInstructions", "prompt_template", "promptTemplate", "instruction", "role_prompt", "context_window", "prompt"),
    "agent_planning": ("agent", "Agent", "plan", "planner", "task_step", "tool_calls", "tool_call", "tool_use", "function_call"),
    "tool_registry_execution": ("ToolRegistry", "ToolExecutor", "ToolCall", "ToolResult", "Mcp", "MCP", "SearchFragment", "ToolOpenFragment", "ToolFindFragment"),
    "local_api_gateway": ("127.0.0.1", "0.0.0.0", "/v1/chat/completions", "/v1/models", "LocalApi", "LocalApiServer", "HttpServer", "ktor-server"),
    "multimodal_image": ("image_url", "image/jpeg", "image/png", "ImagePart", "ImageContent", "vision"),
    "multimodal_audio": ("audio", "audio/mpeg", "audio/wav", "speech", "transcription", "text-to-speech", "tts"),
    "attachment_file": ("multipart/form-data", "application/pdf", "content://", "FileProvider", "Attachment", "upload"),
    "search_web": ("SearchFragment", "search_query", "web_search", "citation", "sources", "reference"),
    "storage_sync": ("RoomDatabase", "DataStore", "SharedPreferences", "conversation_history", "sync"),
    "account_capability": ("subscription", "quota", "model_capability", "feature_flag", "remote_config"),
    "ui_settings": ("Settings", "Preference", "ViewModel", "NavController", "Compose"),
}
SENSITIVE = re.compile(r"(?i)(authorization|bearer\s+|cookie|api[_-]?key|access[_-]?token|refresh[_-]?token|password|message[_-]?content)")
SAFE_PROMPT_MARKER = re.compile(r"(?i)^(system_?prompt|custom_?instructions?|prompt_?(template|id|type|source)|instruction_?(enabled|source|type)|context_window)$")
METHOD_RE = re.compile(r"^\.method\s+(.+?)\s+([^\s(]+)(\([^)]*\).+)$")
CLASS_RE = re.compile(r"^\.class\s+.*?\s+(L[^;]+;)")
SUPER_RE = re.compile(r"^\.super\s+(L[^;]+;)")
IMPL_RE = re.compile(r"^\.implements\s+(L[^;]+;)")
INVOKE_RE = re.compile(r"\binvoke-[\w/-]+\s+\{[^}]*\},?\s*(L[^;]+;)->([^ (]+)(\([^)]*\).+)")
OP_RE = re.compile(r"^\s*([a-z][a-z0-9_/-]+)(?:\s|$)")
FIELD_ACCESS_RE = re.compile(r"\b([is](?:get|put)(?:-[a-z]+)*)\s+.*?,\s*(L[^;]+;)->([^:]+):(\S+)")
BRANCH_RE = re.compile(r"^\s*(?:if-[a-z-]+|goto(?:/16|/32)?|packed-switch|sparse-switch)\b")
LABEL_RE = re.compile(r"^\s*:[A-Za-z0-9_$-]+\s*$")
STR_RE = re.compile(r'const-string(?:/jumbo)?\s+[^,]+,\s+"((?:\\.|[^"])*)"')

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def write_jsonl_gzip(path, records):
    """Write one independently parseable JSON record per physical line."""
    with gzip.open(path, "wt", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n")


def dex_header(data):
    if len(data)<112 or not data.startswith(b"dex\n"): return None
    u=lambda off: struct.unpack_from("<I",data,off)[0]
    return {"magic":data[:8].decode("latin1").replace("\0",""),"bytes":len(data),
            "header_file_size":u(32),"string_ids":u(56),"type_ids":u(64),"proto_ids":u(72),
            "field_ids":u(80),"method_ids":u(88),"class_defs":u(96),
            "file_size_matches":u(32)==len(data),"adler32_header":u(8)}

def run(cmd,log):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace")
    pathlib.Path(log).write_text(p.stdout,errors="replace")
    return p.returncode

def parse_aapt_badging(output, exit_code=0):
    result={"aapt_exit":exit_code}
    line=next((x for x in output.splitlines() if x.startswith("package: ")), "")
    if line:
        for key in ("name","versionCode","versionName","split"):
            m=re.search(r"(?:^|\s)"+re.escape(key)+r"='([^']*)'",line)
            if m: result[{"name":"package","versionCode":"version_code","versionName":"version_name","split":"split"}[key]]=m.group(1) or None
    return result

def aapt_badging(aapt, apk, log_path):
    if not aapt: return {}
    p=subprocess.run([aapt,"dump","badging",str(apk)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace")
    pathlib.Path(log_path).write_text(p.stdout,errors="replace")
    return parse_aapt_badging(p.stdout,p.returncode)

def parse_signing_certificates(output, exit_code=0):
    digests = []
    pattern = r"Signer(?: #\d+)?(?: \(minSdkVersion=[^)]+\))? certificate SHA-256 digest:\s*([0-9a-fA-F]{64})"
    for value in re.findall(pattern, output):
        normalized = value.lower()
        if normalized not in digests: digests.append(normalized)
    return {"apksigner_exit":exit_code,"signing_sha256":digests[0] if digests else None,"signing_sha256s":digests}

def signing_certificate(apksigner, apk, log_path):
    if not apksigner: return {}
    p=subprocess.run([apksigner,"verify","--print-certs",str(apk)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors="replace")
    pathlib.Path(log_path).write_text(p.stdout,errors="replace")
    return parse_signing_certificates(p.stdout,p.returncode)


def safe_strings(line):
    m=STR_RE.search(line)
    if not m: return []
    value=m.group(1)
    # Preserve Smali-escaped text verbatim; unicode_escape corrupts non-ASCII and can create surrogates.
    # Preserve schema identifiers for prompt discovery, but never index prompt bodies.
    if SENSITIVE.search(value) and not SAFE_PROMPT_MARKER.fullmatch(value): return ["<redacted-content>"]
    if re.search(r"(?i)prompt|instruction", value) and not SAFE_PROMPT_MARKER.fullmatch(value): return ["<redacted-content>"]
    return [value[:240]]

def build_smali_cfg(body_lines):
    """Build a conservative instruction-index CFG from one Smali method body.

    Payload pseudo-instructions are excluded from executable instruction indices.
    The result explicitly reports unresolved labels and truncation; it is not a
    verifier-grade DEX CFG and must not be treated as complete when flagged.
    """
    instructions=[]; labels={}; payload_labels=set(); switch_payloads={}
    catches=[]; active_payload=None; active_payload_label=None; last_label=None
    label_re=re.compile(r"^\s*(:[A-Za-z0-9_$-]+)\s*$")
    catch_re=re.compile(r"^\s*\.catch(?:all)?\b.*?\{\s*(:[\w$-]+)\s+\.\.\s+(:[\w$-]+)\s*\}\s*(:[\w$-]+)")
    switch_entry_re=re.compile(r"^\s*(?:-?0x[0-9a-fA-F]+|-?\d+)\s*->\s*(:[\w$-]+)")
    for line_no,line in enumerate(body_lines,1):
        stripped=line.strip()
        lm=label_re.match(line)
        if lm:
            label=lm.group(1)
            labels[label]=len(instructions)
            last_label=label
            if active_payload is not None:
                payload_labels.add(label)
                active_payload_label=label
            continue
        if active_payload is not None:
            if stripped.startswith(".end "):
                active_payload=None; active_payload_label=None
            else:
                sm=switch_entry_re.match(line)
                if sm and active_payload_label:
                    switch_payloads.setdefault(active_payload_label,[]).append(sm.group(1))
            continue
        if stripped.startswith(".packed-switch") or stripped.startswith(".sparse-switch"):
            active_payload="switch"
            active_payload_label=last_label
            if last_label: payload_labels.add(last_label)
            continue
        if stripped.startswith(".array-data"):
            active_payload="array"
            active_payload_label=last_label
            if last_label: payload_labels.add(last_label)
            continue
        cm=catch_re.match(line)
        if cm:
            catches.append(cm.groups())
            continue
        if not stripped or stripped.startswith((".", "#")):
            continue
        opm=OP_RE.match(line)
        if opm:
            instructions.append({"op":opm.group(1),"text":stripped,"line":line_no})

    count=len(instructions)
    if count == 0:
        return {"instruction_count":0,"block_count":0,"edge_count":0,
                "unresolved_target_count":0,"complete":True,"edges":[],"edges_truncated":False}
    leaders={0}; unresolved=[]
    branch_target_re=re.compile(r"(:[A-Za-z0-9_$-]+)")
    terminal=lambda op: op.startswith(("return","throw"))
    conditional=lambda op: op.startswith("if-")
    goto=lambda op: op.startswith("goto")
    switch=lambda op: op in ("packed-switch","sparse-switch")
    for index,ins in enumerate(instructions):
        op=ins["op"]; text=ins["text"]
        if conditional(op) or goto(op):
            matches=branch_target_re.findall(text)
            target=matches[-1] if matches else None
            if target and target in labels and target not in payload_labels:
                leaders.add(labels[target])
            else:
                unresolved.append(target or "<missing-branch-label>")
            if index+1<count: leaders.add(index+1)
        elif switch(op):
            matches=branch_target_re.findall(text)
            payload=matches[-1] if matches else None
            if payload not in labels or payload not in payload_labels:
                unresolved.append(payload or "<missing-switch-payload>")
            else:
                if index+1<count: leaders.add(index+1)
                for target in switch_payloads.get(payload,[]):
                    if target in labels and target not in payload_labels:
                        leaders.add(labels[target])
                    else:
                        unresolved.append(target)
        elif terminal(op) and index+1<count:
            leaders.add(index+1)

    catch_ranges=[]
    for start_label,end_label,handler_label in catches:
        if start_label not in labels or end_label not in labels or handler_label not in labels:
            unresolved.append("catch-range:" + ",".join((start_label,end_label,handler_label)))
            continue
        start,end,handler=labels[start_label],labels[end_label],labels[handler_label]
        leaders.add(start)
        if end<count: leaders.add(end)
        leaders.add(handler)
        catch_ranges.append((start,end,handler))

    starts=sorted(x for x in leaders if 0 <= x < count)
    block_for={}; blocks=[]
    for block_id,start in enumerate(starts):
        end=(starts[block_id+1]-1) if block_id+1<len(starts) else count-1
        blocks.append({"id":block_id,"start":start,"end":end})
        for ix in range(start,end+1): block_for[ix]=block_id
    edges=set()
    def add_edge(src_index,target_index,kind):
        if target_index is None or target_index<0 or target_index>=count: return
        src=block_for[src_index]; dst=block_for[target_index]
        if src != dst: edges.add((src,dst,kind))
    for block in blocks:
        ix=block["end"]; ins=instructions[ix]; op=ins["op"]; matches=branch_target_re.findall(ins["text"])
        if conditional(op):
            target=matches[-1] if matches else None
            if target in labels and target not in payload_labels: add_edge(ix,labels[target],"conditional")
            if ix+1<count: add_edge(ix,ix+1,"fallthrough")
        elif goto(op):
            target=matches[-1] if matches else None
            if target in labels and target not in payload_labels: add_edge(ix,labels[target],"goto")
        elif switch(op):
            payload=matches[-1] if matches else None
            if payload in labels and payload in payload_labels:
                for target in switch_payloads.get(payload,[]):
                    if target in labels and target not in payload_labels: add_edge(ix,labels[target],"switch")
            if ix+1<count: add_edge(ix,ix+1,"switch-default")
        elif not terminal(op) and ix+1<count:
            add_edge(ix,ix+1,"fallthrough")
    for start,end,handler in catch_ranges:
        for block in blocks:
            if start <= block["start"] < end:
                add_edge(block["end"],handler,"exception")
    edge_list=[{"from":a,"to":b,"kind":kind} for a,b,kind in sorted(edges)]
    return {"instruction_count":count,"block_count":len(blocks),"edge_count":len(edge_list),
        "unresolved_target_count":len(unresolved),"unresolved_targets":sorted(set(unresolved))[:32],
        "complete":not unresolved and len(edge_list)<=256,"edges":edge_list[:256],"edges_truncated":len(edge_list)>256,
        "blocks":blocks,"blocks_truncated":False}


def analyze_register_use_def(body_lines):
    """Extract conservative per-instruction Dalvik register reads/writes.

    This is local instruction use-def metadata, not reaching-definitions analysis.
    Unknown opcodes are reported and never silently treated as having no uses.
    """
    register_re=re.compile(r"\b([vp])(\d+)\b")
    def registers_in(text):
        range_match=re.search(r"\{\s*([vp])(\d+)\s*\.\.\s*([vp])(\d+)\s*\}",text)
        if range_match and range_match.group(1)==range_match.group(3):
            prefix,start,end=range_match.group(1),int(range_match.group(2)),int(range_match.group(4))
            if end>=start and end-start<=255:
                return [prefix+str(index) for index in range(start,end+1)]
        return [prefix+number for prefix,number in register_re.findall(text)]
    result=[]; unknown=[]
    read_all_prefixes=("invoke-", "filled-new-array")
    write_first_prefixes=(
        "move", "const", "new-instance", "new-array", "array-length", "instance-of",
        "iget", "sget", "aget", "neg-", "not-", "int-to-", "long-to-", "float-to-",
        "double-to-", "add-", "sub-", "mul-", "div-", "rem-", "and-", "or-",
        "xor-", "shl-", "shr-", "ushr-", "cmp"
    )
    read_only_prefixes=("return", "throw", "if-", "packed-switch", "sparse-switch",
                        "iput", "sput", "aput", "monitor-", "check-cast")
    for line_no,line in enumerate(body_lines,1):
        stripped=line.strip()
        match=OP_RE.match(line)
        if not match or stripped.startswith((".",":","#")):
            continue
        op=match.group(1)
        regs=registers_in(stripped)
        if not regs:
            continue
        # Wide Dalvik values occupy register pairs. Until pair-aware transfer
        # functions are implemented, do not certify these instructions as complete.
        if "wide" in op or "long" in op or "double" in op:
            unknown.append({"line":line_no,"opcode":op,"reason":"wide-register-pair-not-modeled"})
            continue
        if op.startswith(read_all_prefixes) or op.startswith(read_only_prefixes):
            reads=regs
            writes=[]
            if op.startswith("check-cast"):
                writes=regs[:1]
        elif "/2addr" in op:
            reads=regs
            writes=regs[:1]
        elif op.startswith(write_first_prefixes):
            writes=regs[:1]
            reads=regs[1:]
        elif op.startswith(("move-exception", "move-result")):
            writes=regs[:1]; reads=regs[1:]
        elif op in ("nop",):
            reads=[]; writes=[]
        else:
            unknown.append({"line":line_no,"opcode":op})
            continue
        result.append({"line":line_no,"opcode":op,"reads":sorted(set(reads)),
                       "writes":sorted(set(writes))})
    all_reads=sorted({r for item in result for r in item["reads"]})
    all_writes=sorted({r for item in result for r in item["writes"]})
    return {
        "instruction_count":len(result),"read_registers":all_reads,
        "written_registers":all_writes,"unknown_opcode_count":len(unknown),
        "unknown_opcodes":unknown[:32],"complete":not unknown,
        "instructions":result[:256],"instructions_truncated":len(result)>256
    }



def analyze_register_dataflow(body_lines, cfg, parameter_registers=()):
    """Conservative intraprocedural reaching-definitions over the recovered CFG."""
    executable=[]
    for line_no,line in enumerate(body_lines,1):
        match=OP_RE.match(line)
        if not match or line.lstrip().startswith((".",":","#")):
            continue
        op=match.group(1)
        facts=analyze_register_use_def([line])
        item=facts["instructions"][0] if facts["instructions"] else None
        executable.append({"index":len(executable),"line":line_no,"opcode":op,
                           "reads":item["reads"] if item else [],
                           "writes":item["writes"] if item else [],
                           "known":not facts["unknown_opcode_count"]})
    blocks=cfg.get("blocks",[])
    if not executable or not blocks:
        return {"complete":False,"reason":"missing-instruction-or-block-index",
                "instruction_count":len(executable),"definition_count":0,
                "use_count":0,"ambiguous_use_count":0,"unresolved_use_count":0,
                "uses":[],"definitions":[]}
    block_by_instruction={}
    for block in blocks:
        for index in range(block["start"],block["end"]+1):
            block_by_instruction[index]=block["id"]
    if len(block_by_instruction)!=len(executable):
        return {"complete":False,"reason":"cfg-instruction-index-mismatch",
                "instruction_count":len(executable),"definition_count":0,
                "use_count":0,"ambiguous_use_count":0,"unresolved_use_count":0,
                "uses":[],"definitions":[]}
    predecessors={b["id"]:set() for b in blocks}
    for edge in cfg.get("edges",[]):
        if edge["to"] in predecessors and edge["from"] in predecessors:
            predecessors[edge["to"]].add(edge["from"])
    definitions=[]; defs_by_instruction={}
    all_defs_by_register=collections.defaultdict(set)
    entry_definitions=set()
    for reg in parameter_registers:
        ident="entry:{}".format(reg)
        definitions.append({"id":ident,"register":reg,"instruction":-1,
                            "line":0,"opcode":"method-parameter","kind":"parameter"})
        all_defs_by_register[reg].add(ident)
        entry_definitions.add(ident)
    for ins in executable:
        current=set()
        for reg in ins["writes"]:
            ident="d{}:{}".format(ins["index"],reg)
            definitions.append({"id":ident,"register":reg,"instruction":ins["index"],
                                "line":ins["line"],"opcode":ins["opcode"],"kind":"instruction"})
            current.add(ident); all_defs_by_register[reg].add(ident)
        defs_by_instruction[ins["index"]]=current
    gen={b["id"]:set() for b in blocks}; kill={b["id"]:set() for b in blocks}
    last_definition={}
    for ins in executable:
        bid=block_by_instruction[ins["index"]]
        for ident in defs_by_instruction[ins["index"]]:
            reg=ident.split(":",1)[1]
            last_definition[(bid,reg)]=ident
    for (bid,reg),ident in last_definition.items():
        gen[bid].add(ident)
        kill[bid].update(all_defs_by_register[reg]-{ident})
    incoming={b["id"]:set() for b in blocks}
    outgoing={b["id"]:set(gen[b["id"]]) for b in blocks}
    changed=True; iterations=0
    while changed and iterations<max(8,len(blocks)*4):
        changed=False; iterations+=1
        for block in blocks:
            bid=block["id"]
            new_in=set().union(*(outgoing[p] for p in predecessors[bid])) if predecessors[bid] else set()
            if bid==min(b["id"] for b in blocks):
                new_in.update(entry_definitions)
            new_out=gen[bid]|(new_in-kill[bid])
            if new_in!=incoming[bid] or new_out!=outgoing[bid]:
                incoming[bid]=new_in; outgoing[bid]=new_out; changed=True
    uses=[]; ambiguous=0; unresolved=0
    for ins in executable:
        bid=block_by_instruction[ins["index"]]; reaching=set(incoming[bid])
        for index in range(blocks[bid]["start"],ins["index"]):
            # A new definition kills every older definition of the same register,
            # including method-entry parameters and definitions from predecessors.
            for written_register in executable[index]["writes"]:
                reaching.difference_update(all_defs_by_register[written_register])
            reaching.update(defs_by_instruction[index])
        for reg in ins["reads"]:
            matches=sorted(d for d in reaching if d.endswith(":"+reg))
            state="resolved" if len(matches)==1 else ("ambiguous" if matches else "unresolved")
            ambiguous+=state=="ambiguous"; unresolved+=state=="unresolved"
            uses.append({"register":reg,"instruction":ins["index"],"line":ins["line"],
                         "opcode":ins["opcode"],"reaching_definitions":matches[:16],
                         "resolution":state})
    known=all(x["known"] for x in executable)
    definitions_truncated=len(definitions)>256
    uses_truncated=len(uses)>512
    complete=bool(cfg.get("complete")) and known and not changed and not definitions_truncated and not uses_truncated
    reason=(None if complete else
            ("unknown-opcodes" if not known else
             "evidence-truncated" if definitions_truncated or uses_truncated else
             "incomplete-cfg-or-nonconvergence"))
    return {"complete":complete,"reason":reason,
            "instruction_count":len(executable),"definition_count":len(definitions),
            "parameter_definition_count":len(entry_definitions),
            "use_count":len(uses),"ambiguous_use_count":ambiguous,
            "unresolved_use_count":unresolved,"iterations":iterations,
            "definitions":definitions[:256],"definitions_truncated":definitions_truncated,
            "uses":uses[:512],"uses_truncated":uses_truncated}

def parse_method_descriptor(descriptor):
    """Return JVM/Dalvik parameter and return types without losing array/object widths."""
    if not descriptor.startswith("(") or ")" not in descriptor:
        return None
    def parse_one(text, offset):
        start=offset
        while offset<len(text) and text[offset]=="[":
            offset+=1
        if offset>=len(text): return None
        if text[offset]=="L":
            end=text.find(";",offset)
            if end<0: return None
            return text[start:end+1],end+1
        if text[offset] in "VZBSCIJFD":
            return text[start:offset+1],offset+1
        return None
    close=descriptor.find(")")
    params=[]; offset=1
    while offset<close:
        parsed=parse_one(descriptor,offset)
        if not parsed: return None
        value,offset=parsed
        params.append(value)
    result=parse_one(descriptor,close+1)
    if not result or result[1]!=len(descriptor): return None
    return {"parameters":params,"return_type":result[0]}


def parameter_registers_for_method(access, descriptor):
    parsed=parse_method_descriptor(descriptor)
    if not parsed: return []
    word=0 if "static" in access.split() else 1
    registers=[]
    if word: registers.append("p0")
    for value in parsed["parameters"]:
        width=2 if value in ("J","D") else 1
        registers.extend("p{}".format(word+i) for i in range(width))
        word+=width
    return registers


def parse_invoke_registers(register_text):
    text=register_text.strip()
    range_match=re.fullmatch(r"([vp])(\d+)\s*\.\.\s*([vp])(\d+)",text)
    if range_match and range_match.group(1)==range_match.group(3):
        prefix=range_match.group(1); start=int(range_match.group(2)); end=int(range_match.group(4))
        if end>=start and end-start<=255:
            return [prefix+str(i) for i in range(start,end+1)]
        return []
    return re.findall(r"\b[vp]\d+\b",text)


def extract_invoke_sites(body_lines):
    """Capture invoke argument registers and the immediately following move-result."""
    detail_re=re.compile(r"\b(invoke-[\w/-]+)\s+\{([^}]*)\},?\s*(L[^;]+;)->([^ (]+)(\([^)]*\).+)")
    sites=[]; pending=None; instruction_index=0
    for line_no,line in enumerate(body_lines,1):
        op_match=OP_RE.match(line)
        if not op_match or line.lstrip().startswith((".",":","#")):
            continue
        op=op_match.group(1)
        match=detail_re.search(line)
        if match and not match.group(1).startswith(("invoke-custom","invoke-polymorphic")):
            opcode,register_text,owner,name,descriptor=match.groups()
            site={"instruction":instruction_index,"line":line_no,"opcode":opcode,
                  "owner":owner,"name":name,"descriptor":descriptor,
                  "registers":parse_invoke_registers(register_text),
                  "result_instruction":None,"result_register":None}
            sites.append(site); pending=len(sites)-1
        elif op.startswith("move-result") and pending is not None:
            registers=re.findall(r"\b[vp]\d+\b",line)
            if registers:
                sites[pending]["result_instruction"]=instruction_index
                sites[pending]["result_register"]=registers[0]
            pending=None
        else:
            pending=None
        instruction_index+=1
    return sites


def extract_field_access_sites(body_lines):
    """Record field slot plus receiver/value registers; instance identity is not inferred here."""
    field_re=re.compile(r"\b([is](?:get|put)(?:-[a-z]+)*)\s+([^,]+)(?:,\s*([^,]+))?,\s*(L[^;]+;)->([^:]+):(\S+)")
    result=[]; instruction_index=0
    for line_no,line in enumerate(body_lines,1):
        op_match=OP_RE.match(line)
        if not op_match or line.lstrip().startswith((".",":","#")):
            continue
        match=field_re.search(line)
        if match:
            opcode,value_reg,object_reg,owner,name,field_type=match.groups()
            is_static=opcode.startswith(("sget","sput"))
            is_read=opcode.startswith(("iget","sget"))
            result.append({"instruction":instruction_index,"line":line_no,"opcode":opcode,
                           "field":owner+"->"+name+":"+field_type,
                           "access":"read" if is_read else "write",
                           "value_register":value_reg.strip(),
                           "object_register":None if is_static or not object_reg else object_reg.strip(),
                           "static":is_static})
        instruction_index+=1
    return result


def object_parameter_registers_for_method(access, descriptor):
    """Return receiver and reference-typed formal registers (wide words excluded)."""
    parsed=parse_method_descriptor(descriptor)
    if not parsed:
        return []
    registers=[]
    word=0
    if "static" not in access.split():
        registers.append("p0")
        word=1
    for param_type in parsed["parameters"]:
        if param_type.startswith(("L","[")):
            registers.append("p{}".format(word))
        word += 2 if param_type in ("J","D") else 1
    return registers


def analyze_object_points_to(body_lines, cfg, owner, method_name, descriptor,
                             access, field_access_sites, invoke_sites=()):
    """Conservative intraprocedural points-to for parameters, allocations and move-object.

    Unsupported object-producing instructions become unknown. Only a singleton,
    non-unknown abstract object identity is eligible for same-instance evidence.
    """
    executable=[]
    for line_no,line in enumerate(body_lines,1):
        match=OP_RE.match(line)
        if not match or line.lstrip().startswith((".",":","#")):
            continue
        facts=analyze_register_use_def([line])
        item=facts["instructions"][0] if facts["instructions"] else None
        executable.append({"index":len(executable),"line":line_no,"opcode":match.group(1),
                           "writes":item["writes"] if item else [],
                           "known":not facts["unknown_opcode_count"]})
    blocks=cfg.get("blocks",[])
    if not cfg.get("complete") or not executable or not blocks:
        return {"complete":False,"reason":"incomplete-cfg-or-empty-method",
                "field_receivers":[],"same_instance_groups":[],"return_values":[]}
    block_by_instruction={}
    for block in blocks:
        for index in range(block["start"],block["end"]+1):
            block_by_instruction[index]=block["id"]
    if len(block_by_instruction)!=len(executable) or not all(x["known"] for x in executable):
        return {"complete":False,"reason":"instruction-index-mismatch-or-unknown-opcode",
                "field_receivers":[],"same_instance_groups":[],"return_values":[]}
    predecessors={b["id"]:set() for b in blocks}
    normal_predecessors={b["id"]:set() for b in blocks}
    exception_predecessors={b["id"]:set() for b in blocks}
    successors={b["id"]:set() for b in blocks}
    for edge in cfg.get("edges",[]):
        if edge["from"] in predecessors and edge["to"] in predecessors:
            predecessors[edge["to"]].add(edge["from"])
            successors[edge["from"]].add(edge["to"])
            if edge.get("kind")=="exception":
                exception_predecessors[edge["to"]].add(edge["from"])
            else:
                normal_predecessors[edge["to"]].add(edge["from"])
    cyclic_blocks=set()
    for start in successors:
        pending=list(successors[start]); visited=set()
        while pending:
            current=pending.pop()
            if current==start:
                cyclic_blocks.add(start)
                break
            if current in visited:
                continue
            visited.add(current)
            pending.extend(successors.get(current,()))
    cyclic_allocation_count=sum(
        1 for ins in executable
        if ins["opcode"].startswith("new-instance")
        and block_by_instruction[ins["index"]] in cyclic_blocks)
    method_key=owner+"->"+method_name+descriptor
    entry_points={reg:{"param:{}:{}".format(method_key,reg)}
                  for reg in object_parameter_registers_for_method(access,descriptor)}
    in_points={b["id"]:{} for b in blocks}
    out_points={b["id"]:{} for b in blocks}
    in_unknown={b["id"]:set() for b in blocks}
    out_unknown={b["id"]:set() for b in blocks}
    # An exception may leave a protected block before any later instruction runs.
    # Preserve the union of every pre/post-instruction state for exceptional edges.
    exceptional_out_points={b["id"]:{} for b in blocks}
    exceptional_out_unknown={b["id"]:set() for b in blocks}

    def merge_maps(maps):
        merged=collections.defaultdict(set)
        for mapping in maps:
            for reg,values in mapping.items():
                merged[reg].update(values)
        return {reg:set(values) for reg,values in merged.items()}

    def transfer(index, points, unknown):
        ins=executable[index]
        line=body_lines[ins["line"]-1].strip()
        op=ins["opcode"]
        new_points={reg:set(values) for reg,values in points.items()}
        new_unknown=set(unknown)
        if op.startswith("new-instance"):
            match=re.search(r"\bnew-instance\s+([vp]\d+)\s*,\s*(L[^;]+;)",line)
            if match:
                dest,allocated_type=match.groups()
                if block_by_instruction[index] in cyclic_blocks:
                    new_points[dest]=set()
                    new_unknown.add(dest)
                else:
                    new_points[dest]={"alloc:{}#{}:{}".format(method_key,index,allocated_type)}
                    new_unknown.discard(dest)
            else:
                for dest in ins["writes"]:
                    new_points[dest]=set(); new_unknown.add(dest)
        elif op.startswith("move-object"):
            match=re.search(r"\bmove-object(?:/(?:from16|16))?\s+([vp]\d+)\s*,\s*([vp]\d+)",line)
            if match:
                dest,src=match.groups()
                new_points[dest]=set(new_points.get(src,set()))
                if src in new_unknown:
                    new_unknown.add(dest)
                else:
                    new_unknown.discard(dest)
            else:
                for dest in ins["writes"]:
                    new_points[dest]=set(); new_unknown.add(dest)
        elif op.startswith("check-cast"):
            pass
        else:
            object_result=(op.startswith(("move-result-object","iget-object","sget-object",
                                          "aget-object","const-string","const-class")))
            for dest in ins["writes"]:
                new_points[dest]=set()
                if object_result:
                    new_unknown.add(dest)
                else:
                    new_unknown.discard(dest)
        return new_points,new_unknown

    changed=True
    iterations=0
    limit=max(8,len(blocks)*4)
    while changed and iterations<limit:
        changed=False
        iterations+=1
        for block in blocks:
            bid=block["id"]
            pred_points=[out_points[p] for p in normal_predecessors[bid]]
            pred_points.extend(exceptional_out_points[p] for p in exception_predecessors[bid])
            pred_unknown=[out_unknown[p] for p in normal_predecessors[bid]]
            pred_unknown.extend(exceptional_out_unknown[p] for p in exception_predecessors[bid])
            new_in=merge_maps(pred_points)
            new_in_unknown=set().union(*pred_unknown) if pred_unknown else set()
            if bid==min(b["id"] for b in blocks):
                for reg,values in entry_points.items():
                    new_in.setdefault(reg,set()).update(values)
            current_points={reg:set(values) for reg,values in new_in.items()}
            current_unknown=set(new_in_unknown)
            exceptional_states=[({reg:set(values) for reg,values in current_points.items()},
                                 set(current_unknown))]
            for index in range(block["start"],block["end"]+1):
                current_points,current_unknown=transfer(index,current_points,current_unknown)
                # Include both sides of each instruction: a throwing instruction may
                # expose its incoming state, while a completed one may expose its output.
                exceptional_states.append(({reg:set(values) for reg,values in current_points.items()},
                                           set(current_unknown)))
            exceptional_points=merge_maps([state[0] for state in exceptional_states])
            exceptional_unknown=set().union(*(state[1] for state in exceptional_states))
            if (new_in!=in_points[bid] or new_in_unknown!=in_unknown[bid]
                    or current_points!=out_points[bid] or current_unknown!=out_unknown[bid]
                    or exceptional_points!=exceptional_out_points[bid]
                    or exceptional_unknown!=exceptional_out_unknown[bid]):
                in_points[bid]=new_in
                in_unknown[bid]=new_in_unknown
                out_points[bid]=current_points
                out_unknown[bid]=current_unknown
                exceptional_out_points[bid]=exceptional_points
                exceptional_out_unknown[bid]=exceptional_unknown
                changed=True
    if changed:
        return {"complete":False,"reason":"points-to-nonconvergence",
                "field_receivers":[],"same_instance_groups":[],"return_values":[]}

    field_by_instruction={site["instruction"]:site for site in field_access_sites
                          if site.get("object_register")}
    invoke_by_instruction={site["instruction"]:site for site in invoke_sites}
    receiver_facts=[]
    invoke_argument_facts=[]
    return_values=[]
    for block in blocks:
        bid=block["id"]
        points={reg:set(values) for reg,values in in_points[bid].items()}
        unknown=set(in_unknown[bid])
        for index in range(block["start"],block["end"]+1):
            instruction=executable[index]
            if instruction["opcode"].startswith("return-object"):
                return_line=body_lines[instruction["line"]-1].strip()
                return_regs=re.findall(r"\b[vp]\d+\b",return_line)
                if return_regs:
                    return_reg=return_regs[0]
                    return_ids=sorted(points.get(return_reg,set()))
                    return_unknown=return_reg in unknown
                    return_values.append({
                        "instruction":index,"register":return_reg,
                        "points_to":return_ids,"unknown":return_unknown,
                        "identity_status":("unknown" if return_unknown else
                            "singleton" if len(return_ids)==1 else
                            "multiple" if len(return_ids)>1 else "unresolved")
                    })
                else:
                    return_values.append({
                        "instruction":index,"register":None,"points_to":[],
                        "unknown":True,"identity_status":"unknown"
                    })
            invoke_site=invoke_by_instruction.get(index)
            if invoke_site:
                parsed=parse_method_descriptor(invoke_site.get("descriptor",""))
                actual=list(invoke_site.get("registers",[]))
                is_static=invoke_site.get("opcode","").startswith("invoke-static")
                formal_word=0
                actual_word=0
                object_arguments=[]
                if not is_static:
                    object_arguments.append((actual[0] if actual else None,"p0","receiver"))
                    actual_word=1
                    formal_word=1
                if parsed:
                    for parameter_type in parsed["parameters"]:
                        width=2 if parameter_type in ("J","D") else 1
                        if parameter_type.startswith(("L","[")):
                            actual_reg=actual[actual_word] if actual_word<len(actual) else None
                            object_arguments.append((actual_reg,"p{}".format(formal_word),"argument"))
                        actual_word+=width
                        formal_word+=width
                aligned=parsed is not None and actual_word==len(actual)
                for actual_reg,formal_reg,argument_kind in object_arguments:
                    identities=sorted(points.get(actual_reg,set())) if actual_reg else []
                    is_unknown=(actual_reg in unknown) if actual_reg else True
                    status=("singleton" if len(identities)==1 and not is_unknown else
                            "unknown" if is_unknown else
                            "multiple" if len(identities)>1 else "unresolved")
                    invoke_argument_facts.append({
                        "call_instruction":index,"call_line":invoke_site.get("line"),
                        "owner":invoke_site.get("owner"),"name":invoke_site.get("name"),
                        "descriptor":invoke_site.get("descriptor"),
                        "formal_register":formal_reg,"actual_register":actual_reg,
                        "argument_kind":argument_kind,"points_to":identities,
                        "unknown":is_unknown,"identity_status":status,
                        "mapping_complete":aligned
                    })
            site=field_by_instruction.get(index)
            if site:
                reg=site["object_register"]
                identities=sorted(points.get(reg,set()))
                is_unknown=reg in unknown
                status=("singleton" if len(identities)==1 and not is_unknown else
                        "unknown" if is_unknown else
                        "multiple" if len(identities)>1 else "unresolved")
                receiver_facts.append({
                    "instruction":index,"field":site["field"],"access":site["access"],
                    "receiver_register":reg,"points_to":identities,
                    "unknown":is_unknown,"identity_status":status,
                    "identity":identities[0] if status=="singleton" else None
                })
            points,unknown=transfer(index,points,unknown)
    groups=collections.defaultdict(list)
    for fact in receiver_facts:
        if fact["identity_status"]=="singleton":
            groups[(fact["field"],fact["identity"])].append(fact["instruction"])
    same_instance_groups=[
        {"field":field,"identity":identity,"instructions":sorted(set(indices)),
         "same_instance_within_single_activation":True,
         "identity_scope":"single-method-activation"}
        for (field,identity),indices in groups.items() if len(set(indices))>1
    ]
    return {"complete":True,"reason":None,"iterations":iterations,
            "cyclic_allocation_site_count":cyclic_allocation_count,
            "field_receivers":receiver_facts,
            "invoke_arguments":invoke_argument_facts,
            "invoke_argument_count":len(invoke_argument_facts),
            "return_values":return_values,
            "return_value_count":len(return_values),
            "instruction_writes":[{"instruction":x["index"],"registers":x["writes"]} for x in executable],
            "invoke_argument_incomplete_count":sum(not x["mapping_complete"] for x in invoke_argument_facts),
            "same_instance_groups":same_instance_groups,
            "singleton_receiver_count":sum(x["identity_status"]=="singleton" for x in receiver_facts),
            "unknown_receiver_count":sum(x["identity_status"]=="unknown" for x in receiver_facts),
            "unresolved_receiver_count":sum(x["identity_status"]=="unresolved" for x in receiver_facts),
            "multiple_receiver_count":sum(x["identity_status"]=="multiple" for x in receiver_facts)}


def build_interprocedural_value_graph(methods):
    """Link caller definitions to callee parameters and callee returns to move-result defs.

    Exact owner/name/descriptor matching is required. This emits evidence edges only;
    it does not grant Hook authorization or infer object identity for field accesses.
    """
    by_signature=collections.defaultdict(list)
    for method in methods:
        key=method["class"]+"->"+method["name"]+method["descriptor"]
        method["_semantic_key"]=key
        by_signature[key].append(method)
    edges=[]; unresolved_calls=0; ambiguous_calls=0; resolved_calls=0
    argument_edges=0; return_edges=0; unresolved_arguments=0; unresolved_returns=0
    incomplete_dataflow_calls=0; truncated_callsite_methods=0
    total_edge_count=0
    def append_edge(edge):
        nonlocal total_edge_count
        total_edge_count+=1
        if len(edges)<MAX_INTERPROCEDURAL_VALUE_EDGES:
            edges.append(edge)
    for caller in methods:
        caller_key=caller["_semantic_key"]
        caller_flow=caller.get("register_dataflow",{})
        uses={(item["instruction"],item["register"]):item
              for item in caller_flow.get("uses",[])}
        if caller.get("invoke_sites_truncated"):
            truncated_callsite_methods+=1
            continue
        if caller.get("invoke_sites_incomplete"):
            truncated_callsite_methods+=1
            continue
        for site in caller.get("invoke_sites",[]):
            target=site["owner"]+"->"+site["name"]+site["descriptor"]
            choices=by_signature.get(target,[])
            same_component=[m for m in choices if m.get("component")==caller.get("component")]
            if len(same_component)==1: callee=same_component[0]
            elif len(choices)==1: callee=choices[0]
            elif len(choices)>1:
                ambiguous_calls+=1
                continue
            else:
                unresolved_calls+=1
                continue
            resolved_calls+=1
            callee_flow=callee.get("register_dataflow",{})
            if not caller_flow.get("complete") or not callee_flow.get("complete"):
                incomplete_dataflow_calls+=1
                unresolved_arguments+=len(site.get("registers",[]))
                if site.get("result_register"): unresolved_returns+=1
                continue
            parsed=parse_method_descriptor(site["descriptor"])
            if not parsed:
                unresolved_arguments+=1
                continue
            actual=list(site["registers"])
            is_static=site["opcode"].startswith("invoke-static")
            formal_word=0; actual_word=0; mapping=[]
            if not is_static:
                mapping.append((actual[actual_word] if actual_word<len(actual) else None,
                                "p0","receiver"))
                actual_word+=1; formal_word=1
            for parameter_index,param_type in enumerate(parsed["parameters"]):
                width=2 if param_type in ("J","D") else 1
                for word_index in range(width):
                    actual_reg=actual[actual_word] if actual_word<len(actual) else None
                    formal_reg="p{}".format(formal_word+word_index)
                    mapping.append((actual_reg,formal_reg,"argument"))
                    actual_word+=1
                formal_word+=width
            arguments_aligned=actual_word==len(actual)
            if not arguments_aligned:
                unresolved_arguments+=1
            callee_defs={d["register"]:d["id"] for d in callee.get("register_dataflow",{}).get("definitions",[])
                         if d.get("kind")=="parameter"}
            if arguments_aligned:
                for actual_reg,formal_reg,kind in mapping:
                    if not actual_reg:
                        unresolved_arguments+=1
                        continue
                    formal_id=callee_defs.get(formal_reg)
                    use=uses.get((site["instruction"],actual_reg))
                    reaching=use.get("reaching_definitions",[]) if use else []
                    if not formal_id or not reaching:
                        unresolved_arguments+=1
                        continue
                    for source_id in reaching:
                        append_edge({"kind":"argument","from_method":caller_key,
                                      "from_definition":source_id,"to_method":callee["_semantic_key"],
                                      "to_parameter":formal_id,"actual_register":actual_reg,
                                      "formal_register":formal_reg,"call_instruction":site["instruction"],
                                      "call_line":site["line"],"argument_kind":kind,
                                      "component":caller.get("component")})
                        argument_edges+=1
            if site.get("result_instruction") is not None and site.get("result_register"):
                caller_result_id="d{}:{}".format(site["result_instruction"],site["result_register"])
                return_uses=[u for u in callee.get("register_dataflow",{}).get("uses",[])
                             if u.get("opcode","").startswith("return") and u.get("reaching_definitions")]
                if not return_uses:
                    unresolved_returns+=1
                for return_use in return_uses:
                    for source_id in return_use["reaching_definitions"]:
                        append_edge({"kind":"return","from_method":callee["_semantic_key"],
                                      "from_definition":source_id,"to_method":caller_key,
                                      "to_definition":caller_result_id,
                                      "call_instruction":site["instruction"],
                                      "result_instruction":site["result_instruction"],
                                      "result_register":site["result_register"],
                                      "component":caller.get("component")})
                        return_edges+=1
    for method in methods:
        method.pop("_semantic_key",None)
    return {"edges":edges,"summary":{"resolved_call_sites":resolved_calls,
            "unresolved_call_sites":unresolved_calls,"ambiguous_call_sites":ambiguous_calls,
            "argument_edges":argument_edges,"return_edges":return_edges,
            "unresolved_argument_mappings":unresolved_arguments,
            "unresolved_return_mappings":unresolved_returns,
            "incomplete_dataflow_call_sites":incomplete_dataflow_calls,
            "truncated_callsite_methods":truncated_callsite_methods,
            "edge_count":total_edge_count,"stored_edge_count":len(edges),
            "edges_truncated":total_edge_count>MAX_INTERPROCEDURAL_VALUE_EDGES}}


def build_interprocedural_points_to_graph(methods, max_call_depth=4, max_records=200000, root_scope="all"):
    """Build bounded call-string contexts for receiver and direct return identity projection.

    Return values are propagated only across straight-line caller methods, and only
    when the callee's every object-return site resolves to the same known identity.
    This remains a bounded diagnostic abstraction, not a whole-program fixed point.
    """
    by_signature=collections.defaultdict(list)
    for method in methods:
        key=method["class"]+"->"+method["name"]+method["descriptor"]
        method["_points_to_key"]=key
        by_signature[key].append(method)
    eligible_roots=[m for m in methods if m.get("object_points_to",{}).get("complete")
                    and not m.get("invoke_sites_truncated") and not m.get("invoke_sites_incomplete")]
    if root_scope not in ("all","semantic-candidates"):
        raise ValueError("root_scope must be 'all' or 'semantic-candidates'")
    roots=(eligible_roots if root_scope=="all"
           else [m for m in eligible_roots if m.get("roles")])
    queue=collections.deque()
    for root in roots:
        queue.append({
            "method":root,"context_id":"root:"+root["_points_to_key"],
            "root_method_key":root["_points_to_key"],
            "bindings":{},"register_overrides":{},
            "path":(root["_points_to_key"],),"depth":0
        })
    call_contexts=[]
    contextual_receivers=[]
    resolved=unresolved=ambiguous=incomplete=0
    singleton_context_receivers=0
    return_propagations=return_unknowns=return_unresolved=0
    recursive_contexts_cut=depth_contexts_cut=0
    records_truncated=False
    if max_records < 1:
        raise ValueError("max_records must be positive")
    record_limit=max_records
    # Partition the aggregate storage budget across roots so one hot root cannot consume
    # every other root's evidence allowance. Keep at least one slot per root when
    # the requested budget is smaller than the root count.
    per_root_record_limit=max(1,record_limit//max(1,len(roots)))
    roots_with_roles=sum(bool(m.get("roles")) for m in roots)
    queue_states_enqueued=len(queue)
    queue_states_processed=0
    duplicate_context_states_skipped=0
    call_context_records_dropped=0
    receiver_records_dropped=0
    seen_contexts=set()
    root_diagnostics={
        root["_points_to_key"]:{
            "call_contexts_seen":0,"call_contexts_stored":0,
            "call_contexts_dropped":0,"receiver_records_seen":0,
            "receiver_records_stored":0,"receiver_records_dropped":0,
            "queue_states_processed":0,"recursive_cuts":0,"depth_cuts":0,
            "unresolved_call_sites":0,"ambiguous_call_sites":0,
            "incomplete_call_sites":0,"return_summary_recursive_cuts":0,
            "return_summary_depth_cuts":0,"return_identity_unknown_count":0,
            "return_identity_unresolved_count":0
        } for root in roots
    }

    def substitute(identity,method_key,bindings,context_id,contextualize_allocations=True):
        formal_prefix="param:{}:".format(method_key)
        if identity.startswith(formal_prefix):
            formal=identity[len(formal_prefix):]
            actual=bindings.get(formal)
            if not actual or actual.get("unknown"):
                return [],True
            return list(actual.get("points_to",[])),False
        allocation_prefix="alloc:{}#".format(method_key)
        if identity.startswith(allocation_prefix):
            if contextualize_allocations:
                return ["context:{}:{}".format(context_id,identity)],False
            return [identity],False
        return [identity],False

    return_summary_recursive_cuts=0
    return_summary_depth_cuts=0
    return_summary_compositions=0

    def resolve_contextual_return(method, context_id, bindings, path, depth, expand=True):
        """Resolve a method's object return through bounded nested call contexts."""
        nonlocal return_summary_recursive_cuts, return_summary_depth_cuts
        nonlocal return_summary_compositions
        pts=method.get("object_points_to",{})
        parsed_method=parse_method_descriptor(method.get("descriptor",""))
        if (not pts.get("complete") or not parsed_method
                or not parsed_method["return_type"].startswith(("L","["))):
            return {"points_to":[],"unknown":True,"identity_status":"unknown"}
        key=method["_points_to_key"]
        cfg=method.get("control_flow",{}).get("cfg",{})
        linear_safe=(method.get("control_flow",{}).get("branch_count")==0
            and cfg.get("complete") is True
            and not any(edge.get("kind")=="exception" for edge in cfg.get("edges",[])))
        overrides={}
        args_by_instruction=collections.defaultdict(list)
        for item in pts.get("invoke_arguments",[]):
            args_by_instruction[item.get("call_instruction")].append(item)
        writes_by_register=collections.defaultdict(list)
        for write in pts.get("instruction_writes",[]):
            for register in write.get("registers",[]):
                writes_by_register[register].append(write["instruction"])

        if expand and linear_safe:
            for nested_site in sorted(method.get("invoke_sites",[]),key=lambda x:x["instruction"]):
                nested_parsed=parse_method_descriptor(nested_site.get("descriptor",""))
                if (not nested_parsed or not nested_parsed["return_type"].startswith(("L","["))
                        or not nested_site.get("result_register")
                        or nested_site.get("result_instruction") is None):
                    continue
                target=(nested_site["owner"]+"->"+nested_site["name"]+
                        nested_site["descriptor"])
                choices=by_signature.get(target,[])
                same_component=[m for m in choices if m.get("component")==method.get("component")]
                if len(same_component)==1:
                    nested_callee=same_component[0]
                elif len(choices)==1:
                    nested_callee=choices[0]
                else:
                    continue
                nested_key=nested_callee["_points_to_key"]
                nested_context="{}=>{}@{}".format(context_id,key,nested_site["instruction"])
                nested_bindings={}
                nested_actuals=args_by_instruction.get(nested_site["instruction"],[])
                if any(not x.get("mapping_complete") for x in nested_actuals):
                    continue
                for item in nested_actuals:
                    reg=item.get("actual_register")
                    override=overrides.get(reg) if reg else None
                    override_valid=False
                    if override and nested_site["instruction"]>override["definition_instruction"]:
                        writes=[x for x in writes_by_register.get(reg,[])
                                if override["definition_instruction"]<x<nested_site["instruction"]]
                        override_valid=not writes
                    if override_valid:
                        ids=list(override["points_to"])
                        unknown=bool(override["unknown"])
                    else:
                        ids=[]; unknown=bool(item.get("unknown"))
                        for identity in item.get("points_to",[]):
                            projected,was_unknown=substitute(
                                identity,key,bindings,context_id,
                                contextualize_allocations=depth>0)
                            ids.extend(projected); unknown=unknown or was_unknown
                    nested_bindings[item["formal_register"]]={
                        "points_to":sorted(set(ids)),"unknown":unknown
                    }
                if nested_key in path:
                    return_summary_recursive_cuts+=1
                    nested_result={"points_to":[],"unknown":True,"identity_status":"unknown"}
                elif depth+1>=max_call_depth:
                    if nested_callee.get("invoke_sites"):
                        return_summary_depth_cuts+=1
                    nested_result=resolve_contextual_return(
                        nested_callee,nested_context,nested_bindings,
                        path+(key,),depth+1,expand=False)
                else:
                    nested_result=resolve_contextual_return(
                        nested_callee,nested_context,nested_bindings,
                        path+(key,),depth+1,expand=True)
                if nested_result["identity_status"]=="singleton":
                    overrides[nested_site["result_register"]]={
                        "definition_instruction":nested_site["result_instruction"],
                        "points_to":nested_result["points_to"],"unknown":False
                    }
                    return_summary_compositions+=1

        expected=method.get("control_flow",{}).get("return_count",0)
        return_facts=pts.get("return_values",[])
        if expected<=0 or len(return_facts)!=expected:
            return {"points_to":[],"unknown":True,"identity_status":"unknown"}
        returned=set()
        has_unknown=False
        for fact in return_facts:
            reg=fact.get("register")
            override=overrides.get(reg) if reg else None
            override_valid=False
            if override and fact.get("instruction",-1)>override["definition_instruction"]:
                writes=[x for x in writes_by_register.get(reg,[])
                        if override["definition_instruction"]<x<fact["instruction"]]
                override_valid=not writes
            if override_valid:
                returned.update(override["points_to"])
                has_unknown=has_unknown or bool(override["unknown"])
            else:
                has_unknown=has_unknown or bool(fact.get("unknown"))
                for identity in fact.get("points_to",[]):
                    projected,unknown=substitute(
                        identity,key,bindings,context_id,
                        contextualize_allocations=depth>0)
                    returned.update(projected)
                    has_unknown=has_unknown or unknown
        values=sorted(returned)
        status=("unknown" if has_unknown else
                "singleton" if len(values)==1 else
                "multiple" if len(values)>1 else "unresolved")
        return {"points_to":values,"unknown":has_unknown,"identity_status":status}

    while queue:
        state=queue.popleft()
        queue_states_processed+=1
        caller=state["method"]
        caller_key=caller["_points_to_key"]
        root_method_key=state["root_method_key"]
        root_stats=root_diagnostics[root_method_key]
        root_stats["queue_states_processed"]+=1
        caller_pts=caller.get("object_points_to",{})
        if (not caller_pts.get("complete") or caller.get("invoke_sites_truncated")
                or caller.get("invoke_sites_incomplete")):
            incomplete+=len(caller.get("invoke_sites",[])) or 1
            root_stats["incomplete_call_sites"]+=len(caller.get("invoke_sites",[])) or 1
            continue
        args_by_instruction=collections.defaultdict(list)
        for item in caller_pts.get("invoke_arguments",[]):
            args_by_instruction[item.get("call_instruction")].append(item)
        writes_by_register=collections.defaultdict(list)
        for write in caller_pts.get("instruction_writes",[]):
            for register in write.get("registers",[]):
                writes_by_register[register].append(write["instruction"])
        cfg=caller.get("control_flow",{}).get("cfg",{})
        linear_return_safe=(caller.get("control_flow",{}).get("branch_count")==0
            and cfg.get("complete") is True
            and not any(edge.get("kind")=="exception" for edge in cfg.get("edges",[])))
        register_overrides=dict(state.get("register_overrides",{}))
        for site in sorted(caller.get("invoke_sites",[]),key=lambda x:x["instruction"]):
            target=site["owner"]+"->"+site["name"]+site["descriptor"]
            choices=by_signature.get(target,[])
            same_component=[m for m in choices if m.get("component")==caller.get("component")]
            if len(same_component)==1:
                callee=same_component[0]
            elif len(choices)==1:
                callee=choices[0]
            elif len(choices)>1:
                ambiguous+=1
                root_stats["ambiguous_call_sites"]+=1
                continue
            else:
                unresolved+=1
                root_stats["unresolved_call_sites"]+=1
                continue
            callee_key=callee["_points_to_key"]
            callee_pts=callee.get("object_points_to",{})
            if not callee_pts.get("complete"):
                incomplete+=1
                root_stats["incomplete_call_sites"]+=1
                continue
            actuals=args_by_instruction.get(site["instruction"],[])
            if any(not x.get("mapping_complete") for x in actuals):
                incomplete+=1
                root_stats["incomplete_call_sites"]+=1
                continue
            context_id="{}=>{}@{}".format(
                state["context_id"],caller_key,site["instruction"])
            resolved_bindings={}
            for item in actuals:
                identities=[]
                has_unknown=bool(item.get("unknown"))
                actual_reg=item.get("actual_register")
                override=register_overrides.get(actual_reg) if actual_reg else None
                override_valid=False
                if override and linear_return_safe and site["instruction"]>override["definition_instruction"]:
                    writes=[x for x in writes_by_register.get(actual_reg,[])
                            if override["definition_instruction"]<x<site["instruction"]]
                    override_valid=not writes
                if override_valid:
                    identities=list(override["points_to"])
                    has_unknown=bool(override["unknown"])
                else:
                    for identity in item.get("points_to",[]):
                        projected,unknown=substitute(
                            identity,caller_key,state["bindings"],state["context_id"],
                            contextualize_allocations=state["depth"]>0)
                        identities.extend(projected)
                        has_unknown=has_unknown or unknown
                resolved_bindings[item["formal_register"]]={
                    "points_to":sorted(set(identities)),"unknown":has_unknown
                }

            return_summary={"points_to":[],"unknown":True,"identity_status":"unknown"}
            parsed_target=parse_method_descriptor(site.get("descriptor",""))
            is_object_return=(parsed_target is not None and
                parsed_target["return_type"].startswith(("L","[")))
            if (is_object_return and site.get("result_register")
                    and site.get("result_instruction") is not None):
                recursive_cuts_before=return_summary_recursive_cuts
                depth_cuts_before=return_summary_depth_cuts
                return_summary=resolve_contextual_return(
                    callee,context_id,resolved_bindings,
                    state["path"]+(caller_key,callee_key),state["depth"]+1,expand=True)
                root_stats["return_summary_recursive_cuts"]+=(
                    return_summary_recursive_cuts-recursive_cuts_before)
                root_stats["return_summary_depth_cuts"]+=(
                    return_summary_depth_cuts-depth_cuts_before)
                if return_summary["identity_status"]=="singleton" and linear_return_safe:
                    register_overrides[site["result_register"]]={
                        "definition_instruction":site["result_instruction"],
                        "points_to":return_summary["points_to"],"unknown":False
                    }
                    return_propagations+=1
                elif return_summary["identity_status"]=="unknown":
                    return_unknowns+=1
                    root_stats["return_identity_unknown_count"]+=1
                else:
                    return_unresolved+=1
                    root_stats["return_identity_unresolved_count"]+=1

            root_stats["call_contexts_seen"]+=1
            if root_stats["call_contexts_stored"]<per_root_record_limit:
                root_stats["call_contexts_stored"]+=1
                call_contexts.append({
                    "root_method_key":root_method_key,
                    "context_id":context_id,"caller":caller_key,"callee":callee_key,
                    "call_instruction":site["instruction"],"call_line":site["line"],
                    "call_depth":state["depth"]+1,
                    "arguments":[{
                        "formal_register":x["formal_register"],
                        "actual_register":x["actual_register"],
                        "argument_kind":x["argument_kind"],
                        "points_to":resolved_bindings[x["formal_register"]]["points_to"],
                        "unknown":resolved_bindings[x["formal_register"]]["unknown"],
                        "identity_status":("unknown" if resolved_bindings[x["formal_register"]]["unknown"]
                            else "singleton" if len(resolved_bindings[x["formal_register"]]["points_to"])==1
                            else "multiple" if len(resolved_bindings[x["formal_register"]]["points_to"])>1
                            else "unresolved")
                    } for x in actuals],
                    "return_value":{
                        "register":site.get("result_register"),
                        "identity_status":return_summary["identity_status"],
                        "points_to":return_summary["points_to"],
                        "unknown":return_summary["unknown"]
                    }
                })
            else:
                records_truncated=True
                call_context_records_dropped+=1
                root_stats["call_contexts_dropped"]+=1
            # Storage truncation is diagnostic only: continue traversing this call so
            # descendants and independent roots are still analyzed.
            resolved+=1
            for fact in callee_pts.get("field_receivers",[]):
                identities=[]
                has_unknown=bool(fact.get("unknown"))
                for identity in fact.get("points_to",[]):
                    projected,unknown=substitute(
                        identity,callee_key,resolved_bindings,context_id)
                    identities.extend(projected)
                    has_unknown=has_unknown or unknown
                identities=sorted(set(identities))
                status=("unknown" if has_unknown else
                        "singleton" if len(identities)==1 else
                        "multiple" if len(identities)>1 else "unresolved")
                root_stats["receiver_records_seen"]+=1
                if root_stats["receiver_records_stored"]<per_root_record_limit:
                    root_stats["receiver_records_stored"]+=1
                    contextual_receivers.append({
                        "root_method_key":root_method_key,
                        "context_id":context_id,"caller":caller_key,"callee":callee_key,
                        "call_instruction":site["instruction"],
                        "call_depth":state["depth"]+1,
                        "receiver_instruction":fact.get("instruction"),
                        "field":fact.get("field"),"access":fact.get("access"),
                        "points_to":identities,"unknown":has_unknown,
                        "identity_status":status,
                        "identity":identities[0] if status=="singleton" else None,
                        "identity_scope":"bounded-call-string-context",
                        "runtime_identity_proven":False
                    })
                else:
                    records_truncated=True
                    receiver_records_dropped+=1
                    root_stats["receiver_records_dropped"]+=1
                if status=="singleton":
                    singleton_context_receivers+=1
            if callee_key in state["path"]:
                recursive_contexts_cut+=1
                root_stats["recursive_cuts"]+=1
                continue
            if state["depth"]+1>=max_call_depth:
                if callee.get("invoke_sites"):
                    depth_contexts_cut+=1
                    root_stats["depth_cuts"]+=1
                continue
            next_state_id=(callee_key,context_id)
            if next_state_id in seen_contexts:
                duplicate_context_states_skipped+=1
                continue
            seen_contexts.add(next_state_id)
            queue_states_enqueued+=1
            queue.append({
                "method":callee,"context_id":context_id,
                "root_method_key":root_method_key,
                "bindings":resolved_bindings,"register_overrides":{},
                "path":state["path"]+(callee_key,),
                "depth":state["depth"]+1
            })
        # A returned object may be used directly as a field receiver in the caller,
        # not only forwarded as an argument to another invoke.
        for fact in caller_pts.get("field_receivers",[]):
            register=fact.get("receiver_register")
            override=register_overrides.get(register) if register else None
            if not override or not linear_return_safe:
                continue
            definition=override["definition_instruction"]
            instruction=fact.get("instruction",-1)
            if instruction<=definition:
                continue
            if any(definition<x<instruction for x in writes_by_register.get(register,[])):
                continue
            identities=sorted(set(override["points_to"]))
            unknown=bool(override["unknown"])
            status=("unknown" if unknown else
                    "singleton" if len(identities)==1 else
                    "multiple" if len(identities)>1 else "unresolved")
            root_stats["receiver_records_seen"]+=1
            if root_stats["receiver_records_stored"]<per_root_record_limit:
                root_stats["receiver_records_stored"]+=1
                contextual_receivers.append({
                    "root_method_key":root_method_key,
                    "context_id":state["context_id"],"caller":caller_key,"callee":caller_key,
                    "call_instruction":None,"receiver_instruction":instruction,
                    "receiver_register":register,"field":fact.get("field"),
                    "access":fact.get("access"),"points_to":identities,"unknown":unknown,
                    "identity_status":status,
                    "identity":identities[0] if status=="singleton" else None,
                    "identity_scope":"bounded-call-string-context",
                    "runtime_identity_proven":False
                })
            else:
                records_truncated=True
                receiver_records_dropped+=1
                root_stats["receiver_records_dropped"]+=1
            if status=="singleton":
                singleton_context_receivers+=1
    root_rows=[]
    for root_key,stats in root_diagnostics.items():
        root_incomplete=(
            stats["call_contexts_dropped"]>0
            or stats["receiver_records_dropped"]>0
            or stats["recursive_cuts"]>0
            or stats["depth_cuts"]>0
            or stats["return_summary_recursive_cuts"]>0
            or stats["return_summary_depth_cuts"]>0
            or stats["unresolved_call_sites"]>0
            or stats["ambiguous_call_sites"]>0
            or stats["incomplete_call_sites"]>0
        )
        root_rows.append({
            "root_method_key":root_key,**stats,
            "context_expansion_complete":not root_incomplete
        })
    root_rows.sort(
        key=lambda row:(
            row["call_contexts_seen"]+row["receiver_records_seen"],
            row["queue_states_processed"],row["root_method_key"]
        ),reverse=True)
    root_summary={
        "root_count":len(root_rows),
        "roots_with_truncation":sum(
            row["call_contexts_dropped"]>0 or row["receiver_records_dropped"]>0
            for row in root_rows),
        "roots_with_recursive_cuts":sum(row["recursive_cuts"]>0 for row in root_rows),
        "roots_with_depth_cuts":sum(row["depth_cuts"]>0 for row in root_rows),
        "roots_with_return_summary_cuts":sum(
            row["return_summary_recursive_cuts"]>0 or row["return_summary_depth_cuts"]>0
            for row in root_rows),
        "roots_with_unresolved_calls":sum(
            row["unresolved_call_sites"]>0 for row in root_rows),
        "roots_with_ambiguous_calls":sum(
            row["ambiguous_call_sites"]>0 for row in root_rows),
        "roots_with_incomplete_calls":sum(
            row["incomplete_call_sites"]>0 for row in root_rows),
        "roots_marked_incomplete":sum(not row["context_expansion_complete"] for row in root_rows),
        "top_hot_roots":root_rows[:20]
    }
    for method in methods:
        method.pop("_points_to_key",None)
    return {
        "call_contexts":call_contexts,
        "contextual_receivers":contextual_receivers,
        "summary":{
            "resolved_call_contexts":resolved,"unresolved_call_sites":unresolved,
            "ambiguous_call_sites":ambiguous,"incomplete_call_sites":incomplete,
            "contextual_receiver_count":len(contextual_receivers),
            "singleton_context_receiver_count":singleton_context_receivers,
            "return_identity_propagations":return_propagations,
            "return_identity_unknown_count":return_unknowns,
            "return_identity_unresolved_count":return_unresolved,
            "return_summary_compositions":return_summary_compositions,
            "return_summary_recursive_cuts":return_summary_recursive_cuts,
            "return_summary_depth_cuts":return_summary_depth_cuts,
            "records_truncated":records_truncated,
            "record_limit":record_limit,
            "per_root_record_limit":per_root_record_limit,
            "record_budget_policy":"fair-share-per-root; storage truncation never stops graph traversal",
            "analysis_scope":("whole-program-eligible-method-roots" if root_scope=="all"
                else "semantic-role-roots-only"),
            "scope_is_whole_program":root_scope=="all",
            "eligible_root_method_count":len(eligible_roots),
            "root_method_count":len(roots),
            "semantic_candidate_root_count":roots_with_roles,
            "queue_states_enqueued":queue_states_enqueued,
            "queue_states_processed":queue_states_processed,
            "unique_context_states":len(seen_contexts),
            "duplicate_context_states_skipped":duplicate_context_states_skipped,
            "call_context_records_dropped":call_context_records_dropped,
            "receiver_records_dropped":receiver_records_dropped,
            "max_call_depth":max_call_depth,
            "recursive_contexts_cut":recursive_contexts_cut,
            "depth_contexts_cut":depth_contexts_cut,
            "context_expansion_complete":(not records_truncated and recursive_contexts_cut==0
                and depth_contexts_cut==0 and return_summary_recursive_cuts==0
                and return_summary_depth_cuts==0 and unresolved==0
                and ambiguous==0 and incomplete==0),
            "root_diagnostics":root_summary,
            "recursive_fixed_point":False,"runtime_identity_proven":False
        }
    }

def build_field_slot_index(methods):
    """Group field reads/writes by exact DEX field descriptor, without claiming object identity."""
    groups=collections.defaultdict(lambda:{"field":"","writers":[],"readers":[]})
    for method in methods:
        key=method["class"]+"->"+method["name"]+method["descriptor"]
        for access in method.get("field_access_sites",[]):
            group=groups[access["field"]]
            group["field"]=access["field"]
            event={"method":key,"component":method.get("component"),
                   "instruction":access["instruction"],"line":access["line"],
                   "opcode":access["opcode"],"value_register":access["value_register"],
                   "object_register":access.get("object_register"),
                   "static":access["static"]}
            group["readers" if access["access"]=="read" else "writers"].append(event)
    records=[]
    for field in sorted(groups):
        group=groups[field]
        if group["writers"] and group["readers"]:
            writer_methods={writer["method"] for writer in group["writers"]}
            reader_methods={reader["method"] for reader in group["readers"]}
            group["cross_method_pair_count"]=(
                len(writer_methods)*len(reader_methods)-len(writer_methods & reader_methods))
            group["instance_identity_confirmed"]=False
            records.append(group)
    return records


def analyze_smali(root):
    classes=[]; methods=[]; call_edges=[]
    for file in sorted(root.rglob("*.smali")):
        try: lines=file.read_text(errors="replace").splitlines()
        except OSError: continue
        desc=super_desc=None; interfaces=[]; current=None; in_method=False
        for line_no,line in enumerate(lines,1):
            if not in_method:
                m=CLASS_RE.match(line)
                if m: desc=m.group(1)
                m=SUPER_RE.match(line)
                if m: super_desc=m.group(1)
                m=IMPL_RE.match(line)
                if m: interfaces.append(m.group(1))
                if line.startswith(".method "):
                    m=METHOD_RE.match(line)
                    if m:
                        current={"class":desc or "", "name":m.group(2), "descriptor":m.group(3),
                                 "access":m.group(1), "file":str(file.relative_to(root)),
                                 "line":line_no, "strings":[], "invokes":[], "invoke_sites":[],
                                 "parameter_registers":parameter_registers_for_method(m.group(1),m.group(3)),
                                 "field_access_sites":[], "opcodes":collections.Counter(),
                                 "field_reads":[], "field_writes":[], "branch_count":0, "label_count":0,
                                 "return_count":0, "throw_count":0, "body_lines":[]}
                        in_method=True
                continue
            if line.startswith(".end method"):
                if current:
                    blob=" ".join(current["strings"])+" "+" ".join(current["invokes"])
                    roles=[]
                    for role,terms in ANCHORS.items():
                        hits=[t for t in terms if t in blob]
                        if hits: roles.append({"role":role,"anchors":hits[:20]})
                    current["roles"]=roles
                    current["opcode_count"]=sum(current["opcodes"].values())
                    current["opcode_histogram"]=dict(current["opcodes"].most_common(24))
                    current["field_reads"]=sorted(set(current["field_reads"]))[:120]
                    current["field_writes"]=sorted(set(current["field_writes"]))[:120]
                    cfg=build_smali_cfg(current["body_lines"])
                    current["register_flow"]=analyze_register_use_def(current["body_lines"])
                    current["control_flow"]={"branch_count":current["branch_count"],"label_count":current["label_count"],
                        "return_count":current["return_count"],"throw_count":current["throw_count"],
                        "basic_block_estimate":cfg["block_count"],"cfg":cfg}
                    current["register_dataflow"]=analyze_register_dataflow(
                        current["body_lines"],cfg,current["parameter_registers"])
                    invoke_sites=extract_invoke_sites(current["body_lines"])
                    invoke_opcode_count=sum(1 for body_line in current["body_lines"]
                        if (OP_RE.match(body_line) and OP_RE.match(body_line).group(1).startswith("invoke-")))
                    current["invoke_sites"]=invoke_sites[:512]
                    current["invoke_sites_truncated"]=len(invoke_sites)>512
                    current["invoke_sites_incomplete"]=len(invoke_sites)!=invoke_opcode_count
                    field_sites=extract_field_access_sites(current["body_lines"])
                    field_opcode_count=sum(1 for body_line in current["body_lines"]
                        if (OP_RE.match(body_line) and OP_RE.match(body_line).group(1).startswith(("iget","iput","sget","sput"))))
                    current["field_access_sites"]=field_sites[:512]
                    current["field_access_sites_truncated"]=len(field_sites)>512
                    current["field_access_sites_incomplete"]=len(field_sites)!=field_opcode_count
                    current["object_points_to"]=analyze_object_points_to(
                        current["body_lines"],cfg,current["class"],current["name"],
                        current["descriptor"],current["access"],current.get("field_access_sites",[]),
                        current.get("invoke_sites",[]))
                    receiver_by_instruction={x["instruction"]:x for x in
                        current["object_points_to"].get("field_receivers",[])}
                    for field_site in current.get("field_access_sites",[]):
                        receiver=receiver_by_instruction.get(field_site["instruction"])
                        if receiver:
                            field_site["receiver_identity_status"]=receiver["identity_status"]
                            field_site["receiver_identity"]=receiver["identity"]
                    current["invokes"]=sorted(set(current["invokes"]))[:120]
                    current["strings"]=sorted(set(current["strings"]))[:100]
                    current.pop("body_lines",None)
                    methods.append(current)
                    for target,name,sig in current.pop("_edges",[]):
                        call_edges.append({"from":current["class"]+"->"+current["name"]+current["descriptor"],
                                           "to":target+"->"+name+sig})
                current=None; in_method=False
                continue
            if current is None: continue
            current["body_lines"].append(line)
            sm=safe_strings(line)
            current["strings"].extend(sm)
            im=INVOKE_RE.search(line)
            if im:
                target,name,sig=im.groups()
                current["invokes"].append(target+"->"+name+sig)
                current.setdefault("_edges",[]).append((target,name,sig))
            fa=FIELD_ACCESS_RE.search(line)
            if fa:
                opcode,owner,field_name,field_type=fa.groups()
                field_key=owner+"->"+field_name+":"+field_type
                if opcode.startswith(("iget","sget")): current["field_reads"].append(field_key)
                else: current["field_writes"].append(field_key)
            if BRANCH_RE.match(line): current["branch_count"] += 1
            if LABEL_RE.match(line): current["label_count"] += 1
            stripped=line.strip()
            if stripped.startswith(("return","throw")):
                if stripped.startswith("return"): current["return_count"] += 1
                else: current["throw_count"] += 1
            op=OP_RE.match(line)
            if op and not line.lstrip().startswith((".",":","#")):
                current["opcodes"][op.group(1)] += 1
        if desc:
            classes.append({"descriptor":desc,"super":super_desc,"interfaces":interfaces,
                            "file":str(file.relative_to(root))})
    return classes,methods,call_edges

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True); ap.add_argument("--version",required=True)
    ap.add_argument("--work",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--jadx",required=True); ap.add_argument("--apktool",required=True)
    ap.add_argument("--aapt",required=True); ap.add_argument("--apksigner",required=True)
    a=ap.parse_args()
    src=pathlib.Path(a.input); work=pathlib.Path(a.work); out=pathlib.Path(a.out)
    if work.exists(): shutil.rmtree(work)
    if out.exists(): shutil.rmtree(out)
    work.mkdir(parents=True); out.mkdir(parents=True)
    components=[]
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            names=[n for n in z.namelist() if n.lower().endswith(".apk")]
            if names:
                for i,n in enumerate(names):
                    target=work/f"component-{i}-{pathlib.Path(n).name}"
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(z.read(n)); components.append(target)
            elif src.suffix.lower()==".apk": components=[src]
            else: raise SystemExit("ZIP container has no embedded APK components")
    else: components=[src]
    if not components: raise SystemExit("No APK components discovered")
    inventory=[]; all_classes=[]; all_methods=[]; all_edges=[]; native=[]
    for i,apk in enumerate(components):
        comp=apk.stem
        comp_out=out/comp; comp_out.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(apk) as z:
            dex_entries=[x for x in z.infolist() if re.fullmatch(r"classes[0-9]*\.dex",pathlib.PurePosixPath(x.filename).name)]
            for item in dex_entries:
                raw=z.read(item)
                dh=dex_header(raw) or {"invalid_dex":True}
                inventory.append({"component":apk.name,"entry":item.filename,"sha256":hashlib.sha256(raw).hexdigest(),**dh})
            for item in z.infolist():
                if item.filename.startswith("lib/") and item.filename.endswith(".so"):
                    raw=z.read(item.filename)
                    native.append({"component":apk.name,"path":item.filename,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
        smali=work/f"smali-{i}"
        apktool_rc=run(["java","-jar",a.apktool,"d","-f","-o",str(smali),str(apk)],comp_out/"apktool.log")
        if smali.exists():
            cls,meth,edges=analyze_smali(smali)
            for x in cls: x["component"]=apk.name
            for x in meth: x["component"]=apk.name
            for x in edges: x["component"]=apk.name
            all_classes.extend(cls); all_methods.extend(meth); all_edges.extend(edges)
        manifest={}
        manifest_path=smali/"AndroidManifest.xml"
        if manifest_path.exists():
            try:
                root=ET.parse(manifest_path).getroot()
                android_ns="{http://schemas.android.com/apk/res/android}"
                manifest={"package":root.attrib.get("package"),"split":root.attrib.get("split"),
                          "version_code":root.attrib.get(android_ns+"versionCode") or root.attrib.get("versionCode"),
                          "version_code_major":root.attrib.get(android_ns+"versionCodeMajor") or root.attrib.get("versionCodeMajor"),
                          "version_name":root.attrib.get(android_ns+"versionName") or root.attrib.get("versionName"),
                          "root_attributes":{k:v for k,v in root.attrib.items()}}
            except (ET.ParseError,OSError) as exc:
                manifest={"parse_error":type(exc).__name__,"parse_detail":str(exc)[:240]}
        binary_manifest=aapt_badging(a.aapt,apk,comp_out/"aapt-badging.log")
        for key in ("package","split","version_code","version_name"):
            if binary_manifest.get(key): manifest[key]=binary_manifest[key]
        signing=signing_certificate(a.apksigner,apk,comp_out/"apksigner.log")
        manifest["binary_manifest"]=binary_manifest
        manifest["signing_sha256"]=signing.get("signing_sha256")
        manifest["apksigner_exit"]=signing.get("apksigner_exit")
        jadx_dir=work/f"jadx-{i}"
        jadx_rc=run([a.jadx,"--show-bad-code","--no-res","--threads-count","2","-d",str(jadx_dir),str(apk)],comp_out/"jadx.log")
        java_count=len(list((jadx_dir/"sources").rglob("*.java"))) if (jadx_dir/"sources").exists() else 0
        (comp_out/"component.json").write_text(json.dumps({"apk":apk.name,"bytes":apk.stat().st_size,
             "sha256":sha256(apk),"manifest":manifest,"apktool_exit":apktool_rc,"jadx_exit":jadx_rc,
             "java_files":java_count,"dex_count":len(dex_entries)},indent=2,ensure_ascii=True))
    if not all_classes or not all_methods:
        raise SystemExit(f"No DEX methods recovered from {src.name}; apktool exit status and input package layout require investigation")
    interprocedural=build_interprocedural_value_graph(all_methods)
    interprocedural_points_to=build_interprocedural_points_to_graph(all_methods)
    # A separate candidate-root slice is additive evidence. It must never replace
    # or be merged into the whole-program bounded analysis above.
    interprocedural_points_to_candidates=build_interprocedural_points_to_graph(
        all_methods, root_scope="semantic-candidates")
    field_slot_index=build_field_slot_index(all_methods)
    # Keep the complete method inventory compressed in the repository; no source dump or raw logs are copied.
    write_jsonl_gzip(out/"methods.jsonl.gz", all_methods)
    write_jsonl_gzip(out/"classes.jsonl.gz", all_classes)
    write_jsonl_gzip(out/"call-edges.jsonl.gz", all_edges)
    write_jsonl_gzip(out/"interprocedural-value-edges.jsonl.gz", interprocedural["edges"])
    write_jsonl_gzip(out/"field-slot-index.jsonl.gz", field_slot_index)
    write_jsonl_gzip(out/"interprocedural-points-to.jsonl.gz", interprocedural_points_to["contextual_receivers"])
    write_jsonl_gzip(out/"interprocedural-points-to-candidates.jsonl.gz",
                     interprocedural_points_to_candidates["contextual_receivers"])
    candidates=[]
    for m in all_methods:
        roles=m.get("roles",[])
        if roles:
            score=sum(len(x["anchors"]) for x in roles)
            candidates.append({"class":m["class"],"name":m["name"],"descriptor":m["descriptor"],
                "component":m["component"],"file":m["file"],"line":m["line"],"score":score,"roles":roles,
                "invokes":m["invokes"][:40],"opcode_count":m["opcode_count"]})
    candidates.sort(key=lambda x:(-x["score"],x["class"],x["name"]))
    summary={"version_label":a.version,"source_file":src.name,"source_bytes":src.stat().st_size,
      "source_sha256":sha256(src),"components":[x.name for x in components],"component_metadata":[json.loads((out/x.stem/"component.json").read_text()) for x in components],"dex":inventory,
      "dex_count":len(inventory),"class_count":len(all_classes),"method_count":len(all_methods),
      "call_edge_count":len(all_edges),
      "field_read_count":sum(len(m.get("field_reads",[])) for m in all_methods),
      "field_write_count":sum(len(m.get("field_writes",[])) for m in all_methods),
      "methods_with_control_flow":sum(1 for m in all_methods if m.get("control_flow",{}).get("branch_count",0)>0),
      "control_flow_branch_count":sum(m.get("control_flow",{}).get("branch_count",0) for m in all_methods),
      "methods_with_complete_register_dataflow":sum(1 for m in all_methods if m.get("register_dataflow",{}).get("complete",False)),
      "register_dataflow_definition_count":sum(m.get("register_dataflow",{}).get("definition_count",0) for m in all_methods),
      "register_dataflow_use_count":sum(m.get("register_dataflow",{}).get("use_count",0) for m in all_methods),
      "register_dataflow_ambiguous_use_count":sum(m.get("register_dataflow",{}).get("ambiguous_use_count",0) for m in all_methods),
      "register_dataflow_unresolved_use_count":sum(m.get("register_dataflow",{}).get("unresolved_use_count",0) for m in all_methods),
      "parameter_definition_count":sum(m.get("register_dataflow",{}).get("parameter_definition_count",0) for m in all_methods),
      "invoke_site_count":sum(len(m.get("invoke_sites",[])) for m in all_methods),
      "invoke_site_truncated_methods":sum(1 for m in all_methods if m.get("invoke_sites_truncated")),
      "invoke_site_incomplete_methods":sum(1 for m in all_methods if m.get("invoke_sites_incomplete")),
      "field_access_site_count":sum(len(m.get("field_access_sites",[])) for m in all_methods),
      "field_access_site_truncated_methods":sum(1 for m in all_methods if m.get("field_access_sites_truncated")),
      "field_access_site_incomplete_methods":sum(1 for m in all_methods if m.get("field_access_sites_incomplete")),
      "register_dataflow_evidence_truncated_methods":sum(1 for m in all_methods if m.get("register_dataflow",{}).get("reason")=="evidence-truncated"),
      "field_slot_group_count":len(field_slot_index),
      "field_slot_cross_method_pair_count":sum(x["cross_method_pair_count"] for x in field_slot_index),
      "field_instance_identity_confirmed":False,
      "methods_with_complete_object_points_to":sum(1 for m in all_methods if m.get("object_points_to",{}).get("complete",False)),
      "field_receiver_singleton_count":sum(m.get("object_points_to",{}).get("singleton_receiver_count",0) for m in all_methods),
      "field_receiver_unknown_count":sum(m.get("object_points_to",{}).get("unknown_receiver_count",0) for m in all_methods),
      "field_receiver_unresolved_count":sum(m.get("object_points_to",{}).get("unresolved_receiver_count",0) for m in all_methods),
      "same_instance_field_group_count":sum(len(m.get("object_points_to",{}).get("same_instance_groups",[])) for m in all_methods),
      "cyclic_allocation_site_count":sum(m.get("object_points_to",{}).get("cyclic_allocation_site_count",0) for m in all_methods),
      "field_instance_identity_scope":"intraprocedural-singleton-points-to-per-method-activation",
      "interprocedural_value_flow":interprocedural["summary"],
      "interprocedural_points_to":interprocedural_points_to["summary"],
      "interprocedural_points_to_candidate_scope":interprocedural_points_to_candidates["summary"],
      "candidate_method_count":len(candidates),
      "native_libraries":native,"tool_limits":{"JADX":"best-effort; inspect exit status and APKTool smali evidence",
      "Hook":"static candidate discovery only; no device Hook is claimed"}}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=True))
    (out/"hook-candidates.json").write_text(json.dumps(candidates,indent=2,ensure_ascii=True))
    (out/"candidate-methods.csv").write_text("version,component,class,method,descriptor,score,roles,file,line\n"+"".join(
      ",".join(json.dumps(v,ensure_ascii=True) for v in [a.version,c["component"],c["class"],c["name"],c["descriptor"],c["score"],"|".join(x["role"] for x in c["roles"]),c["file"],c["line"]])+"\n" for c in candidates))
    print(json.dumps({k:summary[k] for k in ("version_label","source_sha256","dex_count","class_count","method_count","call_edge_count","candidate_method_count","component_metadata")},ensure_ascii=True))
if __name__=="__main__": main()
