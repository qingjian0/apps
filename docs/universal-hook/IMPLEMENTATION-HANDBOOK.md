# Universal Hook Engine：跨项目实施手册

> 文档性质：可执行工程规范（Normative Implementation Guide）
> 适用对象：Apps 核心仓库、Deekseep-Custom、Deepseek-Harness-Local-Android，以及后续接入的 Android 宿主 Hook 项目。
> 状态基线：本文定义目标架构与实施顺序；除非“当前实现状态”明确列出代码/测试证据，否则接口和模块均视为待实现，不得对外宣称已交付。
> 核心原则：Apps 是通用引擎唯一源码；接入项目只实现平台/宿主 Adapter，不复制 Resolver、Profile 解析器或 Hook 生命周期管理器。

## 0. 其他 AI 接手时先读什么

严格按顺序阅读：

1. 根目录 `README.md`：仓库定位与当前状态。
2. 本文：跨项目实施合同、模块边界、开发顺序和验收门槛。
3. [ENGINE-ARCHITECTURE.md](ENGINE-ARCHITECTURE.md)：引擎设计原则。
4. [README.md](README.md)：语义角色、功能域矩阵、证据规则。
5. [FINAL-AUDIT-AND-HANDOFF-2026-11-08.md](FINAL-AUDIT-AND-HANDOFF-2026-11-08.md)：当前审计事实、版本身份、CI 与阻断项。
6. [SDK-CONTRACT.md](SDK-CONTRACT.md)：跨仓库 SDK/API 合同。
7. [AI-IMPLEMENTATION-PROMPT.md](AI-IMPLEMENTATION-PROMPT.md)：可直接交给其他 AI 的执行任务书。

接手 AI 必须先核对目标分支 HEAD、PR、CI 和文件现状；不得假设文档中的规划接口已经存在。

## 1. 目标与非目标

### 1.1 目标

交付一套可嵌入不同 Android Hook 项目的通用运行时引擎：

- 自动识别目标宿主身份和运行进程；
- 从 APK/DEX 静态证据与运行时行为证据中定位语义角色；
- 通过完整方法描述符、类型结构、调用图、协议锚点、控制流和负面证据消歧；
- 将已验证的语义角色转换为平台 Hook 计划；
- 通过独立 Hook Backend 执行安装；
- 以稳定事件契约向各宿主模块提供能力；
- 对未知版本、歧义候选、描述符冲突、ClassLoader 错误采取 fail-closed；
- 允许每个功能域独立安装、失败、重试和降级；
- 为已知版本建立回归集，并对未见版本进行盲测。

### 1.2 不承诺

“通用 Hook”不是“任何 APK、任何版本、任何功能都必定 Hook 成功”。程序语义变化、Native 实现、动态加载、反射、服务端能力变化都可能使某功能不可定位。正确行为可以是安全拒绝，而不是猜测一个类名。

不把以下内容当作成功：
- 只找到关键词或字符串；
- 静态候选排名第一；
- 解析出一个混淆类名；
- Hook API 返回成功但目标功能没有触发；
- 收到 ToolCall/ToolOpen 等数据模型但没有证明本地执行闭环；
- CI 编译通过但没有设备运行证据。

### 1.3 仓库边界

| 仓库 | 责任 | 不应负责 |
|---|---|---|
| `apps` | Semantic Core、Profile Schema、Resolver、Hook Coordinator、平台无关事件合同、测试框架、审计与文档 | 各业务项目的 UI、Local API 业务实现、具体宿主功能策略 |
| `Deekseep-Custom` | LSPosed/Xposed Backend、DeepSeek 宿主 Adapter、目标版本真机验证 | 复制通用 Resolver / Profile engine |
| `Deepseek-Harness-Local-Android` | 自身运行环境的 Hook/Host Adapter、Agent/Harness 集成 | 依赖 LSPosed 专有 API；复制 Resolver |
| `OmniRouter` | 标准 API/Gateway 能力消费和协议适配 | 直接依赖 Android Hook、解析 APK 混淆类 |
| 后续项目 | 实现 SDK Adapter 和 Feature Bridge | 修改核心算法的私有分叉 |

