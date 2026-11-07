# Runtime Semantic Hook Engine — 工程架构与交付规范

> 状态：架构基线已定义；核心引擎与设备运行时适配尚未完成。本文不把设计、静态候选或 CI 通过冒充真机 Hook 成功。

## 1. 目标定义

构建一套可复用的 Android 宿主语义发现与 Hook 框架。DeepSeek 2.7.1–2.7.5 是首批训练/回归样本，后续未知版本必须接受盲测。

目标不是保证任意版本 100% 自动 Hook（在程序语义变化、Native/服务端迁移、动态代码加载、反射和加密边界下无法作此保证），而是：
- 不依赖固定混淆类名、方法名或固定调用链；
- 从多源证据识别功能角色、数据边界和可观察事件；
- 通过候选唯一性、证据多样性、运行时行为校验决定是否安装；
- 不确定时按功能域 fail-closed，不影响宿主原生行为；
- 以统一事件契约向 Agent、Prompt、Local API 等模块提供能力。

## 2. 关键设计：从“找方法”升级为“找语义边界”

### 2.1 证据来源

1. DEX 静态结构：类/方法/字段/原型/访问标志/注解/继承/接口。
2. 控制流与调用图：基本块、分支、调用者/被调用者邻域、协程状态机。
3. 数据流：字符串/常量/字段写入/对象构造/序列化输入输出的污点标签（仅追踪结构标签，不采集敏感正文）。
4. 稳定框架边界：Android、Kotlin、Flow、Ktor、Serialization、Room 等 API 的调用形状。
5. 动态观测：方法进入/退出、参数和返回类型、线程、耗时、异常类型、对象生命周期；默认不记录参数值。
6. 运行行为：用户触发的功能阶段、事件顺序、状态转移和请求/响应模型类型。
7. Native/动态加载：JNI 映射、so 导出、ClassLoader、反射调用与动态 dex 加载线索。

### 2.2 语义身份

候选身份由以下内容组成，而非混淆名称：
- FeatureRole（如 prompt.compose、agent.tool.dispatch、local_api.request、conversation.submit）；
- 输入/输出类型结构及约束；
- 调用图邻域和数据流关系；
- 框架交互模式；
- 运行时触发条件和状态转移；
- HostFingerprint 约束。

候选描述符可以随版本变化；语义角色和契约保持稳定。调用链变化时，允许在新的边界上重新定位，而不是强行匹配旧路径。

### 2.3 解析与安装门槛

每个候选必须经过：
1. Host 身份验证：包名、versionCode、签名摘要、DEX 指纹、ClassLoader。
2. 证据聚合：至少三个相互独立的证据族；同一字符串的多次出现不算多个证据族。
3. 结构校验：输入输出类型、调用上下文、对象关系、控制流形态。
4. 唯一性校验：最佳候选与次佳候选达到配置的分差；并列时不安装。
5. 负面证据校验：确认不是 UI 点击、通用网络库、日志方法、错误处理分支等伪候选。
6. 运行时校验：在安全诊断模式下确认候选在对应功能操作中被触发，且非目标操作不会误触发。
7. 角色级安装：幂等键包含进程、宿主指纹、角色和解析方法；角色之间隔离。

静态扫描可生成候选，但不能单独将状态升级为 RUNTIME_CONFIRMED。

## 3. 功能域契约

每个功能域必须定义独立的 FeatureContract：
- roleId、版本范围、必要/可选状态；
- 输入/输出语义类型；
- 触发条件和生命周期；
- 允许采集的非敏感元数据；
- 不允许采集的数据；
- 适配器与桥接事件 schema；
- 正向、负向、并发、取消、异常测试；
- 最低证据门槛与降级策略。

首批角色域：
- Host/Runtime：宿主指纹、进程、ClassLoader、生命周期。
- Conversation/Message：会话、提交、编辑、重试、继续、取消、历史。
- Prompt/Instruction：默认系统提示词、自定义指令、Agent 指令、上下文组装、模板优先级、最终请求序列化。
- Agent：规划、步骤状态、工具选择、工具参数、执行、结果回填、继续推理、终止。
- Tools：注册表、能力声明、执行器、权限门、结果模型。
- Local API：HTTP server、路由、鉴权、models、chat completions、流式转换、取消、并发、LAN。
- Network/Protocol：请求 DTO、Serializer、HTTP、SSE、错误、重试、恢复。
- Multimodal：图片、文件、音频/语音及 APK 实际存在的其他媒体能力。
- Search/Web/Citation：查询、结果、引用和来源。
- Storage/Sync：数据库、偏好设置、缓存、迁移、同步。
- UI/Settings：页面状态、配置入口、开关与 ViewModel。
- Account/Capability/Policy：只读能力与策略边界，不伪造账号状态或绕过服务端安全校验。

