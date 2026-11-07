#!/usr/bin/env python3
"""Aggregate cross-version semantic candidates and privacy-safe probe summaries."""
from __future__ import annotations
import collections, difflib, gzip, json, pathlib, re, zipfile, hashlib

ROOT=pathlib.Path("audit/universal-hook")
VERSIONS=("2.7.1","2.7.2","2.7.3","2.7.4","2.7.5")
def read_json(path): return json.loads(path.read_text())
def read_jsonl_gz(path):
    with gzip.open(path,"rt",encoding="utf-8") as f:
        for line in f:
            if line.strip(): yield json.loads(line)

def version_identity(label, summary):
    """Use the base APK manifest as the version authority; split manifests often omit versionName."""
    components=summary.get("component_metadata",[])
    base=[x for x in components if not x.get("manifest",{}).get("split")]
    if len(base)!=1:
        return {"label":label,"status":"base-component-ambiguous","trusted_for_cross_version":False,
                "base_component_count":len(base)}
    component=base[0]
    manifest=component.get("manifest",{})
    package=manifest.get("package")
    actual=manifest.get("version_name")
    if package!="com.deepseek.chat":
        status="package-mismatch"
    elif not actual:
        status="version-name-missing"
    elif actual!=label:
        status="label-mismatch"
    else:
        status="verified"
    return {"label":label,"status":status,"trusted_for_cross_version":status=="verified",
            "base_component":component.get("apk"),"package":package,
            "manifest_version_name":actual,"version_code":manifest.get("version_code"),
            "apk_sha256":component.get("sha256")}

def project_candidate(method):
    """Keep only fields used by semantic matching; full method records contain large CFG/dataflow payloads."""
    return {key:method.get(key,[]) for key in
            ("class","name","descriptor","roles","invokes","strings","opcode_histogram","opcode_count")}

def prepared_method(method):
    return (method,feature_set(method),method.get("opcode_histogram",{}))

def prepared_similarity(left,right):
    # Role labels partition the search space; they are not discriminative similarity evidence.
    A={item for item in left[1] if not item.startswith("role:")}
    B={item for item in right[1] if not item.startswith("role:")}
    if not A or not B: return 0.0
    j=len(A&B)/len(A|B)
    ah=left[2]; bh=right[2]
    keys=set(ah)|set(bh)
    if keys:
        den=sum(max(ah.get(k,0),bh.get(k,0)) for k in keys) or 1
        op=sum(min(ah.get(k,0),bh.get(k,0)) for k in keys)/den
    else: op=0.0
    return round(0.78*j+0.22*op,4)
def feature_set(m):
    out=set()
    for role in m.get("roles",[]):
        out.add("role:"+role["role"])
        out.update("anchor:"+x for x in role.get("anchors",[]))
    for call in m.get("invokes",[]):
        # Keep stable framework/API namespace and method names; discard obfuscated app owner.
        if call.startswith(("Lkotlin/","Lkotlinx/","Ljava/","Landroid/","Lio/ktor/","Lokhttp3/","Lretrofit2/")):
            out.add("api:"+call)
    for s in m.get("strings",[]):
        if s.startswith("/api/v0/chat/") or s in ("text/event-stream","DeltaCommand","ToolOpenFragment","ToolFindFragment","SearchFragment"):
            out.add("string:"+s)
    return out
def mutual_best_matches(left_candidates, right_candidates, minimum_score=0.48, minimum_margin=0.06):
    """Return conservative one-to-one cross-version matches; ambiguous ties are never emitted."""
    if not left_candidates or not right_candidates:
        return [], {"left_ambiguous": 0, "right_ambiguous": 0, "non_mutual": 0, "below_threshold": 0, "no_shared_semantic_evidence": 0}

    def semantic_score(left, right):
        shared = left[1] & right[1]
        # A shared role label is only a search bucket, not evidence of method identity.
        # Require at least one shared protocol anchor, stable API call, or protocol string.
        if not any(item.startswith(("anchor:", "api:", "string:")) for item in shared):
            return 0.0
        return prepared_similarity(left, right)

    scores = [
        [semantic_score(left, right) for right in right_candidates]
        for left in left_candidates
    ]
    no_shared_semantic_evidence = sum(1 for row in scores if not any(value > 0.0 for value in row))

    def best_and_margin(values):
        ranked = sorted(values, reverse=True)
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else 0.0
        return best, best - second

    left_best = []
    left_ambiguous = 0
    below_threshold = 0
    for row in scores:
        best, margin = best_and_margin(row)
        index = max(range(len(row)), key=row.__getitem__)
        if best < minimum_score:
            below_threshold += 1
            left_best.append(None)
        elif margin < minimum_margin:
            left_ambiguous += 1
            left_best.append(None)
        else:
            left_best.append(index)

    right_best = []
    right_ambiguous = 0
    for column in zip(*scores):
        best, margin = best_and_margin(column)
        index = max(range(len(column)), key=column.__getitem__)
        if best < minimum_score:
            right_best.append(None)
        elif margin < minimum_margin:
            right_ambiguous += 1
            right_best.append(None)
        else:
            right_best.append(index)

    matches = []
    non_mutual = 0
    for left_index, right_index in enumerate(left_best):
        if right_index is None:
            continue
        if right_best[right_index] != left_index:
            non_mutual += 1
            continue
        matches.append((scores[left_index][right_index],
                        left_candidates[left_index][0],
                        right_candidates[right_index][0]))

    matches.sort(key=lambda item: -item[0])
    return matches, {
        "left_ambiguous": left_ambiguous,
        "right_ambiguous": right_ambiguous,
        "non_mutual": non_mutual,
        "below_threshold": below_threshold,
        "no_shared_semantic_evidence": no_shared_semantic_evidence,
    }