## 2. 目标仓库结构

以下是目标结构，不代表所有目录当前已存在。实施时允许根据现有 Gradle 模块做最小适配，但不得破坏模块职责。

```text
apps/
├── audit/                         # APK/DEX 审计产物（现有）
├── scripts/                       # Python 静态分析器（现有）
├── engine/
│   ├── semantic-model/            # 纯 Kotlin：身份、证据、候选、角色、结果类型
│   ├── semantic-core/             # Resolver、Verifier、Policy、Score/Margin
│   ├── runtime-core/              # Coordinator、状态机、HookPlan、事件总线
│   ├── profile-schema/             # Profile JSON schema、解析和校验
│   ├── static-index-reader/        # 审计 JSON/JSONL ingestion
│   ├── android-runtime/            # Android 身份、ClassLoader、反射解析
│   ├── hook-backend-api/           # 平台无关 HookBackend API
│   └── test-fixtures/              # 假宿主、假图、测试 Profile
├── backends/
│   ├── lsposed/                    # 可选独立模块：LSPosed 实现
│   └── fake/                       # JVM 模拟 HookBackend
├── profiles/
│   ├── schema/
│   ├── deepseek/
│   │   ├── code287/
│   │   ├── code289/
│   │   ├── code294/
│   │   └── code295/
│   └── fixtures/
├── adapters/
│   ├── deepseek/                   # 仅角色映射和 FeatureAdapter
│   └── sample-host/
├── sdk/
│   ├── kotlin/
│   └── docs/
├── integration-tests/
│   ├── resolver/
│   ├── fake-backend/
│   ├── profile-validation/
│   └── device/
└── docs/
    └── universal-hook/
```

### 2.1 依赖方向（强制）

```text
semantic-model
   ↑          ↑
semantic-core  profile-schema
   ↑          ↑
runtime-core ← static-index-reader
   ↑
hook-backend-api
   ↑
android-runtime
   ↑
lsposed backend / project-specific adapter
   ↑
Feature Bridge → consumer project (Agent / Prompt / Local API / UI)
```

规则：
- `semantic-model`、`semantic-core` 不依赖 Android、Xposed、LSPosed、宿主 APK 类。
- `runtime-core` 只依赖抽象接口，不直接 import 平台 Hook API。
- `backends/lsposed` 才能依赖 LSPosed/Xposed。
- 各项目 adapter 依赖发布的 SDK，不复制核心实现。
- OmniRouter 不应依赖 Android runtime；它只消费已标准化的 API/事件。

## 3. 核心领域模型

以下是规范级数据模型示意。具体 Kotlin 包名可按当前 Gradle 结构调整，但字段语义和安全规则不得改变。

### 3.1 HostIdentity

必须包含：
- `packageName`；
- `versionName`、`versionCode`；
- `signingCertSha256`（可为空，但缺失时降低身份等级）；
- `baseApkSha256` 和 split APK 摘要；
- `dexFingerprint`（DEX 数量、类/方法计数及规范化摘要）；
- `processName`；
- `classLoaderIdentity`（仅进程内身份标识，不持久化对象引用）；
- `observedAt`；
- `identityCompleteness`。

身份选择必须是多字段联合匹配。versionName 单独命中不得授权精确 Profile。签名或 APK 指纹冲突时拒绝精确 Profile。

### 3.2 Evidence

每条证据必须保留来源和完整性：

- `family`：协议锚点、调用图、稳定 API、类型结构、CFG、数据流、运行时行为、宿主身份等；
- `source`：APK SHA、DEX component、method descriptor、日志/设备 run id；
- `subject`：候选角色和目标方法；
- `polarity`：positive / negative；
- `strength`：有限枚举，不允许把任意浮点数伪装成概率；
- `complete`：证据本身是否完整；
- `details`：脱敏的可复核细节；
- `observedAt` / `toolVersion`。