**Prompt 隐私规则：** 不采集或持久化提示词原文、消息正文、附件内容。只允许来源标签、模板标识/哈希、开关状态、长度区间、类型结构等非内容元数据。

**Local API 边界：** 模块自己的 HTTP Gateway 与 DeepSeek APK 内部网络调用是两个不同组件。若宿主 APK 不含 Local API Server，必须明确标记为模块侧能力，不得虚构宿主 Hook 点。

## 4. 引擎组件

| 组件 | 职责 | 输入 | 输出 |
|---|---|---|---|
| HostFingerprint | 宿主身份、进程、ClassLoader | Package/DEX/签名元数据 | HostIdentity |
| DexGraph | DEX 解析、调用图、类型/字段图 | APK/DEX | ProgramGraph |
| FlowAnalyzer | 控制流、数据流和协程结构 | ProgramGraph | FlowFacts |
| BehaviorObserver | 运行时元数据观察 | 目标进程行为 | RuntimeFacts |
| SemanticDiscovery | 角色候选生成与证据归并 | 静态/动态证据 | CandidateSet |
| CandidateVerifier | 独立证据、负面证据、唯一性和版本约束 | CandidateSet | Verified/Rejected |
| HookCoordinator | 幂等、隔离、卸载/重试状态 | VerifiedHookPlan | InstallState |
| AdapterRegistry | 版本差异封装 | FeatureContract + resolved endpoints | FeatureAdapter |
| EventBridge | 稳定事件 schema 和隐私过滤 | FeatureAdapter events | Module events |
| RegressionHarness | 版本/功能测试与盲测 | APK + test scenarios | Evidence report |

核心引擎不直接依赖 Xposed/LSPosed API。运行时平台通过 HookBackend 接口注入，方便单元测试、模拟后端和未来平台适配。

## 5. GitHub 云端工程策略

GitHub 是唯一源码和分析产物工作区：
- 所有源代码、配置、Profile、报告通过仓库分支提交；
- Actions 执行 APK 静态分析、单元测试、构建、质量门禁和回归；
- 大体积原始 APK 作为输入材料管理；派生索引按需压缩、分版本保留；
- CI 只发布脱敏元数据、候选描述符和测试结果，不提交 prompt/body/token/cookie；
- 不依赖开发者本机保存分析文件或执行编译。

云端 CI 能验证静态分析、Resolver 逻辑、HookBackend 模拟行为和构建产物。真实 LSPosed/Android 行为仍需要设备或自托管 Android runner；没有设备证据时状态保持 STATIC_CONFIRMED / SIMULATED_CONFIRMED。

## 6. 自动化流水线

1. Ingest：校验 APK/APKM、SHA-256、Manifest、split、DEX 数量和签名信息。
2. Static Analysis：DEX/Smali/Native/manifest 全量索引，生成调用图和候选证据。
3. Semantic Discovery：按角色识别候选，保存证据链和负面证据。
4. Core CI：编译核心引擎，执行单元测试、属性测试和契约测试。
5. Simulated Hook：使用 FakeHookBackend 验证幂等、冲突、异常隔离、取消和重入。
6. Build：构建 Android/LSPosed adapter（当模块工程进入仓库后）。
7. Cross-version：已知版本回归 + 留出版本盲测；新版本不能只用已知 Profile 回放。
8. Device validation：真机/自托管 runner 产生签名化测试报告，单独标记真实运行证据。
9. Publish：汇总功能覆盖矩阵、版本差异、未识别角色和回归结果。

## 7. 完成状态机

功能域的状态只能单向升级，除非新版本回归失败而降级：

DISCOVERED → STATIC_CONFIRMED → SIMULATED_CONFIRMED → RUNTIME_CONFIRMED → BRIDGED → TESTED

- DISCOVERED：仅发现关键词/结构线索。
- STATIC_CONFIRMED：反编译/DEX 结构和调用关系确认。
- SIMULATED_CONFIRMED：Resolver 和 HookBackend 模拟测试通过。
- RUNTIME_CONFIRMED：目标 Android 进程实际触发证据通过。
- BRIDGED：稳定事件契约可用。
- TESTED：完整功能正负向和回归用例通过。

