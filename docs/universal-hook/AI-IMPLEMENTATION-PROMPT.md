# 给其他 AI 的工程执行任务书：Apps Universal Hook Core

你接手的是 GitHub 仓库 `qingjian0/apps`。你的目标不是写一份方案，而是把该仓库逐步实现为可被多个项目依赖的通用 Hook 引擎核心，并提供稳定 SDK，使 Deekseep-Custom、Deepseek-Harness-Local-Android 等项目只需实现自己的 Adapter。

## A. 开工前必须做

1. 读取根 README、`docs/universal-hook/IMPLEMENTATION-HANDBOOK.md`、`SDK-CONTRACT.md`、`ENGINE-ARCHITECTURE.md` 和最新最终审计报告。
2. 检查当前分支、HEAD、所有未合并 PR、Actions 最新状态、Gradle 模块、源码、测试和现有 API。
3. 把文档中的“目标结构/示意 API”与真实代码逐项对照，列出已存在、部分存在、缺失、冲突四类。
4. 不要重新审计已完成的 APK 静态产物；只在实现改动影响审计器或 Profile schema 时重新跑相关审计。
5. 不要在没有证据的情况下写“完成”“通过”“通杀”“真机验证成功”。

## B. 总体架构（必须遵守）

- Apps 是通用核心唯一源码。
- 核心算法不得依赖 Android/Xposed/LSPosed。
- Hook 平台能力通过 HookBackend 抽象注入。
- 各项目仅实现 HostIdentityProvider、HookBackend、FeatureAdapter 和事件消费者。
- Profile 是绑定 APK/签名/DEX 指纹的纯数据，不允许含可执行脚本。
- Resolver 解析、运行时验证、授权、安装是四个不同阶段。
- 静态候选永远不能直接授权 Hook。
- 未知版本、身份冲突、候选歧义、描述符不符、证据截断必须 fail-closed。
- 单个 role 失败不能使整个模块崩溃，也不能阻止独立 role。
- 不允许把 prompt、消息正文、附件内容、凭据、Cookie、API key、PoW challenge、salt、nonce 写入日志。

## C. 实施优先级（按序完成，不要跳过）

### P0：稳定现有核心，不破坏已完成审计
- 梳理现有 Kotlin Semantic Core 的 package/API/依赖。
- 把模型、Resolver、Coordinator、Backend 抽象的依赖边界画清楚。
- 补齐单元测试，保证当前安全门槛。
- 修正最新 HEAD CI 的 action_required/未运行问题（只能按 GitHub 正常审批/工作流权限解决，不得伪造绿灯或移除必要检查）。
- 所有变更保持兼容或提供 migration。

### P1：公开模型与 Profile Schema
- 实现 HostIdentity、MethodDescriptor、Evidence、Candidate、ResolveResult、RuntimeVerificationResult、AuthorizedHookPlan、HookKey、HookStatus、NormalizedHookEvent。
- Profile JSON schema 加版本、宿主指纹、角色策略、完整 descriptor、正负证据、来源和状态。
- Profile validator 校验 APK hash、Manifest、签名、DEX 指纹、class/method descriptor、父类/接口、必要字段。
- 未知 schema major、hash mismatch、descriptor mismatch 均拒绝加载。

### P2：Resolver 和 CandidateVerifier
- 候选生成与证据归并分离。
- 证据族去重，不允许同源重复命中增加多样性。
- role-specific required evidence families。
- 负面证据优先于正面分数。
- winner margin 不足、多候选、索引截断时返回 Ambiguous/Rejected。
- Points-to 不完整时仅诊断，不进入强 DATA_FLOW 证据。
- 产生可审计 ResolveReport，包括接受和拒绝原因。

### P3：Runtime Core 与 HookCoordinator
- 实现 per-role 状态机。
- 幂等键必须包含 process + host fingerprint + roleId + full descriptor。
- 并发安装合并，lifecycle 重入去重。
- 可重试/不可重试错误分类。
- 单 role 失败隔离。
- 只有不可伪造的 AuthorizedHookPlan 可安装；resolve 不能副作用安装。

### P4：FakeHookBackend 和 Sample Consumer
- JVM FakeHookBackend 完成全部 backend contract tests。
- 提供 sample host adapter。
- 验证 before/after/constructor 等平台能力差异。
- 验证卸载、进程销毁、异常隔离、事件映射、背压和取消。
- 给出一条端到端模拟链路：HostIdentity → Profile → Resolve → Runtime Verify → Authorize → Fake Install → Normalized Event。