同一证据族中的多个字符串命中仍只算一个 family。截断的调用图、未闭合数据流和不完整 Points-to 不得作为强证据。

### 3.3 Candidate 与 ResolveResult

候选必须包含：
- semantic role id；
- 完整 owner + method name + JVM/Dex descriptor；
- 输入输出类型摘要；
- 静态证据族集合；
- 负面证据；
- 所属 HostIdentity；
- 排名与 winner margin（仅诊断）；
- 完整性状态；
- 拒绝原因集合。

解析结果必须区分：
- `Resolved`：唯一候选满足静态策略；不代表可安装；
- `NeedsRuntimeVerification`：需要设备行为证据；
- `Ambiguous`：多个候选无法安全区分；
- `Rejected`：身份、描述符、证据或负面策略不通过；
- `UnsupportedHost`：没有受支持身份或适配器。

禁止将空结果、异常或超时默认为 Resolved。

## 4. Profile 规范

### 4.1 版本绑定

每个精确 Profile 至少绑定：
- packageName；
- versionName/versionCode；
- 签名证书摘要（如可得）；
- base APK SHA-256；
- split APK SHA-256 列表（如有）；
- DEX 指纹；
- Profile schema version；
- Profile revision；
- 证据来源链接/审计 run；
- 状态：draft / static-verified / runtime-verified / deprecated / quarantined。

任何身份字段冲突均禁止静默 fallback 到“最接近版本”。

### 4.2 语义角色

Profile 只描述某个 HostIdentity 中的候选证据，不是直接执行的任意代码。每个 role 至少包含：
- `roleId`；
- `requiredEvidenceFamilies`；
- `forbiddenOwners/packages`；
- `candidateMethods[]`；
- `methodDescriptor`；
- `typeConstraints`；
- `callGraphConstraints`；
- `controlFlowConstraints`；
- `runtimeTrigger`；
- `negativeScenarios`；
- `expectedEventSchema`；
- `minimumResolverPolicy`；
- `profileEvidence[]`。

禁止只写 `className` 或 `methodName`。混淆名称只是描述符中的一部分，必须与 APK 指纹绑定。

### 4.3 示例 Profile（示意，不是当前真实 Profile）

```json
{
  "schemaVersion": "1",
  "profileId": "sample-host-code100",
  "host": {
    "packageName": "example.host",
    "versionName": "1.0",
    "versionCode": 100,
    "signingCertSha256": "REPLACE_WITH_REAL_CERT_SHA256",
    "baseApkSha256": "REPLACE_WITH_REAL_APK_SHA256",
    "dexFingerprint": "REPLACE_WITH_REAL_DEX_FINGERPRINT"
  },
  "roles": [
    {
      "roleId": "message.submit",
      "status": "draft",
      "requiredEvidenceFamilies": [
        "HOST_IDENTITY",
        "CALL_GRAPH",
        "TYPE_SHAPE",
        "RUNTIME_BEHAVIOR"
      ],
      "candidateMethods": [
        {
          "owner": "Lx/y/Z;",
          "name": "a",
          "descriptor": "(Lx/y/Request;)Ljava/lang/Object;"
        }
      ],
      "negativeConstraints": [
        "NOT_UI_CLICK_ONLY",
        "NOT_LOGGING_ONLY"
      ],
      "runtimeTrigger": "one controlled test message submission",
      "expectedEventSchema": "MessageSubmitted.v1"
    }
  ]
}
```

示例中的 package、hash、descriptor 都是占位符，不可复制进生产 Profile。

## 5. Resolver 算法与安全门槛

按以下顺序执行，不允许跳步：