不同证据层不可相互替代。设备不可用时，交付报告必须明确停在相应阶段。

## 8. 首轮交付顺序

A. 先完成并验证静态证据管线（现有五版本扫描器），包括输入身份、DEX 完整性、Smali 解析质量、APK split 覆盖和聚合报告。

B. 建立独立 Kotlin/JVM 语义核心：模型、证据聚合、候选评分、唯一性门槛、fail-closed Resolver、幂等 HookCoordinator、FakeHookBackend 测试。

C. 已开始实现 DEX/Smali 调用图、跨方法字段读写关联和控制流形态数据提供器；下一步补充精确基本块边、字段值传播、类型/接口图和序列化注册关系。

D. 为 Prompt、Agent、Tools、Local API、Conversation、Multimodal 等建立契约和版本证据矩阵。APK 不含的能力明确归属模块侧或 N/A。

E. 接入 LSPosed HookBackend 和 Android 模块构建；真机验证前不宣称可安装或通杀。

F. 使用未参与开发的新版本 APK 盲测。盲测报告记录自动定位率、歧义率、误 Hook 率、漏检率和人工介入点。

## 9. 验收标准

- 类名、方法名变化测试通过：语义等价的替代实现可被 Resolver 识别。
- 调用链变化测试通过：新增包装层、拆分方法、合并方法后可定位新的合法边界，或安全拒绝。
- 干扰候选测试通过：UI、日志、通用网络方法不能冒充业务角色。
- 多候选/低置信度/版本未知时 fail-closed。
- Hook 重入、并发安装、局部失败、进程重启不重复安装、不影响其他角色。
- Prompt 与消息内容不进入持久化日志。
- Agent 工具链必须验证真实执行/结果回填，不以 ToolCall DTO 存在作为闭环证明。
- Local API 必须分别验证路由、鉴权、非流式、流式、错误、取消、并发和 LAN 绑定。
- 新版本盲测与真实设备测试分别出具结果；不允许仅凭五个已知 APK 声称通杀。

## 10. 当前事实状态

- 已有：五版本 APK/APKM 输入清单、独立审计 workflow、Smali/DEX 方法与调用边扫描器、初版候选聚合器、2.7.3/2.7.5 SSE 链路证据、2.7.2 动态 Hook 日志线索。
- 已完成：五版本（2.7.1–2.7.5，含 2.7.4 APKM）Actions 全量静态审计，Run `42345954380` 的五个版本任务和 aggregate 均成功；完整统计、输入哈希、组件清单、DEX/方法/调用边/字段/控制流指标记录于 `docs/universal-hook/五版本静态审计与语义解析记录-2026-11-07.md` 和 `audit/universal-hook/`。
- 已发现并纠正：首轮静态解析把第三方验证 SDK 的方法误判为宿主 `local_api.request`；已移除宿主 APK 对模块 Local API Gateway 的角色映射。首轮 2.7.5 `conversation.session` 候选的胜出分差仅约 0.355，已将默认 margin 提高至 0.5。
- 已增加 HookCoordinator 安装授权门槛：要求完整运行时 HostFingerprint（含 versionCode/versionName/签名摘要/DEX/ClassLoader）以及 `HOST_IDENTITY`、`RUNTIME_BEHAVIOR` 证据；静态候选不得直接安装。
- 身份核验增强：扫描器现调用 `aapt dump badging` 提取二进制 Manifest 的 package/versionCode/versionName/split，并调用 `apksigner verify --print-certs` 记录签名证书 SHA-256；Ubuntu runner 首次未找到预装 build-tools，已改为 apt 安装 `aapt`/`apksigner`。新审计 Run `42347209753` 需验证安装与输出。
- 本轮新增的 Local API 边界、静态候选禁止安装、运行时身份缺失禁止安装、近似并列拒绝测试，等待最新 Semantic Core CI 结果。
- 已有核心原型：Kotlin/JVM SemanticResolver（独立证据族、候选歧义和 fail-closed）、角色级幂等 HookCoordinator、HookBackend 抽象、元数据 FeatureContract、StaticAuditJsonReader/StaticEvidenceMapper/StaticAuditCli、RuntimeBehaviorVerifier，以及 StaticProgramGraph（调用者/被调用者索引、跨方法字段读写关联、控制流形态统计、类继承与接口实现关系）。
- 身份增强后的五版本静态接入 Run `42347209753` 对每个版本均得到 0/17 个角色可接受，所有候选均因歧义被拒绝；首轮发现的宿主 Local API 假阳性已移除。这是当前 fail-closed 结果，不是 Hook 解析成功。
- 语义证据继续收紧：默认至少四个独立证据族；平台框架/第三方 SDK owner 带负面证据并被默认策略禁止；调用图和跨方法字段流现在传播稀有语义锚点，以区别“方法自身命中字符串”与“上下游共同体现同一语义”。对应测试正在运行。
- 新增 RolePolicy.forRole：按功能域要求核心证据族（协议锚点、调用图、类型结构），并为 Prompt/Agent/Tools/Conversation/Storage/Search/多模态等要求字段数据流，为 SSE/PoW 要求控制流，为网络路由/Flow 要求稳定框架交互；静态 ingest 现使用生产策略而非宽松默认策略。
- 当前 CFG 仅是分支/标签/返回/异常的结构摘要与基本块数量估计，不是完整基本块图；当前字段流是基于字段读写的跨方法静态关联，不等于完整污点分析；类型图目前覆盖父类/接口/实现者，尚未覆盖泛型签名、注解、反射和运行时动态类型。
- 尚未实现：完整 DEX/CFG/Dataflow 引擎、从 APK 自动生成运行时证据的语义发现器、LSPosed Android Backend、Prompt/Agent/Tools/Conversation/Multimodal/Storage/Settings 全功能桥接、模块侧 Local API Gateway、未知版本盲测、真机验证。