### P5：Android Runtime 与 LSPosed Backend
- 仅在核心抽象稳定后开发。
- Android 侧获取 package/version/signature/base+split APK hash/DEX fingerprint/process/ClassLoader。
- 精确解析完整 descriptor。
- LSPosed Backend 只在独立模块中依赖平台 API。
- Deekseep-Custom 作为首个真实消费者。
- 先只读 observer；未设备验证不开放修改参数/返回值的 Hook。
- 目标版本逐一验证，不允许用 2.7.2 的混淆类名映射其他版本。

### P6：SDK 发布与跨项目接入
- 发布 versioned JAR/AAR 和 Profile Pack。
- sample consumer 与至少一个真实消费者编译。
- Deekseep-Custom 移除重复 Resolver，改为 SDK + LSPosed Adapter。
- Deepseek-Harness 复用 SDK contract，使用自己的 Backend。
- OmniRouter 仅消费标准 API/事件，不引入 Android Hook 依赖。
- 每个项目锁定版本，跨仓库 CI 检查兼容性。

## D. DeepSeek 特殊证据限制（必须保留）

当前可信宿主版本身份：
- 2.7.1 / code287
- 2.7.2 / code289
- 2.7.4 / code294
- 2.7.5 / code295

标签为 2.7.3 的现有 APK Manifest 实际为 2.5.2 / code273，必须 quarantine，不能当作可信 2.7.3 样本。

2.7.2 动态 observer 线索：
- `ly1 implements wu1`
- `zn3.o(wu1, Long) -> y60`
- `jw3.g(wu1, Long) -> y60`
- `y60.b(fl4, yb3) -> Object`
这些只属于该日志对应构建。必须对每个 APK 重新核对完整 descriptor、类型结构、调用边和运行时行为，不得跨版本照抄。

旧探针日志说明：
- 宿主识别为 2.7.2/code289-cn；
- 安装器误选 2.7.1 full mode / code257 profile；
- unmapped `mf6` 进入 ClassLoader 后 ClassNotFoundException；
- lifecycle 重入导致重复失败。
正确修复是身份/Profile 路由、unmapped guard、feature 隔离和幂等安装，不是随便补类名。

当前静态产物中 runtime-confirmed 与 hook-authorized 均为 0。五版本 Matrix 成功只证明静态审计任务完成，不证明设备 Hook。

## E. 验收标准

每个阶段完成时必须同时交付：
1. 源码和公开 API；
2. 对应单元/契约/集成测试；
3. 当前 HEAD 对应 CI run URL 和结论；
4. 修改前后模块图/依赖方向；
5. Profile schema 示例及校验结果；
6. 各版本、各 role 的状态矩阵；
7. 失败路径和 fail-closed 测试；
8. 明确的未完成项和设备验证需求。

最终 Apps Core 验收：
- JVM 核心独立编译；
- FakeHookBackend 全契约测试通过；
- Sample Consumer 编译通过；
- Resolver/Coordinator 的负向和并发测试通过；
- Profile schema 有版本兼容测试；
- 最新 HEAD 所有 required CI 成功；
- SDK JAR/AAR 可被外部项目引用；
- 文档、示例、迁移指南与实现一致。

最终 Android Backend 验收：
- Android 构建成功；
- LSPosed Backend 在目标设备可安装；
- 至少一个目标 role 在对应宿主版本真实触发；
- 未知版本/歧义候选拒绝安装；
- 重复 lifecycle 不重复安装；
- 原生宿主行为不被破坏；
- 日志无敏感正文。

## F. 工程执行纪律

- 以批量、并行方式处理互不依赖的测试/文档/模块，但共享文件写入必须串行。
- 不为追求速度跳过编译、测试或安全门禁。
- 不创建重复项目、不把同一 Resolver 同时放在多个仓库。
- 不改写稳定分支；先在专用 feature branch 提交。
- 不自动合并 PR，除非仓库所有者明确授权。
- 不用伪造 profile、假设备日志或 mock 结果冒充真机。
- 每个 commit 使用清晰 Conventional Commit 风格。
- 每轮最后提供简洁交接，指出下一项唯一阻断任务。

**第一条执行指令：完成现状差异审计后，直接开始 P0/P1 的真实代码工作；不要停在重复规划或反复询问确认。**
