# Universal Hook SDK：跨仓库接口合同

> 状态：规范草案（Contract Draft）。本文件用于约束 Apps Core 与消费者项目的公开边界；不是对当前代码已存在接口的声明。具体 Kotlin API 必须经过实现、编译、契约测试后才能标记为 Stable。

## 1. 设计目标

SDK 让消费者项目只表达“我要哪个语义能力”，不再关心宿主混淆类名、调用图算法或 Hook 安装细节。

消费者项目允许：
- 提供宿主身份环境；
- 提供平台 HookBackend；
- 注册 FeatureAdapter；
- 订阅稳定事件；
- 提交受控的运行时验证场景。

消费者项目不允许：
- 直接调用内部 Resolver 私有算法；
- 自行复制 Profile 选择逻辑；
- 根据混淆类名自行 fallback；
- 将静态候选当作可安装 Hook；
- 将宿主 DTO 暴露到 API/Agent 层。

## 2. 公开接口分层

### 2.1 Identity API

职责：读取并规范化当前宿主身份。

概念接口：

```kotlin
interface HostIdentityProvider {
    fun identify(): HostIdentityResult
}

sealed interface HostIdentityResult {
    data class Identified(val identity: HostIdentity) : HostIdentityResult
    data class Incomplete(val partial: HostIdentity, val missing: Set<IdentityField>) : HostIdentityResult
    data class Unsupported(val reason: String) : HostIdentityResult
}
```

身份必须包含包名、versionName/versionCode、签名摘要、APK/split 摘要、DEX 指纹、进程名和 ClassLoader 进程内标识。敏感用户数据不得进入 HostIdentity。

### 2.2 Resolution API

```kotlin
interface SemanticHookEngine {
    fun resolve(request: ResolveRequest): ResolveResult
    fun verify(request: RuntimeVerificationRequest): RuntimeVerificationResult
    fun install(plan: AuthorizedHookPlan): InstallResult
    fun status(key: HookKey): HookStatus
    fun disable(key: HookKey, reason: DisableReason)
}
```

约束：
- `resolve` 只负责静态/配置候选解析，不应隐式安装。
- `verify` 只执行只读行为验证。
- 只有独立授权阶段产生的 `AuthorizedHookPlan` 可传入 `install`。
- API 类型系统应尽量阻止把普通 ResolveResult 强转为 AuthorizedHookPlan。
- 任何缺失身份、证据、运行时行为或策略结果都不能自动授权。

### 2.3 Backend API

```kotlin
interface HookBackend {
    val capabilities: Set<HookCapability>
    fun resolveMethod(identity: HostIdentity, descriptor: MethodDescriptor): BackendMethodResult
    fun install(plan: BackendHookPlan): BackendInstallResult
    fun uninstall(handle: HookHandle): BackendUninstallResult
}
```

Backend 负责平台差异，不负责语义判断。平台不支持某种 Hook 类型时必须返回明确 Unsupported，不得模拟成功。

### 2.4 Feature Adapter API

```kotlin
interface FeatureAdapter {
    val roleId: RoleId
    fun validate(host: HostIdentity, resolved: ResolvedRole): AdapterValidation
    fun mapEvent(raw: BackendInvocation): NormalizedEventResult
}
```

Adapter 只处理本项目/本宿主版本的 DTO 和事件映射；不得读取或修改 Resolver 内部置信度。

### 2.5 Event API

```kotlin
interface HookEventSubscriber {
    fun onEvent(event: NormalizedHookEvent)
    fun onError(error: HookRuntimeError)
}
```

事件需包含 schema version、roleId、host fingerprint、process session、单调序号、时间戳和脱敏 payload。事件 payload 不允许携带 prompt/message body、凭据、Cookie、API key、挑战原文、salt 或 nonce。

## 3. 核心类型语义