1. **宿主识别**：确认 package/process、版本、签名、APK/DEX 指纹和 ClassLoader。
2. **Profile 选择**：精确身份命中才加载精确 Profile；未知版本进入动态发现/诊断状态，不得套用近似版本全量映射。
3. **候选生成**：按角色锚点、类型关系、调用图和框架 API 搜索候选。
4. **证据归并**：去重、按独立证据族计数、保留来源、标记截断。
5. **负面筛选**：排除 UI-only、logger、通用网络库、第三方 SDK、错误分支、测试代码和不相关进程。
6. **结构验证**：精确 descriptor、参数/返回类型、父类/接口、调用邻域、CFG、数据流完整性。
7. **唯一性判断**：必须满足 role policy 和最小 winner margin；并列或分差不足则 Ambiguous。
8. **运行时验证**：只读观察目标操作，检查触发次数、线程、对象生命周期和非目标操作的误触发。
9. **安装授权**：身份、静态证据、运行时行为和策略全部满足后生成 HookPlan。
10. **安装后验证**：确认目标方法实际进入、原始行为未被破坏、事件桥接符合契约。

静态 E0–E3 等级只描述静态证据数量，不是概率、不授权 Hook。Points-to 若 `records_truncated=true` 或 `context_expansion_complete=false`，只可诊断。

### 5.1 Fail-closed 条件

以下任一条件成立时，目标 role 必须拒绝安装：
- HostIdentity 不完整或发生版本/签名/DEX 冲突；
- Profile 身份不匹配；
- 完整 descriptor 不匹配；
- 关键证据被截断或缺失；
- 证据族数量不满足 role policy；
- 负面证据命中；
- 多候选并列或 winner margin 不足；
- ClassLoader 无法解析目标类型；
- 运行时触发行为不符合预期；
- Hook Backend 不支持当前方法类型；
- Hook 安装状态不可确定。

Fail-closed 只禁用当前 role，不应停止其他互不依赖的 role。

## 6. Hook Backend 与生命周期

### 6.1 Backend API 职责

Backend 至少提供：
- 方法/构造器解析（按完整 descriptor）；
- Hook before/after/replace 能力声明；
- 安装句柄；
- 卸载/清理（如平台支持）；
- 平台异常映射；
- 运行时能力检测；
- 线程安全保证。

核心不得假设所有平台都支持 replace、constructor hook 或 unhook。

### 6.2 安装状态机

```text
DISCOVERED
  → VERIFIED
  → AUTHORIZED
  → INSTALLING
  → INSTALLED
  → OBSERVING
  → BRIDGED
  → TESTED

任何阶段失败：
  → ROLE_DISABLED / RETRYABLE_FAILURE / PERMANENT_REJECTION
```

状态必须按 `process + hostFingerprint + roleId + fullMethodDescriptor` 隔离。不能使用单个全局 AtomicBoolean 表示所有 Hook 已安装。

### 6.3 幂等与并发

- 同一幂等键只允许一次有效安装。
- 并发请求必须合并到同一安装任务。
- lifecycle 重入不得重复注册。
- 安装失败必须记录失败原因和重试策略。
- 不可重试错误（身份冲突、descriptor mismatch）不得自动重试。
- 可重试错误（临时 ClassLoader 尚未就绪）必须有次数/退避上限。
- 单个 role 失败不能污染其他 role 状态。
- 进程重启后不得复用旧进程的 ClassLoader 或 Hook handle。

## 7. Feature Adapter 与 EventBridge

### 7.1 责任

Feature Adapter 把版本特有的宿主方法、DTO 和回调转成稳定业务事件。混淆 DTO 不得泄漏到 SDK 或消费者项目。

EventBridge 负责：
- schema version；
- 事件序号与会话关联（若证据支持）；
- 线程切换；
- 取消/完成/错误语义；
- 隐私过滤；
- 背压和缓冲上限；
- 事件去重；
- 消费者断开后的清理。

### 7.2 事件契约最低要求

事件至少包含：
- eventType；
- schemaVersion；
- hostFingerprintId；
- roleId；
- processSessionId；
- monotonicSequence；
- occurredAt；
- payload（仅非敏感、已规范化字段）；
- sourceEvidenceId（可追溯来源）。

禁止包含 prompt 原文、消息正文、附件内容、Authorization、Cookie、API key、PoW challenge、salt、nonce。

### 7.3 Agent / Tool 特别约束

