#!/usr/bin/env python3
"""Repository-only DeepSeek APK audit. Emits compact, privacy-safe evidence indexes."""
from __future__ import annotations
import argparse, collections, gzip, hashlib, json, pathlib, re, shutil, struct, subprocess, zipfile, xml.etree.ElementTree as ET

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
        "complete":not unresolved,"edges":edge_list[:256],"edges_truncated":len(edge_list)>256,
        "blocks_truncated":False}


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
                                 "line":line_no, "strings":[], "invokes":[], "opcodes":collections.Counter(),
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
                    current["control_flow"]={"branch_count":current["branch_count"],"label_count":current["label_count"],
                        "return_count":current["return_count"],"throw_count":current["throw_count"],
                        "basic_block_estimate":cfg["block_count"],"cfg":cfg}
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
    # Keep the complete method inventory compressed in the repository; no source dump or raw logs are copied.
    with gzip.open(out/"methods.jsonl.gz","wt",encoding="utf-8") as f:
        for m in all_methods: f.write(json.dumps(m,separators=(",",":"),ensure_ascii=True)+"\n")
    with gzip.open(out/"classes.jsonl.gz","wt",encoding="utf-8") as f:
        for c in all_classes: f.write(json.dumps(c,separators=(",",":"),ensure_ascii=True)+"\n")
    with gzip.open(out/"call-edges.jsonl.gz","wt",encoding="utf-8") as f:
        for e in all_edges: f.write(json.dumps(e,separators=(",",":"),ensure_ascii=True)+"\n")
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
      "candidate_method_count":len(candidates),
      "native_libraries":native,"tool_limits":{"JADX":"best-effort; inspect exit status and APKTool smali evidence",
      "Hook":"static candidate discovery only; no device Hook is claimed"}}
    (out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=True))
    (out/"hook-candidates.json").write_text(json.dumps(candidates,indent=2,ensure_ascii=True))
    (out/"candidate-methods.csv").write_text("version,component,class,method,descriptor,score,roles,file,line\n"+"".join(
      ",".join(json.dumps(v,ensure_ascii=True) for v in [a.version,c["component"],c["class"],c["name"],c["descriptor"],c["score"],"|".join(x["role"] for x in c["roles"]),c["file"],c["line"]])+"\n" for c in candidates))
    print(json.dumps({k:summary[k] for k in ("version_label","source_sha256","dex_count","class_count","method_count","call_edge_count","candidate_method_count","component_metadata")},ensure_ascii=True))
if __name__=="__main__": main()