def similarity(a,b):
    A=feature_set(a); B=feature_set(b)
    if not A or not B: return 0.0
    j=len(A&B)/len(A|B)
    ah=a.get("opcode_histogram",{}); bh=b.get("opcode_histogram",{})
    keys=set(ah)|set(bh)
    if keys:
        den=sum(max(ah.get(k,0),bh.get(k,0)) for k in keys) or 1
        op=sum(min(ah.get(k,0),bh.get(k,0)) for k in keys)/den
    else: op=0.0
    return round(0.78*j+0.22*op,4)
def probe_summary(repo):
    out={}
    for filename in ("dsprobe.log","deekseep_vision.log"):
        p=repo/filename
        if not p.exists(): continue
        text=p.read_text(errors="replace")
        counts=collections.Counter()
        methods=collections.Counter()
        if filename=="dsprobe.log":
            for line in text.splitlines():
                if "hostGeneration=" in line:
                    m=re.search(r"hostGeneration=([^ ]+)",line)
                    if m: counts["host_generation:"+m.group(1)]+=1
                if "full mode via HostRemap" in line: counts["wrong_full_mode_selection"]+=1
                if "ClassNotFoundException" in line: counts["class_not_found"]+=1
                if "installAllFeatureHooks failed" in line: counts["hook_install_failure"]+=1
                if "installAllFeatureHooks: installing" in line: counts["hook_install_attempt"]+=1
                if "navigation controller capture installed" in line: counts["navigation_capture_installed"]+=1
                if "captured DeepSeek native root" in line: counts["native_root_capture"]+=1
        else:
            for line in text.splitlines():
                if "[OPEN_NATIVE_CALL_OBSERVER]" not in line: continue
                if "installed role=" in line:
                    m=re.search(r"installed role=([^ ]+) method=([^ ]+)",line)
                    if m: counts["observer_role:"+m.group(1)]+=1; methods[m.group(2)]+=1
                if "request-class=" in line: counts["request_class_marker"]+=1
                if "request-constructor-candidate=" in line: counts["request_constructor_candidate"]+=1
                if "request-factory-candidate=" in line: counts["request_factory_candidate"]+=1
                if "session-start" in line: counts["observer_session_start"]+=1
                if "installed" in line: counts["observer_installed_event"]+=1
        out[filename]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                       "line_count":len(text.splitlines()),"event_counts":dict(counts),
                       "top_method_markers":methods.most_common(30)}
    return out
def evidence_zip_summary(repo):
    p=repo/"deepseek-sse-hook-evidence.zip"
    if not p.exists(): return None
    with zipfile.ZipFile(p) as z:
        entries=[{"path":x.filename,"bytes":x.file_size,"sha256":hashlib.sha256(z.read(x)).hexdigest()}
                 for x in z.infolist() if not x.is_dir()]
    return {"file":p.name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "entry_count":len(entries),"entries":entries}