## 12. 2026-11-07 Resolver 收敛轮次（Run 42350351361）

本轮针对五版本真实索引实施两项解析器修正，并通过独立 JVM CI：

1. 先按角色证据合同过滤候选，再对满足合同的候选评分和计算 winner margin。缺失必需证据或带禁止性负面证据的高分候选，不得阻挡其他合格候选。
2. 同一 `PROTOCOL_ANCHOR` 证据族内，多个不同强锚点提供有限、封顶的一致性加分；它们仍然只算一个证据族，不增加证据多样性计数。
3. 对过于通用的发现词实行 weak-only 过滤：`prompt`、`instruction`、`Continuation`、`emit`、`collect`、`agent`、`plan`、`Compose`、`ViewModel`、`upload`、`sync` 等词只能用于初筛/诊断，不能单独生成生产语义候选。原始审计索引仍保留这些命中，未丢弃原始材料。

验证：
- Semantic Core CI Run `42350351294`：最终代码提交 `f0e6ecf1df8bd41bb6c1c8b017dad8462d4026fe`，37 项测试通过。
- 五版本完整审计 Run `42350351361`：五个 APK/APKM 子任务、Semantic Resolver 接入、报告回写和产物上传全部成功。
- 审计报告回写提交：`665e7ec761c99cab7721ff89c1e40d4df4032a61`。

五版本结果一致：每个版本从 17 个角色缩减为 15 个实际产生候选的角色；每个剩余角色均因 `ambiguous-candidates` 被拒绝，接受角色仍为 0。当前没有任何静态候选达到安全 Hook 授权条件。

以 2.7.1 为例，候选数变化：
- attachment.file：160 → 72
- multimodal.audio：328 → 43
- multimodal.image：20 → 8
- search.query：491 → 32
- serializer.model：148 → 25
- settings.toggle：632 → 346

本轮结果说明弱锚点过滤显著压缩了噪声候选，但仍未解决调用图邻域中相似候选的消歧。下一阶段不应继续盲目加字符串，而应实现精确 CFG、寄存器/参数/返回值数据流、协程状态机恢复，并用人工确认的 2.7.3/2.7.5 SSE 调用链作为已知真值集，验证静态分析器能否恢复同一语义边界。所有候选仍须通过真实运行时行为证据后才能安装。


## 13. 2026-11-07 Smali CFG 首轮落地与五版本验证（Run 42355753085）

本轮将原先的 `branch_count/label_count/basic_block_estimate` 统计升级为可审计的指令索引级控制流图（CFG）摘要：

