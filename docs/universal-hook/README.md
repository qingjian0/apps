# DeepSeek 通用 Hook：跨版本语义定位方案

## 目标与范围

目标宿主仅为官方 Android 应用 `com.deepseek.chat`。本目录把 2.7.1、2.7.2、2.7.3、2.7.4、2.7.5 的静态 APK/APKM 证据，与 2.7.2/code289-cn 的设备日志交叉验证，形成跨混淆版本的 Hook 定位、验证和降级规范。

“通用通杀”在工程上定义为：**同一套语义解析器和 Hook 生命周期管理器，能够在不同宿主版本中自动定位同一业务角色；每个版本可以有独立的候选描述符，但不需要人工维护一套完全独立的 Hook 代码。** 不承诺一个固定类名/方法名适配所有版本。

## 新一代引擎架构

- [Runtime Semantic Hook Engine 架构与验收规范](ENGINE-ARCHITECTURE.md)
- [Kotlin Semantic Core](../../engine/semantic-core/)：当前实现候选证据多样性、歧义拒绝、宿主指纹约束和幂等 HookCoordinator（平台 HookBackend 尚未接入）。
- [Semantic Core CI](../../.github/workflows/deepseek-semantic-core-ci.yml)：独立构建与单元测试，不与 API 项目 CI 共享工作流。

当前 Kotlin 核心是第一阶段原型，不代表 APK 自动语义发现、LSPosed 安装或设备端功能闭环已完成。详见架构文档的状态和验收标准。

## 仓库输入清单

| 输入 | 身份/证据 | 处理方式 |
|---|---|---|
| `deepseek271.apk` | DeepSeek 2.7.1 | 本轮重新核对 Manifest、DEX、类/方法索引 |
| `deepseek-2-7-2.apk` | DeepSeek 2.7.2 / code289-cn 候选 APK | 与 `dsprobe.log`、`deekseep_vision.log` 动态证据逐项交叉验证 |
| `deepseek 273.apk` | DeepSeek 2.7.3 | DEX、Smali、JADX、Native 全量扫描 |
| `com.deepseek.chat_2.7.4-294_...apkm` | DeepSeek 2.7.4 / code294 分包容器 | 解包每个内嵌 APK，按组件分别扫描 |
| `DeepSeek_2.7.5.apk` | DeepSeek 2.7.5 | DEX、Smali、JADX、Native 全量扫描 |
| `dsprobe.log` | 2.7.2/code289-cn Hook 安装日志 | 只作动态版本/失败证据，不套用其他版本描述符 |
| `deekseep_vision.log` | 运行时 observer 大日志 | 汇总调用角色、方法标记、线程/事件；不复制消息正文或凭据 |
| `deepseek-sse-hook-evidence.zip` | 已有 SSE/Hook 证据包 | 生成条目、大小、哈希清单并与新扫描结果核对 |
| 先前分析归档 | 2.7.1、2.7.3/2.7.5、Nexus/Deekseep 模块分析 | 只作为历史证据和参考实现；不将模块 APK 当作 DeepSeek 宿主 APK |

2.7.4 APKM 组件扫描已确认 `com.deepseek.chat`；`versionCode=294` 出现在 `split_config.arm64_v8a` 的 Manifest，而不是 base Manifest。后续身份判断需聚合 base 与 split 元数据，不能只读 base Manifest。

2.7.2 APK 已上传到仓库根目录（`deepseek-2-7-2.apk`，22,205,160 bytes）。当前 APKTool 解码结果能确认 Manifest 包名为 `com.deepseek.chat`，但该 APK 根 Manifest 未提供 `versionCode` / `versionName` 属性；因此当前身份等级只能是 package+APK SHA-256+DEX 指纹。`dsprobe.log` 的 `2.7.2/code289-cn` 不能仅凭文件名认定为同一构建，仍需可比较的设备端 DEX/签名指纹。

## 核心设计：语义定位而非混淆名映射

### 1. 宿主身份层

启动时采集以下非敏感身份信息：

- 包名、versionName、versionCode、签名证书摘要；
- APK/base split 的 SHA-256；
- DEX 数量、DEX header 计数、类描述符集合摘要；
- 关键稳定库/接口的存在性。

版本识别必须以多个身份字段联合判定。versionName 单独匹配不够；APK SHA-256 不同的重打包版本不得直接复用精确 Profile。

### 2. 语义角色层

Hook 不绑定混淆类名，而绑定业务角色：

| 角色 ID | 语义职责 | 优先观察边界 | 不应误判为 |
|---|---|---|---|
| `message.submit` | 用户消息提交/上游编排 | 提交对象进入请求构造前 | 单纯 UI 点击 |
| `request.route` | 请求类型分派、路由和序列化 | 请求 DTO 到 transport 的边界 | 任意 Ktor/OkHttp 请求 |
| `stream.flow` | 原生 Flow 创建、收集、取消 | Flow emit/collect 与 Continuation 交界 | 任意协程状态机 |
| `sse.parse` | 字节流到 event/data 的解析 | ByteReadChannel / 行读取器 | 事件分派器或 UI callback |
| `sse.dispatch` | 命名事件与 DeltaCommand 分派 | 已解析事件对象入口 | 原始网络 parser |
| `session.resume` | 断线恢复/续传 | resume_stream 和自动恢复编排 | 普通重试定时器 |
| `session.cancel` | stop/cancel/interrupt | 取消信号向 Flow/transport 传播 | UI 按钮本身 |
| `serializer.model` | 请求/响应模型序列化 | serializer descriptor / polymorphic registry | 只引用字段名的 UI 类 |
| `agent.result` | 服务端工具结果片段解析与渲染 | ToolOpen/ToolFind/Search Delta 模型 | 已经证明的本地工具执行器 |

请求构造、Flow 生命周期和事件分派通常比全局网络库 Hook 更稳定，也更容易保留宿主自身的会话和网络上下文。UI 层只作为必要的辅助入口，不作为主 transport Hook。

### 2A. 全功能覆盖矩阵（目标范围）

本项目的 Hook 覆盖范围不是“只要网络相关就算完成”。必须以功能域建立独立 Role Profile、证据、Hook 点、桥接事件、测试用例和完成状态。APK 中不存在或当前版本未开放的功能标记为 N/A，不得伪造 Hook。