Agent 工具能力必须分开验证：
1. 工具描述/注册；
2. 工具选择；
3. 调用参数生成；
4. 本地执行器触发；
5. 权限/策略校验；
6. 结果回填；
7. Agent 继续推理；
8. 结束/失败/取消。

只发现服务端 ToolOpen/ToolFind/Search 结果模型，不足以证明本地工具执行。任何工具执行必须走项目自己的授权策略，不可由 Hook Engine 绕过权限。

## 8. 跨项目接入步骤

### 8.1 第一步：Apps 发布稳定 SDK

Apps 先完成：
- 模型/API 和 Profile schema；
- Resolver/Verifier；
- HookCoordinator；
- HookBackend API；
- FakeHookBackend；
- 版本化 SDK；
- 示例 Host Adapter；
- 兼容性测试；
- 最小可运行 sample。

没有稳定 SDK 前，不让其他项目各自猜接口。

### 8.2 第二步：Deekseep-Custom 作为首个真实后端

职责：
- 实现 LSPosed Backend；
- 只针对 `com.deepseek.chat` 目标包；
- 读取 Apps SDK；
- 先接入 HostIdentity 与 observer；
- 再接 request.route / stream.flow / sse.dispatch 等经过证据验证的 role；
- 先只读 observer，再桥接；
- 对 2.7.1/code287、2.7.2/code289、2.7.4/code294、2.7.5/code295 分别验证；
- 2.7.3 输入当前被隔离，禁止当作可信 2.7.3 回归样本；
- 每个版本分别出具设备测试报告。

注意：现有 2.7.2 日志中的 `ly1`、`zn3.o`、`jw3.g`、`y60.b` 只能作为对应构建的线索，不能硬编码为跨版本通用实现。

### 8.3 第三步：Deepseek-Harness 适配

- 复用 HostIdentity、SemanticResolver、Profile schema 和 EventBridge。
- 按自身运行架构实现 Backend；不强制使用 LSPosed。
- Agent loop、工具执行和 Local API 仍由 Harness 自己负责。
- Apps 只提供安全的宿主语义事件和稳定接口。

### 8.4 第四步：OmniRouter 与非 Android 项目

OmniRouter 只消费 SDK 产生的标准 API/事件或 Gateway 协议；不依赖 DEX、ClassLoader、LSPosed。若没有 Android Hook 需求，不引入 runtime-core。

### 8.5 依赖分发

开发阶段可用 Git Submodule 或 Git 引用锁定 commit；稳定后优先发布 Maven artifact（JAR/AAR）。每个消费者必须锁定 SDK 版本，不得浮动依赖 main/latest。Profile Pack 独立版本化，且必须与 SDK schema 兼容。

## 9. 测试与验收矩阵

### 9.1 JVM 单元/属性测试

- 证据族去重；
- 正/负证据优先级；
- winner margin；
- descriptor exact match；
- profile identity mismatch；
- 未知版本；
- 截断索引；
- 多候选歧义；
- role policy；
- Coordinator 幂等；
- 并发安装；
- lifecycle 重入；
- 局部失败隔离；
- 重试/永久拒绝；
- 事件序号、去重、背压、取消；
- 隐私字段过滤。

### 9.2 Profile 测试

每个 Profile 必须验证：
- APK SHA 与 Manifest 身份；
- 所有 owner/class 存在；
- 完整 method descriptor 存在；
- superclass/interfaces；
- 必需字段/调用点；
- 负面约束；
- schema compatibility；
- 对应证据文件和审计 run 可追溯。

### 9.3 Android/LSPosed 设备测试

每个版本至少测试：
- 冷启动与宿主识别；
- profile 选择；
- Hook 安装与重复 lifecycle；
- 普通消息请求；
- SSE 首事件、Delta、finish；
- 非 2xx 错误；
- 取消；
- 断线恢复；
- 并发会话；
- 目标功能之外的负向触发；
- 模块/Hook 异常时宿主原生功能仍可用；
- 无敏感内容写入日志。

### 9.4 盲测