1. 将 Smali 可执行指令映射为方法内指令索引；`.packed-switch`、`.sparse-switch`、`.array-data` 等 payload 伪指令不计入可执行指令序列。
2. 以方法入口、条件/无条件跳转目标、分支后的顺序位置、switch case、异常处理器和 try 范围边界建立基本块 leader。
3. 显式构建 conditional、goto、fallthrough、switch、switch-default 和 exception 边。
4. 未解析的跳转标签、switch payload 或异常范围会记录在 `unresolved_targets`，并将 CFG 标记为不完整。
5. CFG 明细边最多保存 256 条；若边列表被截断，`edges_truncated=true` 且 `complete=false`。不能因所有标签已解析就把被截断的图当作完整 CFG。
6. 每个方法的 `control_flow.cfg` 输出指令数、基本块数、边数、未解析目标数、完整性和有界边列表。旧的 branch/label 计数只保留作诊断，不再冒充 CFG。

Kotlin `StaticProgramGraph` 已读取 CFG 完整性和结构计数；只有 `complete=true` 且基本块数大于零时才生成 `CONTROL_FLOW` 证据。历史索引缺少 CFG 或 CFG 不完整时，不会由旧分支计数补造控制流证据。

### 验证结果

- Python Smali CFG 测试：12 项通过，覆盖条件跳转、goto、switch payload、未解析标签、异常边和超过 256 条边时 fail-closed。
- Semantic Core CI Run `42355023519`：成功。
- 五版本审计 Run `42355753085`：2.7.1、2.7.2、2.7.3、2.7.4 APKM、2.7.5 五个扫描任务、聚合、Kotlin Semantic Resolver 接入、报告回写和产物上传全部成功。
- 审计报告回写提交：`477ab43f0000a487c19ef649f911e5b1836ce883`。

本轮五版本静态 Resolver 首次各有一个角色通过静态解析门槛：
- 2.7.1：`network.route` → `Lrv3;->g(Ldu1;Ljava/lang/Long;)Lb60;`
- 2.7.2：`network.route` → `Ljw3;->g(Lwu1;Ljava/lang/Long;)Ly60;`
- 2.7.3：`sse.dispatch` → `Lk11;->a(Lk11;Lgw8;Lif2;)Ljava/lang/Object;`
- 2.7.4：`network.route` → `Ljy3;->g(Lnw1;Ljava/lang/Long;)Ld70;`
- 2.7.5：`network.route` → `Lnw3;->e(Lyu1;Ljava/lang/Long;)Lb70;`

其余 14 个角色/版本组合仍因 `ambiguous-candidates` 被拒绝。上述 `resolved` 只表示静态候选通过 SemanticResolver 的角色证据门槛，不表示 Hook 已授权或已安装。静态审计 CLI 不调用 HookCoordinator；HookCoordinator 仍要求完整运行时宿主身份，并要求候选同时包含 `HOST_IDENTITY` 与 `RUNTIME_BEHAVIOR` 证据。当前没有新增任何真实设备 Hook 成功声明。

### 尚存限制与下一阶段

该 CFG 是 Smali 层的保守结构图，不是 ART/Dex verifier，也不包含寄存器级 def-use、参数/返回值传播、对象别名、支配树或完整协程状态机恢复。下一阶段转向寄存器 use-def 与跨基本块 reaching-def 数据流，并用 2.7.3/2.7.5 已人工复核的 SSE 调用链建立真值集；CFG 不完整或数据流无法闭合时继续 fail-closed。


## 14. Dalvik 寄存器操作数 use-def 初步提取（2026-11-07）

在 CFG 结构输出基础上，APK 审计器新增方法级 `register_flow`：

- 对可识别指令记录寄存器读集合与写集合，并保留方法体行号、opcode。
- 覆盖 move/const/new-instance/array/field access/arithmetic/compare/return/branch/monitor/invoke 等常见指令族。
- 识别 `invoke-*/range {vN .. vM}` 连续寄存器范围，并展开为实际寄存器列表。
- 对 `/2addr` 算术指令同时记录目标寄存器的读与写，避免漏掉旧值依赖。
- 未识别且包含寄存器操作数的 opcode 进入 `unknown_opcodes`，使该方法的 use-def 分类标记为不完整。
- 输出 `read_registers`、`written_registers`、逐指令 `instructions` 和截断状态。

**边界：** 当前只是单方法、单指令级操作数读写提取，不是 reaching-definitions、SSA、跨基本块/跨方法数据流，也未完整建模 wide/long/double 寄存器对、对象别名、异常路径上的寄存器状态或参数/返回值传播。不得将 `register_flow.complete` 解读为完整程序数据流证明；它只表示本方法中已识别的寄存器指令族没有发现未知 opcode。该数据目前只写入脱敏静态索引，不参与 Resolver 加分或 Hook 授权。

