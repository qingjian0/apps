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

C. 实现 DEX 结构/调用图/控制流数据提供器，将当前 Python 扫描器输出转换为核心引擎可消费的 schema。

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
- 正在修复/验证：Unicode/Smali 字符处理、APK 组件身份、五版本 Actions 全量审计、候选排序和报告。
- 已有核心原型：Kotlin/JVM SemanticResolver（独立证据族、候选歧义和 fail-closed）、角色级幂等 HookCoordinator、HookBackend 抽象、Prompt/Agent/Local API/Conversation/SSE 元数据 FeatureContract 与严格字段白名单，以及读取当前 APK 审计器 JSONL 输出的 StaticAuditJsonReader/StaticEvidenceMapper；独立 Actions CI 正在验证。
- 尚未实现：完整 DEX/CFG/Dataflow 引擎、从 APK 自动生成运行时证据的语义发现器、LSPosed Android Backend、Prompt/Agent/Local API 全功能桥接、未知版本盲测、真机验证。