| 功能域 | 必须覆盖的子功能 | 建议语义角色（示例） | 核心观察边界 |
|---|---|---|---|
| 宿主与运行时 | 版本/签名/DEX/进程/ClassLoader、生命周期、线程、崩溃隔离 | `host.fingerprint`、`runtime.lifecycle` | Application、进程入口、ClassLoader、组件生命周期 |
| 对话与消息 | 新建/切换/删除会话、消息提交、编辑、重试、继续、停止、历史、标题、反馈、分页 | `conversation.*`、`message.*` | UI Intent 到领域命令、Repository、持久化和网络边界 |
| 提示词系统 | 系统提示词、默认提示词、用户自定义指令、模板/前后缀、角色消息、提示词拼装、优先级/覆盖、上下文注入、提示词版本与开关 | `prompt.*`、`instruction.*`、`context.assemble` | 最终请求 DTO 构造前；配置读写入口；模板/策略合并点 |
| Agent 核心 | Agent 模式入口、任务分类/规划、步骤状态、工具选择、工具调用参数、结果回填、继续推理、终止/重试、并行任务 | `agent.plan`、`agent.step`、`agent.tool.dispatch`、`agent.result` | Agent 状态机、ToolCall 生成/分派、结果回注和循环退出 |
| 工具生态 | 内置工具、搜索、网页/URL、文件、代码/计算、图片/视觉、附件、MCP/外部工具（仅在宿主实际存在时） | `tool.registry`、`tool.invoke`、`tool.result` | 工具注册表、参数校验、执行器、权限门、结果序列化 |
| 本地 API / Gateway | 本机 HTTP Server、路由、鉴权、模型列表、Chat Completions、流式/非流式、请求映射、工具调用映射、错误映射、取消、并发、会话关联、LAN 开关/绑定地址 | `local_api.server`、`local_api.route`、`local_api.request`、`local_api.stream`、`local_api.auth` | Gateway 入站请求、适配器边界、宿主请求提交、流式事件回传；若某版本 APK 不含 Gateway，则归属模块侧，不冒称宿主 Hook |
| 网络与传输 | API 路由、请求 DTO、header 插件、HTTP、SSE、心跳、错误、重试、恢复、取消、上传/下载 | `request.*`、`transport.*`、`sse.*`、`session.resume` | 请求构造、Ktor/OkHttp 传输、响应体、事件流 |
| 序列化与协议 | JSON/Proto/自定义 Serializer、模型注册、多态、DTO 映射、版本兼容 | `serializer.*`、`protocol.mapping` | Serializer 注册、descriptor、encode/decode 和适配器 |
| 多模态 | 图片输入/理解、文件/文档、音频/语音输入输出、视频（若版本存在）、附件上传、媒体预处理 | `multimodal.image.*`、`multimodal.audio.*`、`attachment.*` | 媒体选择/预处理、上传、请求模型、响应渲染；不记录媒体正文 |
| 搜索与联网 | 搜索入口、查询构造、结果模型、网页内容、引用/来源、工具结果展示 | `search.*`、`web.*`、`citation.*` | 查询/工具调度、结果解析和 UI 数据模型 |
| UI 与交互 | 页面路由、设置页、菜单、弹窗、状态展示、复制/分享、无障碍/文本选择 | `ui.navigation`、`ui.state`、`settings.*` | UI 事件到 ViewModel/状态层；避免只 Hook 点击事件 |
| 本地存储与同步 | 会话数据库、偏好设置、缓存、草稿、附件元数据、迁移、云端同步 | `storage.*`、`sync.*` | Repository/DAO、DataStore/Preferences、迁移与同步边界 |
| 账号与能力开关 | 登录态、订阅/额度展示、远端功能配置、灰度开关、模型能力列表 | `account.state`、`capability.config` | 只读状态和能力配置；不伪造身份、额度或绕过服务端限制 |
| 安全与权限 | 权限门、隐私策略、敏感字段过滤、证书/网络安全状态、Hook fail-closed | `policy.guard`、`privacy.redaction` | 策略判定和脱敏边界；不 Hook 绕过认证、PoW 或安全校验 |
| 可观测性 | 调用链、耗时、线程、错误、流状态、Hook 安装状态、诊断导出 | `telemetry.*`、`diagnostic.*` | 统一事件桥；只保存脱敏元数据 |

**提示词专项要求：** 至少分别识别默认系统提示词、用户自定义指令、Agent/工具提示词、上下文/历史消息拼装、最终请求序列化五个阶段；追踪开关与优先级，但默认只记录来源标签、长度、模板 ID/哈希和开关状态，不记录提示词原文或用户内容。只有用户明确启用受控诊断时，才允许在本地临时查看非敏感测试样本。

**本地 API 专项要求：** 明确区分“宿主 APK 内部的请求/响应 Hook”与“模块自身的 Local API Gateway”。Gateway 的 HTTP 路由、鉴权、模型映射、流转换和 LAN 监听属于模块工程；宿主 Hook 只负责安全地桥接 DeepSeek 原生会话/能力。两者必须有独立测试，不得把 APK 中不存在的本地 HTTP Server 误判为宿主功能。

**完成判据：** 每个功能域都必须登记 `DISCOVERED → STATIC_CONFIRMED → RUNTIME_CONFIRMED → BRIDGED → TESTED` 状态；支持的版本逐一记录。静态字符串命中不等于功能存在，候选方法不等于 Hook 可用，Hook 安装成功不等于业务闭环通过。最终交付必须提供功能覆盖矩阵、版本差异表、Hook Profile、测试证据和明确的未覆盖清单。

### 3. 候选证据评分

候选必须同时检查下列独立证据族：

1. **协议锚点**：路由、事件名、模型类型名、稳定 header 名称。
2. **调用图**：谁创建/调用候选，候选调用谁；上下游至少一层。
3. **方法描述符**：参数、返回值、泛型擦除形态、Continuation 位置。
4. **类型结构**：superclass、interfaces、字段类型和对象关系。
5. **稳定 API 调用**：Ktor、ByteReadChannel、Flow、Serializer、JSON 等框架调用族。
6. **字节码形状**：opcode 分布、异常处理块、协程状态分支、对象构造和 emit 调用。
7. **动态观察**：设备日志中的真实触发、receiver/对象类型、线程和事件顺序。