本轮新增测试覆盖普通寄存器读写、字段访问、invoke 参数、invoke/range 展开、二地址算术和未知 opcode fail-closed。待对应 GitHub Actions run 完成后，再记录最终测试与五版本复验结论。


## 15. 2026-11-07 CFG-based register reaching-definitions first implementation

The Smali audit pipeline now adds a conservative intraprocedural reaching-definitions pass on top of the explicit CFG:

- Every executable Smali instruction receives a stable method-local instruction index for this analysis pass.
- The CFG exports its basic-block ranges, and the analyzer verifies that the block index covers the complete executable instruction sequence.
- Per-instruction register reads/writes are converted into definition identities (d<instruction-index>:<register>).
- Block GEN/KILL sets are computed with the last definition of each register in that block; a forward fixed-point pass propagates definitions across CFG predecessor edges.
- Each register use is classified as resolved (one reaching definition), ambiguous (multiple reaching definitions), or unresolved (no reaching definition in the recovered graph).
- The method record stores bounded definition/use evidence and completeness state. APK summary aggregates complete-method, definition, use, ambiguous-use and unresolved-use counts.

The first regression cases cover a linear assignment chain, a branch join where two definitions must remain ambiguous, and an unresolved branch target that must fail closed.

**Strict limitations:** this is not SSA construction, a verifier-grade Dalvik interpreter, interprocedural parameter/return propagation, object/field alias analysis, wide-register pair modeling, exception-sensitive register-state analysis, or coroutine state-machine reconstruction. The analysis keeps vN and pN register aliases distinct and does not infer semantic values from them. An unresolved use is not automatically a defect: it may be a method parameter, incoming value, or a value whose definition lies outside the analyzed method. The output is evidence for later graph work, not sufficient semantic proof and never Hook authorization.

The next implementation step is to add parameter/return edges between methods and field-value propagation, then validate the recovered graph against manually confirmed 2.7.3/2.7.5 SSE routes and negative candidates. Any incomplete CFG, unknown opcode, index mismatch or non-convergent dataflow remains ineligible as a complete dataflow evidence family.


## 16. 2026-11-07 跨方法参数/返回值数据流第一版

本轮在单方法 CFG reaching-definitions 之上增加了跨方法值边生成器，目标是把“调用关系”提升为“参数与返回值来源关系”。

### 16.1 方法描述符与参数寄存器布局

- 新增 Dalvik/JVM 方法描述符解析，保留对象、数组和基本类型边界。
- 按实例方法/静态方法区分 receiver：实例方法的 p0 为 receiver，静态方法的 p0 为首个参数。
- long / double 按两个 Dalvik register words 计算参数槽位；数组/对象按一个 word。
- 方法入口为参数寄存器建立 synthetic reaching definitions（entry:pN），避免把合法的 incoming parameter 错判为 unresolved。
- 当前参数别名以 Smali pN 表示；不把 vN 与 pN 自动合并，也不尝试推断 .locals / .registers 下的物理寄存器别名。

### 16.2 调用点参数映射

每个可识别 invoke-* 调用点额外记录：
- 指令索引、行号、invoke opcode；
- 精确目标 owner、方法名和完整 descriptor；
- 按调用寄存器顺序展开的实际参数 word 列表（支持 /range）；
- 紧随其后的 move-result* 指令索引和目标寄存器。

只有 owner + name + descriptor 精确匹配到唯一内部方法时才生成跨方法映射。若同一组件存在唯一匹配，优先使用同组件定义；多定义或无定义分别记为 ambiguous / unresolved，不以短类名或方法名猜测目标。

### 16.3 参数与返回值边

- 参数边从 caller 实际寄存器在调用点的 reaching definitions 指向 callee 对应 entry:pN。
- receiver 也作为独立参数槽记录。
- 返回边从 callee return* 读取寄存器的 reaching definitions 指向 caller move-result* 定义。
- long / double 的参数 word 数用于参数槽对齐；当前返回值边以 move-result 目标寄存器为粒度，不做 wide-pair 语义合并。
- caller 或 callee 的 CFG/dataflow 不完整、use/definition 证据被截断、调用点列表被截断时，不生成值边，并记录不完整调用点计数。

### 16.4 字段槽索引（非对象污点传播）

