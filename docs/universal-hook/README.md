# DeepSeek 通用 Hook：跨版本语义定位方案

## 目标与范围

目标宿主仅为官方 Android 应用 `com.deepseek.chat`。本目录把 2.7.1、2.7.2、2.7.3、2.7.4、2.7.5 的静态 APK/APKM 证据，与 2.7.2/code289-cn 的设备日志交叉验证，形成跨混淆版本的 Hook 定位、验证和降级规范。

“通用通杀”在工程上定义为：**同一套语义解析器和 Hook 生命周期管理器，能够在不同宿主版本中自动定位同一业务角色；每个版本可以有独立的候选描述符，但不需要人工维护一套完全独立的 Hook 代码。** 不承诺一个固定类名/方法名适配所有版本。

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

2.7.2 APK 已上传到仓库根目录（`deepseek-2-7-2.apk`，22,205,160 bytes）。本轮扫描会提取每个 APK/APKM 组件的 Manifest 包名、versionCode、versionName、split 标记及 SHA-256；只有这些身份字段与 `dsprobe.log` 的 `2.7.2/code289-cn` 一致，才可认定为同一构建。不得仅凭文件名或 versionName 认定。

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

本方案与自动审计流水线已扩展为五版本矩阵（2.7.1–2.7.5，含 2.7.4 APKM）。完成 Actions 全量扫描并核对每个组件的 Manifest/DEX 身份、Smali 解析完整性和语义候选后，才更新各版本的具体 Profile 和可安装 Hook 代码。静态候选报告不会被标记为真机 Hook 成功。