def main():
    root=pathlib.Path("audit")
    summaries={}
    for v in VERSIONS:
        p=root/v/"summary.json"
        if p.exists(): summaries[v]=read_json(p)
    identities={v:version_identity(v,s) for v,s in summaries.items()}
    role_names=("request_route","pow","sse_transport","sse_dispatch","flow_coroutine","serialization",
        "agent_tool","session","prompt_pipeline","agent_planning","tool_registry_execution","local_api_gateway",
        "multimodal_image","multimodal_audio","attachment_file","search_web","storage_sync","account_capability","ui_settings")
    # Stream the large method inventories and retain only compact role candidates.
    # The previous implementation kept every full CFG/reaching-definitions record in RAM.
    candidates={v:collections.defaultdict(list) for v in summaries}
    for v in summaries:
        for method in read_jsonl_gz(root/v/"methods.jsonl.gz"):
            roles=method.get("roles",[])
            if not roles: continue
            compact=project_candidate(method)
            for role_data in roles:
                role=role_data.get("role")
                if role in role_names:
                    candidates[v][role].append(compact)
    pairs=[]
    match_diagnostics=[]
    # Match methods by semantic role, API-family calls, stable protocol anchors and normalized opcode shape.
    for role in role_names:
        by_version={}
        for v in candidates:
            selected=list(candidates[v].get(role,[]))
            selected.sort(key=lambda m: (
                -max((len(x.get("anchors",[])) for x in m.get("roles",[]) if x["role"]==role), default=0),
                -sum(call.startswith(("Lkotlin/","Lkotlinx/","Ljava/","Landroid/","Lio/ktor/","Lokhttp3/","Lretrofit2/")) for call in m.get("invokes",[])),
                -m.get("opcode_count",0),m.get("class",""),m.get("name","")))
            by_version[v]=[prepared_method(m) for m in selected[:160]]
        # A mismatched or absent Manifest version is quarantined from version-to-version matching.
        present=[v for v in by_version if identities[v]["trusted_for_cross_version"] and by_version[v]]
        for i,va in enumerate(present):
            for vb in present[i+1:]:
                matches, diagnostics=mutual_best_matches(by_version[va],by_version[vb])
                match_diagnostics.append({"role":role,"from_version":va,"to_version":vb,**diagnostics,
                                          "accepted_matches":len(matches)})
                for score,a,b in matches:
                    pairs.append({"role":role,"from_version":va,"from":a["class"]+"->"+a["name"]+a["descriptor"],
                      "to_version":vb,"to":b["class"]+"->"+b["name"]+b["descriptor"],
                      "score":score,"confidence":"candidate" if score<0.68 else "strong-candidate",
                      "match_policy":"mutual-best-with-margin"})
    pairs.sort(key=lambda x:(x["role"],x["from_version"],x["from"],-x["score"]))
    report=["# DeepSeek 通用 Hook 跨版本语义审计","",
      "> 本报告由 GitHub Actions 从 apps 仓库内的宿主 APK/APKM、日志和 SSE 证据包生成。静态候选不等于设备 Hook 已成功。","",
      "## APK / DEX 总览","","| 版本标签 | 文件 | 组件数 | DEX 数 | 类数 | 方法数 | 调用边 | 字段读/写 | CFG 分支方法/分支数 | 候选方法数 |",
      "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for v,s in summaries.items():
        report.append(f"| {v} | {s['source_file']} | {len(s['components'])} | {s['dex_count']} | {s['class_count']} | {s['method_count']} | {s.get('call_edge_count',0)} | {s.get('field_read_count',0)}/{s.get('field_write_count',0)} | {s.get('methods_with_control_flow',0)}/{s.get('control_flow_branch_count',0)} | {s['candidate_method_count']} |")
    report += ["","## 版本标签核验","","| 矩阵标签 | Manifest versionName | versionCode | 身份状态 | 是否参与跨版本匹配 |",
      "|---|---|---:|---|---|"]
    for v,identity in identities.items():
        report.append(f"| {v} | {identity.get('manifest_version_name','')} | {identity.get('version_code','')} | {identity['status']} | {'yes' if identity['trusted_for_cross_version'] else 'no'} |")
    report += ["","2.7.3 当前输入的 Manifest versionName=2.5.2，与矩阵标签 2.7.3 冲突；该输入仍保留独立静态索引，但不会参与可信跨版本候选匹配。需要替换正确 APK 或确认该构建的版本标识后再纳入。","",
      "## 组件身份核对","","| 版本 | 组件 | 包名 | versionCode | versionName | split | 签名证书 SHA-256 | 身份完整度 | APK SHA-256 |",
      "|---|---|---|---|---|---|---|---|---|"]
    for v,s in summaries.items():
        for comp in s.get("component_metadata",[]):
            ident=comp.get("manifest",{})
            identity_status = "package+version+signer+hash" if ident.get("version_code") and ident.get("version_name") and ident.get("signing_sha256") else ("package+version+hash" if ident.get("version_code") and ident.get("version_name") else ("package+signer+hash" if ident.get("signing_sha256") else "package+hash (version/signer attrs absent)"))
            report.append(f"| {v} | {comp.get('apk','')} | {ident.get('package','')} | {ident.get('version_code','')} | {ident.get('version_name','')} | {ident.get('split','')} | `{ident.get('signing_sha256','')}` | {identity_status} | `{comp.get('sha256','')}` |")
    report += ["","## 语义候选匹配","","匹配分数由语义锚点、稳定框架/API 调用族和规范化 opcode 分布组成；候选截取前先按锚点数量、稳定 API 调用量和方法体规模排序。仅保留至少共享一个协议锚点、稳定 API 调用或协议字符串，且双向最佳并领先第二名至少 0.06 的匹配；仅角色相同、并列或非互选候选均被拒绝。分数仅用于排序，必须回看源码/Smali 和调用者/被调用者证据。","",
      "| 角色 | 来源版本 | 来源方法 | 目标版本 | 候选方法 | 相似度 |","|---|---|---|---|---|---:|"]
    for x in pairs[:1000]:
        report.append(f"| {x['role']} | {x['from_version']} | `{x['from']}` | {x['to_version']} | `{x['to']}` | {x['score']:.4f} |")
    report += ["","## 动态日志与证据包","","日志只输出计数、类/方法标记和文件哈希，不复制原始用户内容、凭据或请求正文。","",
      "```json",json.dumps(probe_summary(pathlib.Path(".")),indent=2,ensure_ascii=False),"```","",
      "## Hook 设计门槛","","1. 先用包名、versionCode、versionName、APK SHA-256 和 DEX 指纹识别宿主；未知版本进入只读模式。",
      "2. 优先以语义边界定位：请求模型/路由构造、Flow/Continuation 边界、SSE parser、事件分派、会话恢复。",
      "3. 每个候选需同时满足至少三个独立证据族（调用关系、参数/返回类型、继承/接口、稳定 API 调用、协议常量、字节码结构）；字符串重复不算独立证据。",
      "4. 解析完整 JVM 描述符并检查 ClassLoader；禁止仅按混淆类名安装。",
      "5. 候选不唯一、描述符不符、运行时类不可见或版本未知时，fail-closed，不安装该 Hook。",
      "6. 安装按角色幂等；单个可选 Hook 失败不能阻断其他角色，失败记录版本、角色、候选 ID 和异常类型。",
      "7. 先只读观察，再启用请求桥接；不记录 prompt、消息正文、认证头、Cookie、API Key 或 PoW 原始材料。",
      "8. 真机验证覆盖首个 Delta、finish、错误、心跳超时、取消、自动恢复、并发流和重复安装。","",
      "## 已知证据边界","","- 2.7.2 APK 已纳入扫描；先核对 Manifest 包名、versionCode/versionName（若 APK 提供）、DEX 指纹和 APK SHA-256，再与 code289-cn 运行日志交叉验证。若版本属性缺失，只能标记为 package+hash 身份，不能宣称已确认同一构建。",
      "- 2.7.4 输入为 APKM，组件级身份必须以本次解包结果为准。",
      "- 2.7.1 的 APKS/split 历史分析文件属于先前材料，需与当前单文件 deepseek271.apk 的身份核对。",
      "- 2.7.3 / 2.7.5 既有 SSE 链是静态证据；尚未证明真实设备 Hook 成功。",
      "- 服务端 ToolOpen/ToolFind/Search 片段不等于本地工具执行器；需找到本地执行和结果回注闭环。",""]
    outdir=root/"universal-hook"; outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"version-identity.json").write_text(json.dumps(identities,indent=2,ensure_ascii=True))
    (outdir/"universal-hook-report.md").write_text("\n".join(report))
    (outdir/"semantic-method-matches.json").write_text(json.dumps(pairs,indent=2,ensure_ascii=True))
    (outdir/"semantic-match-diagnostics.json").write_text(json.dumps(match_diagnostics,indent=2,ensure_ascii=True))
    (outdir/"probe-log-summary.json").write_text(json.dumps(probe_summary(pathlib.Path(".")),indent=2,ensure_ascii=True))
    (outdir/"evidence-zip-inventory.json").write_text(json.dumps(evidence_zip_summary(pathlib.Path(".")),indent=2,ensure_ascii=True))
    (outdir/"version-summary.json").write_text(json.dumps(summaries,indent=2,ensure_ascii=True))
    print(f"versions={len(summaries)} semantic_pairs={len(pairs)}")
if __name__=="__main__": main()