开发者不得提前向 Resolver 暴露留出 APK 的人工 Profile。报告：
- 自动定位成功率；
- 正确拒绝率；
- 歧义率；
- 误 Hook 率；
- 漏检率；
- 人工介入时间；
- 各角色/版本状态。

误 Hook 率必须优先于覆盖率；宁可拒绝，不可错误 Hook。

## 10. 功能域完成矩阵

所有角色逐版本登记，不能只给项目一个总百分比。

| 功能域 | 最低角色集合 | 关键闭环 |
|---|---|---|
| Host/Runtime | host.fingerprint、runtime.lifecycle、classloader.ready | 正确识别进程/版本，未知身份拒绝 |
| Conversation | conversation.create/switch/delete、message.submit/edit/retry/continue/cancel/history | 用户动作到领域事件完整闭合 |
| Prompt | prompt.default、prompt.custom、prompt.agent、context.assemble、prompt.serialize | 来源/优先级/开关正确，不记录正文 |
| Agent | agent.plan、agent.step、agent.tool.dispatch、agent.tool.result、agent.terminate | 规划→工具→结果→继续推理→终止 |
| Tools | tool.registry、tool.invoke、tool.permission、tool.result | 必须证明本地执行，不以 DTO 代替 |
| Network | request.route、transport.dispatch、transport.response | 请求/响应对象关联且不改写原生行为 |
| Stream/SSE | stream.flow、sse.parse、sse.dispatch、session.resume、session.cancel | 首事件、Delta、finish、cancel、resume |
| Serializer | serializer.request、serializer.response、protocol.mapping | 输入输出模型和多态注册关系 |
| Multimodal | image/file/audio/video 仅按 APK 实际能力登记 | 媒体元数据链闭合，不采集媒体正文 |
| Search/Web | search.query、web.result、citation.source | 查询与结果模型可追溯 |
| Storage/Sync | storage.read/write、sync.state、migration | 配置/会话持久化与迁移可验证 |
| Settings/UI | settings.read/write、ui.navigation、ui.state | 配置源到状态更新，不只 Hook 点击 |
| Local API | local_api.server/route/auth/models/chat/stream/cancel/lan | 归属模块侧；路由、鉴权、流、取消、并发和 LAN 独立测试 |
| Policy/Privacy | policy.guard、privacy.redaction、diagnostic.export | 权限门不绕过，日志脱敏 |
| Observability | telemetry.lifecycle、diagnostic.hook_state | 诊断可复核且不泄露正文 |

每个 role 使用状态：
`NOT_STARTED` → `DISCOVERED` → `STATIC_CONFIRMED` → `SIMULATED_CONFIRMED` → `RUNTIME_CONFIRMED` → `BRIDGED` → `TESTED`。
允许 `REJECTED`、`UNSUPPORTED`、`N/A`，并必须记录理由。

## 11. 当前证据基线与明确阻断项

### 11.1 可信版本

| 标签 | Manifest versionName | versionCode | 状态 |
|---|---:|---:|---|
| 2.7.1 | 2.7.1 | 287 | trusted |
| 2.7.2 | 2.7.2 | 289 | trusted |
| 2.7.3 标签输入 | 2.5.2 | 273 | quarantined，不是可信 2.7.3 |
| 2.7.4 | 2.7.4 | 294 | trusted |
| 2.7.5 | 2.7.5 | 295 | trusted |

### 11.2 绝不能误读的事实

- 五版本静态矩阵 #203 的五个任务和 aggregate 成功；这不是设备 Hook 测试。
- 静态报告的 `candidate_runtime_confirmed_count=0`、`candidate_hook_authorized_count=0`。
- Points-to 仍可能 `records_truncated=true`、`context_expansion_complete=false`，只能诊断。
- PR #2 最新 HEAD 的 workflows 曾为 `action_required`；必须重新检查当前 HEAD 的实际状态。
- `dsprobe.log` 记录 2.7.2/code289-cn 宿主误选 2.7.1 mapping，随后 unmapped class lookup 失败；Apps 仓库的日志分析不代表探针源码已经修复。
- 2.7.2 动态类名不允许跨版本复用。
- 任何 Agent 本地执行闭环尚未被 ToolOpen/ToolFind/Search 结果片段证明。