评分只用于排序，不单独授权安装。正式安装至少需要三个独立静态证据族；要标记为“设备验证通过”，还必须有对应版本的真实运行日志。候选并列、关键描述符不符、ClassLoader 无法解析、版本身份不确定时必须 fail-closed。

### 4. 跨版本映射算法

扫描器先按语义角色和稳定锚点生成候选，再以以下特征做跨版本相似度排序：

- 语义角色及协议锚点交集；
- 稳定 Android/Kotlin/Ktor/Serialization API 调用族；
- 规范化 opcode 分布；
- 调用者/被调用者邻域；
- 参数/返回类型形态；
- 继承和接口结构。

混淆类名和方法名不参与跨版本身份判定。候选映射必须回看 Smali/JADX 证据，不能仅凭相似度自动升级为已确认映射。

## 运行时 Universal Resolver

推荐将通用 Hook 实现拆成五个组件：

1. `HostFingerprint`：识别包、版本、签名、DEX 指纹和 ClassLoader。
2. `SemanticResolver`：根据角色 Profile 搜索候选方法，验证完整描述符、类型关系和调用特征。
3. `CandidateVerifier`：检查候选唯一性、置信度和负面条件；输出可审计的解析报告。
4. `HookCoordinator`：按角色幂等安装；每个角色独立状态，不让一个可选 Hook 失败拖垮全部安装。
5. `EventBridge`：把已确认的宿主事件转换为模块内部稳定事件模型；不直接依赖宿主混淆 DTO 泄漏到 API 层。

建议状态机：

```text
UNKNOWN_HOST
  -> IDENTIFIED
  -> PROFILE_SELECTED | SEMANTIC_SCAN
  -> CANDIDATES_FOUND
  -> CANDIDATE_VERIFIED
  -> HOOK_INSTALLED
  -> OBSERVING
  -> BRIDGE_ENABLED

任何阶段出现版本冲突、候选歧义、描述符不符或解析异常：
  -> ROLE_DISABLED (fail-closed)
```

安装幂等键建议为 `process + hostFingerprint + roleId + resolvedMethodDescriptor`。不能只用全局 AtomicBoolean，否则版本切换、进程重启或局部失败可能导致状态错误。

## 已知动态问题与修复方向

`dsprobe.log` 明确显示：

- 宿主日志识别为 `2.7.2/code289-cn`；
- 安装器却选择 `2.7.1 full mode` / `HostRemap classes=7636`；
- 后续又触发 `code257` Canvas renderer 映射；
- `deekseep unmapped mf6` 引发 `ClassNotFoundException`；
- 多次 lifecycle 重入反复执行 `installAllFeatureHooks` 并重复失败。

这不是简单增加一个 `mf6` 替代类名能解决的问题。必须先修复 HostFingerprint/Profile 选择，再将 Hook 安装改为按角色幂等、失败隔离。未知版本不允许回退到“最接近版本的 full mode”。

已有 observer 线索包含请求接口/transport 候选（例如 `ly1`、`jw3.g`、`zn3.o`、`y60`）。这些只代表特定日志对应构建中的动态候选；必须与 APK 静态证据逐项核对后，才能成为某个版本 Profile。

## 安全、隐私与稳定性约束

- 仅针对 `com.deepseek.chat`；不对其他应用做全局 Hook。
- 默认只读观察；不篡改认证、登录、PoW、服务端策略或宿主安全状态。
- 不采集 prompt、消息正文、Authorization、Cookie、API Key、挑战原文、salt、nonce 等敏感值。
- 日志仅保留方法描述符、参数类型、返回类型、对象标识、线程、耗时、异常类型和必要的脱敏事件元信息。
- Hook 失败时原样放行宿主行为，不吞异常、不伪造返回、不阻断原生网络请求。
- 不把 ToolOpen/ToolFind/Search 等服务端返回模型等同于本地工具执行闭环。

## 自动审计与交付

专用工作流：`.github/workflows/deepseek-universal-hook-audit.yml`

脚本：

- `scripts/audit_deepseek_apk.py`：APK/APKM 组件、DEX header、Smali 方法/调用边、协议锚点、Native 库和候选方法索引。
- `scripts/aggregate_deepseek_hook_audit.py`：跨版本语义匹配、运行日志汇总、旧 SSE 证据包盘点和最终报告。

自动结果写回本分支 `audit/` 目录，包含：

- 每个版本的 APK/DEX/Native 清单；
- 压缩的完整类索引、方法索引和调用边；
- Hook 候选方法 JSON/CSV；
- 跨版本语义匹配；
- 运行探针摘要和证据包哈希清单；
- 汇总报告。

JADX 反编译失败必须保留退出码和错误日志；Smali 是控制流复核证据，不把 JADX 输出文件数量等同于完整反编译成功。

## 当前状态

