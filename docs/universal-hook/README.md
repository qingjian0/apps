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
