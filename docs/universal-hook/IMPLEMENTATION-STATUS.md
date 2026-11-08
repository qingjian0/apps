# Universal Hook Core：实现状态与交接记录

> 本文跟踪真实代码状态，不以目标架构或设计草案冒充已交付能力。更新时必须核对当前分支 HEAD、测试和 Actions。

## 当前开发增量

- 代码 PR：[#4 — Universal Hook identity and profile contracts](https://github.com/qingjian0/apps/pull/4)
- 开发分支：`work/universal-hook-core-p0p1`
- 基线：现有 `engine/semantic-core` Kotlin/JVM 模块；没有替换现有静态审计 ingestion、SemanticResolver 或 StaticProgramGraph。

## 已进入代码的能力（本 PR 范围）

| 能力 | 实现位置 | 当前边界 |
|---|---|---|
| 完整宿主身份模型 | `PublicContract.kt` | 接收身份数据；Android 采集器尚未实现 |
| APK / split / DEX 指纹绑定 | `HostIdentity`、`HookProfileValidator` | 进行严格相等校验；尚未从设备实时计算 |
| 完整 JVM 方法描述符 | `MethodDescriptor`、`Model.kt` | 校验 owner、方法名、参数和返回类型 |
| 可审计证据封装 | `AuditableEvidence` | 包含来源、证据族、正负极性、强度和完整性；真实采集器仍待接入 |
| Profile 领域模型 | `HookProfile`、`SemanticRoleProfile` | 纯数据模型 |
| Profile 校验器 | `HookProfileValidator` | schema major、宿主身份、版本、哈希、角色和 descriptor fail-closed |
| Profile JSON Codec | `HookProfileJsonCodec.kt` | 严格解析与领域校验；不执行 Profile 内容 |
| Profile JSON Schema v1 | `schemas/universal-hook-profile-v1.schema.json` | 数据格式合同 |
| Hook 授权门 | `HookAuthorizationPolicy` | 必须 Runtime-Verified Profile、精确角色/方法、完整正向宿主与运行时证据 |
| 授权计划 | `AuthorizedHookPlan` | 构造器 module-internal；普通静态 Resolution 不能直接生成 |
| 公共安装入口 | `HookCoordinator.install(AuthorizedHookPlan)` | 外部消费者只使用授权计划；旧 Resolution 安装路径降为 internal 迁移/测试路径 |

## 本增量的安全不变量

1. `versionName` 或 `versionCode` 单独匹配不够；必须匹配签名、base APK、split APK 和 DEX 指纹。
2. Profile 的 schema major 不支持、身份不匹配、状态为 QUARANTINED/DEPRECATED、方法 descriptor 不合法时拒绝。
3. 静态解析只得到 `Resolution`，不能直接传给外部安装 API。
4. Hook 授权要求 Profile 状态为 `RUNTIME_VERIFIED`，并要求 HOST_IDENTITY、RUNTIME_BEHAVIOR 证据及 Profile 要求的证据族。
5. 运行时证据必须绑定当前 base APK、当前 role、当前完整方法 descriptor 和非空设备运行记录 ID。
6. 证据不完整或存在负向证据时拒绝授权。
7. Profile 是数据，不含脚本或可执行代码。

## 测试覆盖

新增/扩展测试覆盖：
- SHA-256 身份完整性和 split APK 摘要；
- JVM 方法 descriptor 语法与参数/返回类型一致性；
- 精确版本和 APK 身份匹配；
- schema major、QUARANTINED 状态、重复角色、空候选和非法 descriptor；
- JSON 正常解析、错误 JSON、未知枚举、未知 schema；
- 静态解析不能授权安装；
- Profile 未达到 RUNTIME_VERIFIED 不能授权；
- 运行时证据必须绑定精确方法；
- Profile 声明的证据族必须满足；
- AuthorizedHookPlan 安装和幂等。

**CI 状态必须以 PR #4 当前 HEAD 对应的最新 Actions run 为准。** 中间提交的失败/取消运行不能替代最终 HEAD 的验证结果。

## 尚未实现（不能宣称已完成）

- Android `HostIdentityProvider`：从 PackageManager、签名、base/split APK、DEX、进程和 ClassLoader 获取真实身份。
- 真实静态证据源与证据完整性签名/校验；当前 `AuditableEvidence` 是领域合同。
- Runtime Observer / Runtime Verification Collector：设备端受控场景采集与基线对照。
- LSPosed/Xposed `HookBackend` 实现。
- Fake Backend 完整契约测试与 sample consumer。
- Maven/AAR/JAR 发布、SDK 版本兼容和跨仓库 CI。
- Deekseep-Custom、Deepseek-Harness 的实际 SDK 接入和真机验证。

## 下一阶段顺序

1. 完成本 PR 当前 HEAD 的编译与测试，并修复所有失败。
2. 为证据和授权 API 增加 Fake Backend / 完整契约测试。
3. 实现 Android HostIdentityProvider 和只读 Runtime Observer。
4. 在 Deekseep-Custom 实现 LSPosed Backend，先完成一个 role 的真机观察闭环。
5. 逐个角色、逐个宿主版本验证，再发布 SDK。