本方案与自动审计流水线已扩展为五版本矩阵（2.7.1–2.7.5，含 2.7.4 APKM）。2026-11-07 的五版本审计 Run \`42345954380\` 中五个版本 job 和 aggregate 均成功，生成 5 份完整索引与聚合报告。

详细扫描数量、SHA-256、组件/split、DEX 头部、方法/调用边/字段/控制流统计、语义候选结果和未完成项，见 [五版本静态审计与语义解析记录](五版本静态审计与语义解析记录-2026-11-07.md)。自动报告位于 \`audit/universal-hook/universal-hook-report.md\`，完整 JSON/JSONL 索引位于 \`audit/\`。

首轮 Resolver 曾把第三方验证 SDK 错判为宿主 Local API，且 2.7.5 会话候选仅以约 0.355 分差胜出。已移除宿主 APK 中的 Local API Gateway 角色映射，默认胜出分差提高至 0.5；HookCoordinator 现要求完整运行时宿主身份和 \`HOST_IDENTITY\`、\`RUNTIME_BEHAVIOR\` 证据。对应回归测试已加入，等待最新 Semantic Core CI 验证。

**静态候选报告不会被标记为真机 Hook 成功。** 当前尚无完整 LSPosed Android Backend、功能桥接和真机闭环测试。


## 语义图分析增量（2026-11-07）

在原有 Smali CFG 与寄存器 reaching-definitions 基础上，审计器新增跨方法参数/返回值证据：
- 方法描述符解析与实例/静态方法参数 word 布局；
- 方法入口参数定义 entry:pN；
- invoke 调用点寄存器列表（含 /range）和 move-result 关联；
- 以完整 owner + method + descriptor 精确匹配生成参数边和返回值边；
- 字段访问点与精确 field descriptor 分组，保留 value/receiver 寄存器；
- 未解析/多重目标、数据流不完整、证据截断和 wide-register 指令保持 fail-closed。

新增产物：interprocedural-value-edges.jsonl.gz、field-slot-index.jsonl.gz。字段槽分组不证明对象实例相同，不能作为强语义证据；现已增加方法激活内对象 Points-to 与有界 call-string 上下文投影，但仅作诊断，不生成 DATA_FLOW 证据或授权 Hook。

专用 Python 静态分析验证工作流：.github/workflows/universal-hook-semantic-audit.yml。测试未通过 Actions 成功结果前，不将本轮标记为 CI 通过。当前工作保留在 Draft PR #2，不合并 main。


Kotlin StaticProgramGraph / StaticAuditCli 已读取参数/返回值边索引；只有 summary 明确确认边文件未截断时才导入。跨方法 DATA_FLOW 证据仅由参数/返回值边产生；相同字段槽的读写共现只作诊断，不再满足 DATA_FLOW 证据合同。对应 Python 与 Kotlin Actions 正在验证。

## Points-to root 预算隔离（2026-11-08）

### 问题证据

此前五版本产物的 Points-to 汇总均达到全局 `200,000` 条存储上限，造成 root 之间竞争同一份记录配额。旧产物记录的丢弃量如下：

| 版本标签 | 丢弃调用上下文 | 丢弃接收者记录 | 旧结果 |
|---|---:|---:|---|
| 2.7.1 | 297,015 | 356,902 | 截断 |
| 2.7.2 | 293,713 | 350,910 | 截断 |
| 2.7.3（APK 身份待确认） | 274,960 | 358,167 | 截断 |
| 2.7.4 | 295,126 | 344,386 | 截断 |
| 2.7.5 | 298,548 | 360,962 | 截断 |

### 修复策略

- `max_records` 是每一种记录族（调用上下文、上下文接收者）各自的全局硬上限；两种记录族分别维护独立的存储计数。
- 使用确定性的 quotient/remainder 分配：`base, remainder = divmod(max_records, root_count)`，各 root 配额相差不超过 1。root 数量超过预算槽位时，部分 root 配额为 0；仍遍历这些 root，并记录 dropped/incomplete 诊断。
- root 身份不能只用方法签名：APK split/component 可能包含相同 owner + name + descriptor。唯一签名继续使用原签名作为稳定键；重复签名使用 component + 方法签名 + 稳定 root ordinal 生成独立 root ID，供配额、队列上下文和诊断使用。方法解析本身仍严格使用完整方法签名。
- **存储截断不再中断分析遍历**：即使某条调用上下文记录未存储，也继续处理其 callee、递归/深度诊断和后续独立调用点。
- `root_diagnostics` 保留每个 root 的 seen/stored/dropped 计数；整体 `records_truncated` 和 `context_expansion_complete` 仍严格反映不完整情况。
- Kotlin Semantic Core 只在整体摘要和 JSONL 记录数一致且完整时加载 Points-to；该数据仍是诊断信息，不得生成 `DATA_FLOW` 证据或授权 Hook。

当 root 数量大于预算槽位时，部分 root 的配额为 0；不得通过给每个 root 强制分配至少一个槽位而突破全局硬上限。root diagnostics 的 `root_count` 必须与 `root_method_count` 一致；相同方法签名跨 component 出现时也必须保留为不同 root。

### 回归覆盖

新增 Python 回归构造一个拥有两个调用点的热点 root，以及一个拥有独立调用点的第二 root，验证：
1. 两个 root 各自拥有独立配额；
2. 热点 root 超额不会耗尽第二 root 的配额；
3. 超额记录不存储，但对应 callee 仍继续遍历；
4. dropped 记录会使整体完整性保持 false。

对应修改位于 `scripts/audit_deepseek_apk.py` 和 `tests/test_audit_smali_graph.py`。代码已提交到 `work/deepseek-universal-hook-audit`；Python CI、五版本重审及 Kotlin 回归需以新提交对应的 Actions 结果为准，未通过前不得标记通过。

### APK 身份阻断项

旧审计产物中的 `deepseek 273.apk` 虽被标为 2.7.3，但 Manifest 实际为 `versionName=2.5.2`、`versionCode=273`。扫描结果可以保留为该 APK 的静态证据，但不能作为已确认的 DeepSeek 2.7.3 版本审计。重新审计时必须继续将其隔离在可信跨版本匹配之外，直到替换 APK 或取得可核对的构建身份依据。

## Hook 候选静态证据等级（2026-11-08）

扫描器现在为每个角色候选输出 `static_evidence_level`、`evidence_family_count`、`evidence_families`、`runtime_confirmed` 和 `hook_authorized`。证据族仅统计可区分的静态来源：

- `protocol_anchor`：角色锚点同时存在于 Smali 字符串常量中；仅由 invoke 目标触发的角色命中不重复算作协议字符串证据。
- `call_graph`：候选方法存在入边或出边。
- `stable_api_calls`：候选方法调用 Kotlin/Java/Android/Ktor/OkHttp/Retrofit 等稳定 API。
- `type_shape`：候选类具有接口实现或非 Object 直接父类。
- `control_flow`：CFG 完整且存在可解析控制流边。
- `intraprocedural_points_to`：方法内 Points-to 完整且至少存在一个 singleton field receiver。

| 等级 | 判据 | 含义 |
|---|---|---|
| `E0_ROLE_MATCH_ONLY` | 0 个独立证据族 | 仅有语义角色命中，不足以支持 Hook 候选结论 |
| `E0_ONE_STATIC_FAMILY` | 1 个静态证据族 | 单一静态来源 |
| `E1_TWO_STATIC_FAMILIES` | 2 个静态证据族 | 初步交叉佐证 |
| `E2_THREE_STATIC_FAMILIES` | 3 个静态证据族 | 多源静态佐证 |
| `E3_FOUR_OR_MORE_STATIC_FAMILIES` | 至少 4 个静态证据族 | 较高静态证据多样性，仍不是运行时确认 |

等级按证据族数量生成，不把重复字符串、混淆名或单一 invoke 的多次出现累计成独立证据。所有静态候选均固定输出 `runtime_confirmed=false`、`hook_authorized=false`；只有独立设备证据和运行时宿主身份校验才能推进到运行时确认，静态等级不能绕过 Kotlin Resolver、负面证据、完整描述符和 fail-closed 门槛。

回归测试覆盖角色命中但无独立证据、真实字符串锚点、多个独立静态证据族，以及任何等级都不授权 Hook。候选 CSV 同步输出证据等级与证据族，summary 输出各等级数量。


### Points-to storage cap edge case (2026-11-08)

The per-root quota is now a deterministic quotient/remainder partition of the configured record-family budget. Per-root quotas differ by at most one. If there are more roots than slots, some roots receive a zero storage quota; those roots are still fully traversed and their dropped-record/incomplete diagnostics are retained. This preserves the hard global cap instead of silently exceeding it with a minimum-one-slot rule. Call-context and contextual-receiver record families each have their own global cap and independent per-root counters. The summary reports both stored counts, the maximum/minimum per-root quota, and each root's actual quota. Regression coverage includes three roots competing for two slots.


### Kotlin ingestion: protocol anchors must be literal (2026-11-08)

Kotlin StaticAuditJsonReader now reads the method-level strings array and passes it to StaticEvidenceMapper. A role anchor is eligible for PROTOCOL_ANCHOR only when the exact anchor also occurs in that method's literal string constants, and generic weak-only anchors remain excluded. Anchor-frequency normalization counts only literal anchors. A role match inferred from an invoke/API token may remain a discovery hint, but it cannot be promoted into protocol evidence by itself. Resolver policy still requires independent evidence families and role-specific required families; this change prevents a static role label from satisfying the protocol-anchor requirement without a real literal.


## 最终审计与交接（2026-11-08）

本轮统一结论、五版本真实 Manifest 身份、扫描统计、Points-to 完整性边界、E0–E3 证据等级、旧探针版本路由异常、CI 状态和剩余 blocker，统一见 [最终审计与交接报告](FINAL-AUDIT-AND-HANDOFF-2026-11-08.md)。

重要状态覆盖此前阶段性记录：Matrix #203 的五版本静态任务及 aggregate 成功；但最新 PR HEAD 的两个 PR workflow 是 `action_required`，不属于通过或失败。2.7.3 标签 APK 仍因 Manifest 2.5.2/code273 被隔离。静态候选不等于 runtime Hook；当前 runtime-confirmed / hook-authorized 计数均为 0。旧探针路由修复需要在探针源码仓库完成，不能由本静态审计仓库的文档替代。



---

# 调用链与逐版本方法证据总表（主文档）

> 本章把静态审计、Kotlin Semantic Core ingestion 和 2.7.2/code289-cn 设备 observer 线索放在同一条证据链中。混淆类名仅在对应 APK 身份内有效。标记为“候选”的方法不等于已安装 Hook；语义角色的跨版本匹配也不自动证明每一条边都存在直接 invoke。

## 1. 先看完整业务链：从提交到流式响应

目标是恢复 DeepSeek 原生对话链，而不是把任意网络库方法当作 Hook 点。按业务语义，链路分为以下阶段：

| 顺序 | 语义层 | 需要捕获的对象/事件 | 当前证据与状态 |
|---:|---|---|---|
| 1 | UI / Compose 入口 | 输入提交、页面/会话状态、Compose root | 设备日志确认 ComposeView.setContent native dual-root capture 安装 1 次；捕获 native root content=zy1 |
| 2 | Message Submit / Agent 编排 | 用户提交命令、会话 ID、模型/模式、附件和提示词组装 | 尚未获得唯一且完整的跨版本提交方法；不能用 UI 点击代替 |
| 3 | Request DTO 构造 | 请求对象、字段赋值、会话上下文、附件引用 | 2.7.2 observer 请求对象候选 ly1 implements wu1；构造器/字段来源仍需逐字段核验 |
| 4 | Request Route / Transport Dispatch | 请求 DTO 进入传输层，选择 endpoint/请求配置 | Kotlin resolver 在可信版本中唯一解析 network.route；2.7.2 为 jw3.g(wu1, Long)->y60 |
| 5 | Low-level Transport | HTTP 请求实际发送、header/plugin、body、响应对象 | 2.7.2 observer 同时标记 zn3.o(wu1, Long)->y60 与 jw3.g(wu1, Long)->y60；两者的直接调用先后关系需以目标 APK invoke edge/设备事件序列确认 |
| 6 | Response / Continuation | 响应体、挂起恢复、错误/完成/取消 | y60 implements el4；另有 y60.b(fl4, yb3)->Object 响应回调候选，需核验完整声明与实际触发 |
| 7 | SSE Byte / Line Parse | 字节流、行读取、event/data/id/retry、空行分帧 | 当前 sse.parse 在五份 ingestion 中均有两个竞争候选，resolver 拒绝唯一解析 |
| 8 | SSE Event Dispatch | 已解析事件到 Delta/事件模型、工具事件和完成事件 | 2.7.1/2.7.2/2.7.4/2.7.5 存在候选歧义；code273 样本虽静态解析出一个候选，但该样本身份不可信，不能作 2.7.3 通用结论 |
| 9 | Flow / Coroutine | emit、collect、Continuation resume、cancel、异常传播 | 跨版本图匹配数量较多，但候选存在歧义和截断；不得据此指定唯一 Hook |
| 10 | UI State / Render | 消息增量、工具卡片、引用、完成态、错误态 | 设备日志只确认 native root/navigation 捕获；尚无完整响应 Delta 到 UI 状态的闭环证据 |

**重要：** 上表是“业务链阶段图”，不是宣称所有相邻阶段已由单条静态 invoke 链贯通。当前最强的 2.7.2 证据集中在 request DTO / transport 入口；SSE parser、event dispatcher、Flow 与最终 UI 状态仍需要逐边补证。

## 2. 2.7.2 / code289-cn：设备观察与方法候选

这是目前唯一有明确设备 observer 标记的版本。日志文件为仓库根目录 deekseep_vision.log（约 6.44 MB、19,746 行）和 dsprobe.log（12,320 bytes、49 行）。probe-log-summary 记录 deekseep_vision.log 中：
- observer_session_start：1
- observer_role:transport-low-level：1
- observer_role:transport-dispatch：1
- request_class_marker：1
- request_constructor_candidate：2
- request_factory_candidate：5
- observer_installed_event：4
- top method markers：jw3.g、zn3.o 各 1 次

### 2.1 请求对象与传输入口

| 节点 | 记录 | 语义判断 | 证据状态 |
|---|---|---|---|
| Request model | ly1 implements wu1 | ly1 是实现 wu1 的请求对象候选；wu1 是 transport 接口/请求抽象候选 | observer class marker；必须回到 code289 DEX 核验字段和构造来源 |
| Transport dispatch | zn3.o(wu1, Long)->y60 | 上层 transport dispatch 候选 | observer method marker；单次标记，不代表全调用路径已复原 |
| Low-level transport | jw3.g(wu1, Long)->y60 | Kotlin resolver 的 network.route 唯一候选；返回 y60 | 静态 resolver + observer method marker |
| Response carrier | y60 implements el4 | y60 具有 el4 接口关系，可能承载响应/continuation 协议 | 类型结构证据；不单独证明 SSE 语义 |
| Response callback | y60.b(fl4, yb3)->Object | 响应/continuation 回调候选 | 既有方法审阅线索；需要用 code289 完整 descriptor、调用者和设备触发日志复核 |

当前可写出的最小证据链为：

    ly1 (implements wu1)
       ├─ request object / request factory evidence
       ▼
    wu1 request abstraction
       ▼
    zn3.o(wu1, Long) -> y60       [transport-dispatch observer marker]
       ▼
    jw3.g(wu1, Long) -> y60       [network.route resolver + low-level observer marker]
       ▼
    y60 implements el4
       ▼
    y60.b(fl4, yb3) -> Object     [response callback candidate]
       ▼
    SSE parser / event dispatch  [not uniquely resolved]
       ▼
    Flow / UI state              [not yet end-to-end proven]

图中 zn3.o 与 jw3.g 的上下层次是角色层面的候选顺序；在补齐 code289 的精确 invoke edge 和 observer event correlation 前，不应把箭头解释为已证明的直接调用关系。

### 2.2 2.7.2 静态 Resolver 结果

来自 audit/universal-hook/semantic-ingest-summary.txt：

| 角色 | 唯一解析结果 | 分数 / runner-up | 决策 |
|---|---|---:|---|
| network.route | Ljw3;->g(Lwu1;Ljava/lang/Long;)Ly60; | 4.85 / 4.1657 | resolved |
| search.query | Lyv9;->j(Ljqa;Lpq7;Lfy4;Lr15;I)V | 5.0996 / 0 | resolved |
| multimodal.image | Leu0;->t(Context, Bitmap, String)->Uri | 5.2853 / 3.5678 | resolved |
| network.pow | 7 个候选 | — | rejected: ambiguous |
| sse.dispatch | Lnv1;->a(...)Object 与 Lr3;->c(...)Object | — | rejected: ambiguous |
| sse.parse | Lfk0;->y(Object)Object 与 Lg0;->y(Object)Object | — | rejected: ambiguous |
| conversation.session | 30 个候选 | — | rejected: ambiguous |
| attachment.file | 5 个候选 | — | rejected: ambiguous |
| account.capability | 2 个候选，缺少必需证据族 | — | rejected |

这意味着当前 code289 可把 network.route、search.query、multimodal.image 作为只读观察候选；不能把 SSE parser/dispatcher、会话存储、PoW 或附件链升级成唯一 Hook。

## 3. 五个输入版本的逐版本候选映射

以下方法来自静态 semantic ingestion。签名采用 DEX owner/name/descriptor 形式；每个混淆名称只在对应 APK 构建中有效。

### 3.1 Request Route

| 输入标签 | Manifest 身份 | network.route 候选 | Resolver 状态 |
|---|---|---|---|
| 2.7.1 | 2.7.1 / code287 | Lrv3;->g(Ldu1;Ljava/lang/Long;)Lb60; | resolved |
| 2.7.2 | 2.7.2 / code289 | Ljw3;->g(Lwu1;Ljava/lang/Long;)Ly60; | resolved；有 observer marker |
| 2.7.3 标签样本 | **2.5.2 / code273** | Lhx2;->g(Lu01;Ljava/lang/Long;)Lz40; 等 5 个候选 | **rejected: ambiguous；样本隔离** |
| 2.7.4 | 2.7.4 / code294 | Ljy3;->g(Lnw1;Ljava/lang/Long;)Ld70; | resolved |
| 2.7.5 | 2.7.5 / code295 | Lnw3;->e(Lyu1;Ljava/lang/Long;)Lb70; | resolved |

四个可信版本的 request_route 两两语义匹配均报告 7 个 accepted matches，且诊断中的 ambiguous/non-mutual/below-threshold/no-shared-evidence 均为 0。这个结果说明语义特征可跨版本对应，不表示四个版本共享同一混淆类名，也不表示已在四个版本设备上安装 Hook。

### 3.2 Search Query

| 输入标签 | search.query 候选 | Resolver 状态 |
|---|---|---|
| 2.7.1 | Lwh7;->h(Lgla;Ldn7;Lbx4;Ln05;I)V | resolved |
| 2.7.2 | Lyv9;->j(Ljqa;Lpq7;Lfy4;Lr15;I)V | resolved |
| 2.7.3 标签样本 | Llu3;->i(Lo39;Lld6;Lhv3;Ley3;I)V | resolved；仅 code273 隔离样本 |
| 2.7.4 | Ly98;->c(Loua;Lgs7;Ln05;La45;I)V | resolved |
| 2.7.5 | Lm07;->h(Ltqa;Lxq7;Ljy4;Lv15;I)V | resolved |

四个可信版本的 search.query 两两语义匹配各有 1 个 accepted match。该角色更接近查询/搜索请求构造入口，不应直接等同于完整 Agent 工具执行器或网页内容解析器。

### 3.3 Multimodal Image

| 输入标签 | multimodal.image 候选 | Resolver 状态 |
|---|---|---|
| 2.7.1 | Ltjc;->w(Context, Bitmap, String)->Uri | resolved |
| 2.7.2 | Leu0;->t(Context, Bitmap, String)->Uri | resolved |
| 2.7.3 标签样本 | Lqga;->l(Context, Bitmap, String)->Uri | resolved；仅 code273 隔离样本 |
| 2.7.4 | Ltv0;->u(Context, Bitmap, String)->Uri | resolved |
| 2.7.5 | Lfu0;->t(Context, Bitmap, String)->Uri | resolved |

五个样本的候选结构均为 Context + Bitmap + String -> Uri，resolver 分数约 5.2853、runner-up 约 3.5678。它是图片预处理/URI 生成候选，不等于图片上传完成、请求包含图片成功或服务端视觉响应已验证。

### 3.4 SSE Parse 与 Dispatch

SSE 必须拆成两个独立角色：

- sse.parse：把响应字节/行流解析为 event、data、id、retry 等帧字段。
- sse.dispatch：把解析后的事件映射为 delta、tool、search、引用、完成/错误等业务事件。

不能把两者合并成一个“收包方法”。

| 输入标签 | sse.parse 候选 | sse.dispatch 候选 | 最终状态 |
|---|---|---|---|
| 2.7.1 | Lg0;->z(Object)Object / Lmj0;->z(Object)Object | Lvu1;->a(...)Object / Ln3;->c(...)Object | 两角色均歧义 |
| 2.7.2 | Lfk0;->y(Object)Object / Lg0;->y(Object)Object | Lnv1;->a(...)Object / Lr3;->c(...)Object | 两角色均歧义 |
| 2.7.3 标签样本 | Le0;->A(Object)Object / Lyf0;->A(Object)Object | Lk11;->a(Lk11;Lgw8;Lif2;)Object | parse 歧义；dispatch 静态唯一但样本身份隔离 |
| 2.7.4 | Lg0;->y(Object)Object / Lpl0;->y(Object)Object | Lex1;->a(...)Object / Lq3;->c(...)Object | 两角色均歧义 |
| 2.7.5 | Lg0;->z(Object)Object / Lgk0;->z(Object)Object | Lpv1;->a(...)Object / Lr3;->c(...)Object | 两角色均歧义 |

跨版本 semantic-match-diagnostics 对 sse_transport 与 sse_dispatch 的部分 pair 记录了 4 个 accepted matches；这属于图匹配统计。Kotlin resolver 对具体版本仍报告 sse.parse / sse.dispatch 候选歧义。**匹配数量不覆盖唯一性门禁**，不能因为 pairwise match accepted 就选择 top candidate 强行安装。

### 3.5 其他语义角色的跨版本图匹配统计

以下数字是 semantic-match-diagnostics 中可信版本 pairwise 对照的 accepted match 数量范围，不是唯一 Hook 数，也不是功能覆盖率：

| 角色 | 每个版本对 accepted matches（大致范围） | 当前解释 |
|---|---:|---|
| request_route | 7 | 角色结构稳定；可信版本 Resolver 唯一 |
| sse_transport | 4 | transport 相关结构可匹配；不能替代 parser/dispatcher 唯一性 |
| sse_dispatch | 4 | 图级匹配可成立；resolver 仍可能歧义 |
| flow_coroutine | 114–117 | 数量多但同类协程方法大量重复，存在 41–44 个左右的双侧歧义 |
| serialization | 93–98 | 序列化方法族庞大，存在双侧歧义和低分候选 |
| agent_tool | 11–13 | 工具相关结构候选；不等于本地工具执行链 |
| session | 107–117 | 会话方法族数量大，不能据此认定唯一 Session Repository |
| agent_planning | 48–49 | 规划/状态机结构候选，仍需参数/状态语义复核 |
| tool_registry_execution | 11–13 | 工具注册/执行相关候选；必须分离服务端工具事件与本地执行器 |
| local_api_gateway | 3 | 曾出现第三方验证 SDK 误判；宿主 APK 不应据此声明内置 Local API Gateway，角色已从宿主 Hook 解析路径移除 |

## 4. 跨方法参数、返回值与字段流：当前能证明什么

审计器已生成跨方法值流：
- invoke 参数寄存器与目标方法 entry:pN 参数定义建立 argument edges；
- move-result 与目标方法返回值建立 return edges；
- 静态/实例调用使用完整 owner + method + descriptor 匹配；
- unresolved、ambiguous、incomplete、truncated 的映射保留诊断，不生成强边；
- field-slot 读写分组只描述字段槽，不证明两个调用点操作同一个运行时对象；
- Points-to 仅在方法激活内 singleton receiver 等受限范围内提供对象身份线索；跨方法上下文仍受递归、深度和记录预算约束。

五版本的 interprocedural value-flow edge 均未被存储截断，但存在大量 unresolved/incomplete call sites。Points-to whole-program summary 则有 records_truncated=true、context_expansion_complete=false。故当前可以说“存在参数/返回值映射证据”，不能说“已经还原完整请求对象从构造器一路流到 parser 的对象身份链”。

Kotlin ingestion 当前显示 interprocedural Points-to 记录未加载（loaded records=0），虽然能读取 expected counts；不得把 expected count 当成实际载入的上下文记录。值流边文件完整不代表 Points-to 完整。

## 5. UI / Navigation / Native Root 设备证据

dsprobe.log 的 code289-cn 设备会话还记录了三项独立成功：
- ComposeView.setContent native dual-root capture installed x1；
- navigation controller capture installed，class=p16；
- captured DeepSeek native root，content=zy1；
- font scale Hook installed on android.app.Activity。

这些是该设备会话的实际安装/捕获日志，强于单纯静态候选，但它们只覆盖 UI root/navigation/字体缩放观察，不证明 message submit、Agent、请求、SSE、工具结果和 Local API 全链路可用。

## 6. 设备安装失败：原始事件与根因链

dsprobe.log 原始顺序显示：

1. module loaded，hostGeneration=2.7.2/code289-cn；
2. installAllFeatureHooks 开始；
3. installer 选择 “2.7.1 full mode via HostRemap classes=7636”；
4. 同一轮又调用 code257 agent tool-log Canvas renderer；
5. ClassLoader 查找 “deekseep unmapped mf6” 失败，抛 ClassNotFoundException；
6. installAllFeatureHooks 整组失败；
7. lifecycle bootstrap 再次进入安装，重复选择 2.7.1 full mode 并重复失败；
8. 日志统计约 10 次 hook_install_attempt、10 次 wrong_full_mode_selection、10 次 hook_install_failure、20 次 class_not_found。

根因链：

    host fingerprint = 2.7.2 / code289-cn
                  |
                  v
    wrong profile selection = 2.7.1 full mode / code287 map
                  |
                  v
    legacy code257 feature mapping leaks into code289 process
                  |
                  v
    unresolved placeholder "deekseep unmapped mf6"
                  |
                  v
    ClassLoader ClassNotFoundException
                  |
                  v
    whole installAllFeatureHooks group fails
                  |
                  v
    lifecycle re-entry repeats same failed installation

### 必须在探针源码仓库修复

- Profile 选择以 package + Manifest/versionCode + 签名 + DEX fingerprint 联合判断；code289 不得回退 code287。
- 所有类名/描述符必须先经过 resolved-state、格式和目标 DEX 存在性校验；unmapped/placeholder 禁止进入 ClassLoader。
- HookCoordinator 按 feature/role 隔离，optional Hook 失败只禁用本角色，不使其他已安装功能回滚。
- 幂等键至少包括 process + host fingerprint + role ID + resolved full descriptor。
- lifecycle 重入复用安装结果，不重复安装同一 Hook。
- 修复后逐一回归 navigation、native root、request route、SSE parse、SSE dispatch；保留失败日志和真实设备版本指纹。

本轮在 apps 仓库完成的是日志根因定位和审计记录，不是 Android 探针源码修复。

## 7. 以调用链为中心的下一轮验证顺序

| 优先级 | 验证点 | 必须取得的证据 | 通过标准 |
|---:|---|---|---|
| P0 | Host Profile / ClassLoader | code289 设备指纹、所选 profile、每个类名解析结果 | 只选 code289；无 placeholder lookup；无 fallback |
| P1 | Request DTO | ly1 构造器、wu1 字段/接口、字段写入来源 | 构造对象、字段值来源、实际请求实例可关联 |
| P1 | Transport dispatch | zn3.o 与 jw3.g 的完整 descriptor、调用者/被调用者、事件顺序 | 证明直接/间接调用关系；区分 dispatch 与 low-level |
| P1 | Response callback | y60 的接口/字段、b(fl4,yb3) 声明、调用时机 | 与同一 request/response session 关联 |
| P2 | SSE parse | 行读取/帧解析入口、event/data 产物 | 候选唯一，至少覆盖多帧、空行、结束帧、异常帧 |
| P2 | SSE dispatch | 解析事件到 delta/tool/search/error/done 的分派 | 唯一 dispatcher；每种事件有可追溯映射 |
| P2 | Flow / cancel | emit/collect/resume/cancel 的同一 session 关联 | 正常结束、异常、用户取消、断线恢复均可追踪 |
| P3 | UI state | response delta 到 Compose state/message item | 同一会话内内容、工具卡片、完成态正确更新 |
| P3 | Local API bridge | Gateway 入站请求到宿主原生请求，再回传 OpenAI chunk | 非流式/流式/工具/取消/错误均闭环；Gateway 与宿主 Hook 独立验收 |

**每个验证点必须记录：** host fingerprint、split/component、完整 method descriptor、调用线程、对象 identity token（仅随机化诊断 ID）、调用顺序、返回/异常、触发场景和脱敏后的事件类型。不得记录 prompt、消息正文、Authorization、Cookie、API Key 或原始媒体数据。

## 8. 证据等级与当前结论

| 结论 | 当前等级 | 允许的工程动作 |
|---|---|---|
| 2.7.2 request route 的 jw3.g 候选 | 静态唯一 + observer method marker | 可做只读观察验证；尚不可宣称完整业务 Hook |
| 2.7.2 zn3.o transport dispatch | observer method marker / 角色候选 | 先补完整 descriptor 和直接调用边 |
| ly1 implements wu1 | observer request class marker | 只读检查字段/构造来源 |
| y60 implements el4 | 类型结构证据 | 检查 response/continuation 语义 |
| y60.b(fl4,yb3) | 待复核回调候选 | 不作为已确认 Hook |
| search.query / multimodal.image | 五版本静态 Resolver resolved（2.7.3 样本隔离） | 逐版本只读观察 |
| sse.parse | 五版本均有歧义 | 禁止唯一 Hook 安装 |
| sse.dispatch | 可信版本有歧义；code273 样本单候选但隔离 | 禁止把 code273 结果推广到 2.7.3 |
| navigation p16 / native root zy1 | 2.7.2 设备日志确认安装/捕获 | 可保留已观察功能；仍需回归幂等与版本路由 |
| 完整 Agent / Local API / SSE 闭环 | 未证明 | 不得宣称完成 |

## 9. 本章对应的机器证据

- [semantic-ingest-summary.txt](../../audit/universal-hook/semantic-ingest-summary.txt)：五版本 Kotlin ingestion、每个角色 resolved/rejected 原因和方法描述符。
- [semantic-match-diagnostics.json](../../audit/universal-hook/semantic-match-diagnostics.json)：跨版本 pairwise 匹配、歧义、非互选和阈值统计。
- [probe-log-summary.json](../../audit/universal-hook/probe-log-summary.json)：设备日志哈希、事件计数和 observer method markers。
- [version-identity.json](../../audit/universal-hook/version-identity.json)：Manifest 身份和可信状态。
- [version-summary.json](../../audit/universal-hook/version-summary.json)：调用图、参数/返回值边、Points-to、CFG 和完整性统计。
- [dsprobe.log](../../dsprobe.log)：2.7.2/code289-cn Profile 错配与 ClassNotFoundException 原始日志。
- [deekseep_vision.log](../../deekseep_vision.log)：observer 会话、transport marker、request class/factory/constructor 事件原始日志。