新增字段访问点索引，记录：
- 精确字段描述符 owner->name:type；
- iget/sget 读取或 iput/sput 写入；
- value register、instance receiver register（静态字段为空）；
- 指令索引、行号、组件和所属方法。

另生成跨方法 field-slot 分组，只有同一精确字段描述符同时存在读和写时才列出潜在读写关联。**这不是对象实例级传播**：当前没有证明两个 pN/vN receiver 指向同一对象，因此 instance_identity_confirmed=false，字段槽分组不得直接作为强语义证据或 Hook 授权条件。

### 16.5 产物与统计

- interprocedural-value-edges.jsonl.gz：参数/返回值值边。
- field-slot-index.jsonl.gz：精确字段槽读写分组，显式标记对象身份未确认。
- methods.jsonl.gz：保留参数寄存器、调用点、字段访问点和方法内 reaching-definitions。
- summary.json：增加参数定义数、invoke/field 访问点数、参数/返回边数、无法解析/歧义调用数、数据流不完整调用点数和字段槽统计。

### 16.6 已知限制与下一步

当前实现仍不是完整 DEX 解释器或完整程序切片：
- 未实现对象别名/points-to 分析、数组元素传播、反射与动态 dispatch；
- 未实现跨调用上下文敏感的递归固定点传播；
- 未实现 wide 返回值双寄存器合并、异常路径寄存器状态和协程 Continuation 状态机恢复；
- invoke-custom、invoke-polymorphic 等特殊调用形式需要单独验证；
- 精确 owner/name/descriptor 无法解析时保持 unresolved，不猜测映射；
- 字段槽读写关联不证明对象实例相同。

下一阶段应先补齐 Python 单元与真实五版本索引回归，再实现基于参数边的 receiver alias propagation（带对象创建点/参数来源），最后将字段槽分组升级为带别名证据的字段值传播。只有被多条独立证据验证的传播关系才可进入生产 SemanticResolver；本轮新图不直接改变 Resolver 评分或 HookCoordinator 授权。


补充 fail-closed 规则：Dalvik wide 指令（包含 wide / long / double 的寄存器操作）在 pair-aware transfer function 完成前会被标记为 unknown opcode，使该方法的数据流完整性失败；不能只追踪 wide value 的低位寄存器并假装整个值已解析。新增回归用例覆盖 move-wide 与 return-wide。


补充调用点完整性门槛：方法内 invoke opcode 总数必须与成功解析的标准 invoke-site 数一致；invoke-custom、invoke-polymorphic、quickened 或无法识别的调用形式不会被猜成普通直接调用。只要调用点清单存在未解析或截断，调用方方法的跨方法值边整体跳过并计入不完整统计。字段访问 opcode 数与字段访问点数也单独核对，避免字段槽索引被误读为完整字段清单。


### 16.7 Kotlin Semantic Core 接入与证据门槛收紧

StaticProgramGraph / StaticAuditCli 已接入同目录的 interprocedural-value-edges.jsonl.gz，并读取 summary.json 的 edges_truncated 状态。只有 summary 明确确认值边文件未截断时才加载；旧审计目录缺少该索引或摘要时不会补造 DATA_FLOW 证据。

**重要修正：** 同一字段描述符的跨方法读写共现不再单独生成 DATA_FLOW 证据。由于尚无 receiver points-to/alias 证明，它只保留为诊断统计。DATA_FLOW 现在必须来自已解析的参数边或返回值边；字段槽共现不能满足 RolePolicy 的 DATA_FLOW 要求。新增 Kotlin 回归覆盖未截断值边可产生证据、截断值边不产生证据，以及字段槽共现单独不足以产生 DATA_FLOW。


### Conservative object points-to / receiver identity

The static audit now includes an intraprocedural, CFG-sensitive points-to pass. Its
initial supported sources are reference-typed method parameters, the instance receiver,
`new-instance` allocation sites, and `move-object` copies. Unsupported object-producing
operations (including object field loads and object method results) become unknown rather
than inheriting a guessed identity. A field receiver is eligible for same-instance evidence
only when its points-to set is a singleton and is not marked unknown. Repeated accesses
to the same field through that same abstract identity are grouped as confirmed same-instance
within the analyzed method. This is not a global alias/no-alias proof: distinct parameter
tokens may still denote the same runtime object, and interprocedural parameter/return
propagation is not yet implemented. Incomplete CFGs and non-convergent analysis fail closed.

