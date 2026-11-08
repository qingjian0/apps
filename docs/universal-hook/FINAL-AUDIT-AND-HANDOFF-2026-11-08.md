# DeepSeek Universal Hook：最终审计与交付记录（2026-11-08）

> 本文是本轮五版本静态审计、语义候选、Points-to 完整性和运行日志复核的最终汇总。它覆盖截至提交 `3769fb3b99047bb41ceb52c322c04c93aeda710b` 的可复核证据。本文严格区分静态分析、设备观察、Hook 安装和业务闭环，不将候选描述为已 Hook。

## 1. 交付结论

| 项目 | 结论 |
|---|---|
| 五版本 APK/APKM 静态扫描 | 完成；2.7.1、2.7.2、2.7.4、2.7.5 身份可信；标签为 2.7.3 的输入身份不匹配，隔离 |
| 五版本 aggregate | 成功；Matrix Run [#203](https://github.com/qingjian0/apps/actions/runs/42448208970) |
| Python / Kotlin 静态语义代码 | 已实现多轮硬化；此前有成功 CI，但最新 HEAD 的两个 PR workflow 处于 `action_required`，不得宣称最新 HEAD CI 通过 |
| Points-to 存储预算 | 全局硬上限、按 root 公平分配、跨 APKM split root 去重已实现；完整性门禁保留 |
| 静态候选等级 | E0–E3 已输出；静态等级不授权 Hook |
| 设备运行时 Hook | 未完成；静态产物中的 `runtime_confirmed_count=0`、`hook_authorized_count=0` |
| 旧探针安装异常 | 根因线索已从 `dsprobe.log` 定位为版本 Profile 错配和 unmapped 类名进入 ClassLoader；本仓库没有足够证据表明探针修复代码已实施 |
| 合并状态 | 本文记录提交时 PR #2 为 Open + Draft；是否能合并取决于最新 required checks / branch protection |

## 2. 五版本输入身份

Manifest 身份来自 `audit/universal-hook/version-identity.json`：

| 输入标签 | Manifest versionName | versionCode | 跨版本可信状态 |
|---|---:|---:|---|
| 2.7.1 | 2.7.1 | 287 | trusted |
| 2.7.2 | 2.7.2 | 289 | trusted |
| 2.7.3 | **2.5.2** | **273** | **quarantined：标签与 Manifest 不匹配** |
| 2.7.4 | 2.7.4 | 294 | trusted |
| 2.7.5 | 2.7.5 | 295 | trusted |

特别说明：`deepseek 273.apk` 可作为 Manifest 为 2.5.2 / code273 的 APK 静态证据保存，但不能作为 DeepSeek 2.7.3 的可信跨版本样本。除非替换 APK 或取得可靠构建身份依据，不得解除隔离。

## 3. 五版本扫描统计

数据来自 Matrix Run #203 的最终汇总产物 `audit/universal-hook/version-summary.json`。E3 表示至少四个独立静态证据族，不表示运行时确认。

| 输入标签 | method_count | candidate_method_count | E3（≥4 证据族） |
|---|---:|---:|---:|
| 2.7.1 | 71,243 | 2,233 | 1,183 |
| 2.7.2 | 72,258 | 2,263 | 1,199 |
| 2.7.3* | 64,557 | 1,886 | 1,026 |
| 2.7.4 | 73,611 | 2,283 | 1,223 |
| 2.7.5 | 72,257 | 2,262 | 1,200 |

`*` 2.7.3 标签输入的 Manifest 实际为 2.5.2 / code273，数字仅描述该 APK 本身，不能被解释为 2.7.3 版本统计。

五个版本的 E0–E3 分级计数之和均与 `candidate_method_count` 相等。所有静态产物均满足：
- `candidate_runtime_confirmed_count = 0`
- `candidate_hook_authorized_count = 0`

## 4. Matrix Run 与交付产物

- Workflow run：[#203](https://github.com/qingjian0/apps/actions/runs/42448208970)
- Run ID：`42448208970`
- 五个版本任务和 aggregate 任务均成功。
- Artifact：[universal-hook-matrix-203](https://github.com/qingjian0/apps/actions/runs/42448208970/artifacts/13605820520)
- 审计结果提交：`3769fb3b99047bb41ceb52c322c04c93aeda710b`
- 聚合报告：[`audit/universal-hook/universal-hook-report.md`](../../audit/universal-hook/universal-hook-report.md)
- 版本身份：[`version-identity.json`](../../audit/universal-hook/version-identity.json)
- 版本汇总：[`version-summary.json`](../../audit/universal-hook/version-summary.json)
- 语义匹配诊断：[`semantic-match-diagnostics.json`](../../audit/universal-hook/semantic-match-diagnostics.json)
- 探针日志摘要：[`probe-log-summary.json`](../../audit/universal-hook/probe-log-summary.json)

## 5. Points-to 完整性与预算策略

### 5.1 已修复的问题

旧实现中不同 root 竞争同一记录存储预算，热点 root 可能耗尽预算，导致其他 root 记录缺失；APK split 中相同 owner + method + descriptor 还可能发生 root key 冲突。

当前实现的约束：
1. Call-context 与 contextual-receiver 两类记录使用各自独立的全局硬上限和计数器。
2. 每类记录的预算按 root 采用确定性 quotient/remainder 分配；各 root 配额最大差不超过 1。
3. root 数量超过预算槽位时允许部分 root 配额为 0；仍遍历 root 并记录 dropped/incomplete 诊断，不以“每个 root 至少一个槽位”突破全局上限。
4. 达到某 root 的存储配额只影响记录存储，不得提前停止该 root 的 callee / descendant 遍历。
5. 对跨 APKM component 的重复方法签名，root accounting 使用 component-qualified 稳定 root ID；方法目标解析仍使用完整 owner + name + descriptor。
6. workflow 校验存储数不超过上限、配额公平、root diagnostics 数量一致、E0–E3 覆盖全部候选，并禁止静态产物声明 runtime confirmation 或 Hook authorization。

### 5.2 Matrix #203 的记录量

每一行均为 whole-program 两类记录的实际存储量；两类记录分别受 200,000 全局上限约束。

| 版本 | call-context stored | contextual-receiver stored |
|---|---:|---:|
| 2.7.1 | 82,181 | 71,839 |
| 2.7.2 | 82,958 | 72,433 |
| 2.7.3* | 82,491 | 73,225 |
| 2.7.4 | 83,593 | 72,851 |
| 2.7.5 | 82,897 | 72,385 |

五版本 whole-program 与 candidate-scope 的 `root_diagnostics.root_count` 均与 `root_method_count` 相等；每 root 配额差不超过 1；存储记录数低于各自全局上限。

### 5.3 不能误读的完整性限制

**全局存储未超限，不等于上下文展开完整。** 当前汇总仍显示 `records_truncated=true`、`context_expansion_complete=false`，并有递归、深度截断或调用不完整诊断。因而：
- Points-to 仍是 diagnostic-only。
- 不得将其提升为 DATA_FLOW 强证据。
- 不得据此证明 ART 运行时对象身份。
- Kotlin ingestion 必须继续要求整体完整性门禁；不完整数据不得进入强语义证据。
- 任何不完整、歧义、递归/深度截断或未知目标均保持 fail-closed。

## 6. E0–E3 静态候选分级

候选证据族为：
- `protocol_anchor`：必须是方法级真实字符串常量；invoke 推导的角色提示不能冒充协议字面量。
- `call_graph`：候选方法的调用入边/出边。
- `stable_api_calls`：稳定 Android / Java / Kotlin / Ktor / OkHttp / Serialization 等 API 调用。
- `type_shape`：接口实现或非 Object 直接父类结构。
- `control_flow`：完整 CFG 的可解析控制流边。
- `intraprocedural_points_to`：方法内完整 Points-to 与 singleton field receiver。

| 等级 | 独立证据族数 | 解释 |
|---|---:|---|
| E0_ROLE_MATCH_ONLY | 0 | 只有角色命中 |
| E0_ONE_STATIC_FAMILY | 1 | 单一静态来源 |
| E1_TWO_STATIC_FAMILIES | 2 | 初步交叉佐证 |
| E2_THREE_STATIC_FAMILIES | 3 | 多源静态佐证 |
| E3_FOUR_OR_MORE_STATIC_FAMILIES | ≥4 | 较高静态证据多样性 |

等级是候选排序和审计信息，不是概率、设备验证结论或安装许可。Hook 安装仍需目标版本身份确认、完整描述符、角色必需证据族、候选唯一性、负面证据检查以及真实运行时行为证据。

## 7. 旧设备探针日志：版本错配根因

`dsprobe.log` 的直接日志证据：
- 宿主识别：`hostGeneration=2.7.2/code289-cn`。
- 安装器却选择：`2.7.1 full mode via HostRemap classes=7636`。
- 后续又调用标记为 code257 的 Agent tool-log Canvas renderer。
- 占位/未映射名称 `deekseep unmapped mf6` 进入 ClassLoader，抛出 `ClassNotFoundException`。
- Activity/lifecycle 重入时，多次重复执行安装并出现相同失败。

同一日志还记录了部分独立功能成功：
- ComposeView.setContent native dual-root capture 安装一次；
- Activity font-scale Hook 安装；
- 2.7.2/code289-cn navigation controller capture，class `p16`；
- 捕获 DeepSeek native root，content `zy1`。

### 根因判断

强证据支持“宿主版本识别结果与 Hook Profile / HostRemap 选择不一致”，而不是证明所有新 Universal Hook 候选错误。不能通过随意补一个 `mf6` 类名掩盖路由问题。

### 必须在探针源码仓库完成的修复

1. 以包名、Manifest versionName/versionCode、build/code 标识和必要的 DEX 指纹选择唯一 Host Profile。
2. code289 必须选择 code289 mapping；禁止静默 fallback 到 2.7.1 / code257 full mode。
3. 对 unmapped、空类名、非法描述符在 ClassLoader lookup 前 fail-closed。
4. Hook 按 feature/role 隔离；optional Hook 失败不得使整个安装组失败。
5. 安装幂等键至少包含 process、host fingerprint、role ID 和 resolved full descriptor。
6. lifecycle 重入时复用安装状态，不重复注册同一 Hook。
7. 先只读 observer 验证调用次数、对象身份、线程和返回类型，再逐项开放功能桥接。

**范围声明：** `apps` 当前承担 APK 静态审计、证据聚合和文档归档。若探针安装器实现位于另一个 Android/LSPosed 仓库，本仓库的日志分析不能替代对该仓库源码的修改和真机回归。本轮没有把上述修复描述为已经落地。

## 8. 请求与响应链候选（动态日志范围）

针对日志对应的 2.7.2 / code289-cn 实例，已有 observer 记录：
- 请求对象候选：`ly1 implements wu1`。
- transport dispatch：`zn3.o(wu1, Long) -> y60`。
- low-level transport：`jw3.g(wu1, Long) -> y60`。
- 两层传输入口记录到同一请求对象，并返回 `y60`。
- 响应/continuation 候选：`y60.b(fl4, yb3) -> Object`。
- `y60` implements `el4`。

建议只读验证顺序：
1. `zn3.o`：请求进入传输层；
2. `jw3.g`：底层传输分发；
3. `y60.b`：continuation / 响应回调；
4. `ly1.<init>`：请求对象构造字段来源；
5. 独立还原 callback 具体类的声明方法和终态语义。

以上类名只对日志对应构建有效，不能直接映射到 2.7.5 或其他版本。SSE 分派目前仍有歧义，不能宣称已完成跨版本唯一映射。

## 9. 当前 CI 状态与合并约束

最新 HEAD：`3769fb3b99047bb41ceb52c322c04c93aeda710b`。

最新 PR 工作流：
- [Universal Hook Static Analysis #260](https://github.com/qingjian0/apps/actions/runs/42450409844)：`action_required`。
- [DeepSeek semantic core CI #256](https://github.com/qingjian0/apps/actions/runs/42450409825)：`action_required`。

这两个 run 均已结束，但结论是 `action_required`，没有实际 jobs 执行结果。它们既不是测试失败，也不是成功。历史上其他提交的 Python/Kotlin CI 成功不能替代对最新 HEAD 的验证。五版本 Matrix #203 成功是本轮独立的 APK 静态审计证据，不等同于 PR required checks 全部通过。

如 GitHub 要求人工批准 workflow，应在 Actions 页面完成审批后重新检查 run 和最新 commit checks。不得通过伪造状态、删除 required checks 或绕过保护规则来制造“全绿”。

## 10. 最终状态与剩余工作

### 已交付
- 五版本 DEX/APK/APKM 静态审计和 aggregate。
- 版本身份隔离，2.7.3 标签样本 quarantine。
- 跨方法参数/返回值边与字段槽诊断。
- bounded call-string 与 nested return summary 的 fail-closed 约束。
- Points-to per-root 公平预算、split-qualified root identity、硬上限验证。
- E0–E3 候选证据分级、真实 literal anchor 校验。
- Kotlin Semantic Core ingestion gates 与 HookCoordinator 安全边界。
- 旧设备日志的版本路由错配根因分析。

### 仍未交付
- 最新 HEAD 上两个 PR workflow 的实际 CI 成功结果（当前 `action_required`）。
- 2.7.3 可信 APK 输入替换或身份确认。
- Android 探针仓库中的版本路由、unmapped 拦截、feature 隔离和幂等安装修复。
- 目标设备上的 runtime-confirmed Hook、SSE 分派唯一性、请求/响应完整桥接及业务闭环。
- LSPosed Android Backend 与完整功能域覆盖。

### 发布判定

本次可以交付的是**静态审计引擎与证据归档**，不是可直接宣称生产可用的跨版本 Hook 产品。所有未完成项必须保留为显式 blocker。任何后续版本只有在对应 APK 身份、静态证据、设备运行日志、安装结果和功能回归均可追溯时，才能升级状态。

---
Generated from repository evidence at HEAD `3769fb3b99047bb41ceb52c322c04c93aeda710b`.