| 类型 | 含义 | 禁止行为 |
|---|---|---|
| HostIdentity | 已识别的宿主身份 | 不完整身份冒充精确版本 |
| MethodDescriptor | owner + name + 完整 JVM/Dex descriptor | 只用类名/方法名查找 |
| Evidence | 带来源、证据族、完整性和正负极性的证据 | 重复字符串虚增独立证据 |
| ResolveResult | 解析结果，不代表 Hook 授权 | 自动安装 |
| RuntimeVerificationResult | 目标设备行为观察结果 | 静态推断伪装成运行时 |
| AuthorizedHookPlan | 已通过身份、证据、行为和策略门槛的不可变计划 | 从候选手工构造绕过门槛 |
| HookHandle | Backend 安装句柄 | 跨进程/跨 ClassLoader 复用 |
| HookStatus | 单 role 安装状态 | 全局布尔值代替角色状态 |
| NormalizedHookEvent | 平台无关稳定事件 | 泄漏宿主混淆 DTO |

## 4. 错误模型

错误必须可分类、可测试：

- `UNSUPPORTED_HOST`
- `IDENTITY_INCOMPLETE`
- `IDENTITY_MISMATCH`
- `PROFILE_NOT_FOUND`
- `PROFILE_SCHEMA_UNSUPPORTED`
- `PROFILE_INTEGRITY_FAILED`
- `CANDIDATE_NOT_FOUND`
- `CANDIDATE_AMBIGUOUS`
- `EVIDENCE_INCOMPLETE`
- `NEGATIVE_EVIDENCE_MATCHED`
- `DESCRIPTOR_MISMATCH`
- `CLASSLOADER_RESOLUTION_FAILED`
- `BACKEND_CAPABILITY_UNSUPPORTED`
- `INSTALL_FAILED`
- `INSTALL_STATE_UNKNOWN`
- `RUNTIME_BEHAVIOR_MISMATCH`
- `ADAPTER_VALIDATION_FAILED`
- `EVENT_MAPPING_FAILED`

错误必须包含 roleId、hostFingerprintId、阶段、是否可重试和脱敏诊断。不得记录原始方法参数值或消息正文。

## 5. 线程与生命周期合同

- 所有公开 API 明确线程模型。
- Android ClassLoader 和反射对象只能在对应进程使用。
- Hook 安装是并发安全操作；相同 HookKey 合并。
- 安装回调不得阻塞主线程。
- EventBridge 必须有有界缓冲和背压策略。
- 消费者取消订阅后释放引用。
- 进程死亡后清理所有 runtime handle。
- 重试有上限，身份冲突和 descriptor mismatch 永不自动重试。

## 6. SDK 兼容策略

- 公开 API 标记 Experimental / Stable / Deprecated。
- 0.x 可快速迭代，但必须发布明确 migration note。
- 1.0 后遵循 SemVer。
- Profile schema 独立版本化。
- 每个 Profile Pack 声明支持的 SDK API/schema 范围。
- 消费项目锁定明确版本，不允许依赖动态 latest。
- 不把任意代码或脚本放入 Profile Pack；Profile 是受 schema 校验的数据。

## 7. 契约测试

SDK 发布前必须有以下契约测试：
- resolve 不会安装；
- 未授权 plan 不能传入 install；
- 版本身份冲突拒绝；
- 完整 descriptor 精确匹配；
- 多候选歧义拒绝；
- 静态候选不能产生 AuthorizedHookPlan；
- runtime verification 不完整时拒绝授权；
- backend capability 不支持时返回 Unsupported；
- 同一 HookKey 并发安装只安装一次；
- 不同 role 安装失败互不影响；
- lifecycle 重入不重复安装；
- event payload 隐私字段过滤；
- 消费者取消订阅释放资源；
- 旧 Profile schema 的兼容/拒绝行为明确。

---
在 SDK 实际实现并由 sample consumer 编译前，本文件中的接口一律保持 Contract Draft，不得作为已发布 API 引用。