### 11.3 先决 blocker

1. 对当前 PR HEAD 重新运行/审批并验证 Python 与 Kotlin CI。
2. 取得真实 2.7.3 APK，或明确将其保持 quarantined。
3. 将 Semantic Core 从原型整理成可发布模块，确定公开 API 和 schema。
4. 实现 FakeHookBackend 和完整 Coordinator 状态机测试。
5. 实现 Android Runtime / ClassLoader resolver。
6. 在 Deekseep-Custom 实现 LSPosed Backend 并做真机只读观察。
7. 逐角色接入并验证，不得一开始打开所有功能域。
8. 发布 SDK 与 Profile Pack，其他项目再接入。

## 12. 版本化与兼容性规则

- SDK 使用语义化版本；破坏性 API 改动提升 major。
- Profile schema 独立版本化；读取器必须拒绝不支持的 major schema。
- Profile Pack 声明最低/最高 SDK schema 兼容区间。
- 每个消费项目锁定 SDK 和 Profile Pack 版本。
- 运行时报告包含 engineVersion、sdkVersion、profileRevision、hostFingerprintId。
- 兼容性测试必须验证旧 Profile 在新 SDK 上的解析结果。
- 不能把 profile 自动下载/更新设计成任意远程代码执行；Profile 只能是受 schema 校验的数据，不得包含可执行脚本。

## 13. 交付清单（Definition of Done）

Apps Core 阶段完成：
- [ ] 模块依赖方向符合第 2.1 节。
- [ ] SDK API、Profile schema、版本策略定稿。
- [ ] Resolver 所有拒绝路径有测试。
- [ ] HookCoordinator 幂等/并发/重入/失败隔离测试通过。
- [ ] FakeHookBackend 全部契约测试通过。
- [ ] 示例 Host Adapter 可运行。
- [ ] 发布 JAR/AAR 与迁移文档。
- [ ] 当前 HEAD CI 全绿，且无 required check 被跳过。

首个 Android Backend 阶段完成：
- [ ] Android HostIdentity 获取和校验。
- [ ] 精确 descriptor 反射解析。
- [ ] LSPosed Backend before/after hook。
- [ ] 安装句柄、异常隔离、幂等和生命周期。
- [ ] 至少一个 role 完成真机只读触发验证。
- [ ] 至少一个事件完成 Bridge 和端到端回归。

跨项目接入阶段完成：
- [ ] Deekseep-Custom 不再维护重复 Resolver。
- [ ] Harness 使用同一 SDK contract，但保留自身 Backend。
- [ ] OmniRouter 只依赖标准协议，不引入 Android 依赖。
- [ ] 所有项目锁定同一兼容 SDK 版本。
- [ ] 跨仓库 CI 对 SDK/API 变更有兼容性检查。

## 14. 交付纪律

接手 AI 必须：
- 先审计现有代码和 Git 历史，再决定新增/修改；
- 不得重写已经存在且通过测试的模块；
- 不得只增加文档而宣称运行时功能已完成；
- 不得只增加接口空壳而宣称 Resolver/Backend 已实现；
- 不得静默降级版本或忽略 Profile 身份冲突；
- 不得把静态证据写成运行时证据；
- 不得删除失败测试来制造 CI 通过；
- 每个提交记录修改文件、测试命令、结果和未解决风险；
- 任何跨仓库改动先建立依赖合同，再分仓提交；
- 不合并 main，除非项目所有者明确要求。

每轮交付报告固定包含：
1. 基线 HEAD/branch；
2. 修改文件清单；
3. 新增/变更 API；
4. 测试与 Actions run URL；
5. 版本/功能覆盖；
6. 已知失败和未验证项；
7. 下一步唯一阻断项；
8. 是否需要设备验证。

---
本文件与 SDK 合同、AI 执行任务书共同构成跨项目交接包。若三者冲突，以更严格的安全门槛和当前代码证据为准，并先更新文档再改代码。
