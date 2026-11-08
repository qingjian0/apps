# DeepSeek APK / 运行链路分析归档

> 本仓库用于保存 DeepSeek Android APK、运行探针日志及其逆向分析记录。当前分析目标限定为 **DeepSeek 官方 Android 宿主应用**，重点是版本识别、Agent 请求构造、网络传输、流式 continuation/callback 链，以及可用于后续 Hook 的稳定边界。
>
> **证据等级约定**
> - **日志直接证实**：日志中存在明确的类名、方法签名、调用栈或事件计数。
> - **强推断**：由多个调用栈和对象关系共同支持，但尚未通过 APK 静态反编译确认语义。
> - **未确认**：当前日志没有足够证据，不得写成已定位。
>
> 本文是基于当前仓库文件与日志的分析归档，不把混淆类名臆测成业务语义，也不把未检查的 APK 二进制说成已完成反编译。

## 新一代 Runtime Semantic Hook Engine

本项目的最终方向升级为跨版本运行时语义 Hook 引擎，不再以固定混淆类名/方法名映射作为通用性基础。工程设计和验收要求见 [引擎架构文档](docs/universal-hook/ENGINE-ARCHITECTURE.md)。

当前已在本分支新增独立 Kotlin/JVM Semantic Core 原型（GitHub Actions 编译与单元测试已通过）：
- 宿主指纹约束（仅允许目标包名进入 Hook 解析）；
- 多证据族聚合，重复字符串不能虚增置信度；
- 候选歧义、证据不足、负面证据时 fail-closed；
- 角色级幂等 HookCoordinator 和可注入 HookBackend；
- 独立 GitHub Actions 单元测试工作流。
- 新增 StaticProgramGraph：接入真实调用边、跨方法字段读写关联、控制流结构摘要、父类继承与接口实现关系；候选锚点按全宿主索引稀有度加权。
- 五版本静态审计已全部通过（Run `42345954380`，五个版本任务与 aggregate 成功）；生成完整 DEX/类/方法/调用边/字段/控制流索引及跨版本报告，见 [五版本详细审计记录](docs/universal-hook/五版本静态审计与语义解析记录-2026-11-07.md) 和 `audit/universal-hook/`。
- 首轮 Resolver 的静态候选存在误判：2.7.3 把第三方验证 SDK 误认为宿主 Local API，2.7.5 的会话候选胜出分差仅约 0.355。已移除宿主 APK 的 Local API 映射、将默认胜出分差提高至 0.5，并要求 HookCoordinator 同时具备完整运行时宿主身份和运行行为证据。
- 以上是静态审计与语义核心进展，不代表已完成 LSPosed Hook；最新安装门槛和回归测试以本轮 Semantic Core CI 为准。
- Resolver 已进一步增加四证据族门槛、框架/第三方 SDK 负面证据、稀有锚点沿调用图/字段流传播，以及按功能域定义的必需证据族；语义引擎改动会自动触发五版本重新接入。
- 2026-11-08 修复 Points-to 全局存储预算竞争：调用上下文和接收者记录按 root 平分预算；单个 root 超额只标记该 root 不完整，不再因记录存储上限提前停止后续图遍历。新增 Python 回归覆盖热点 root 与独立 root 的隔离；以最新 CI 结果为准。
- 旧五版本产物均触及 200,000 条记录上限，不能作为完整 Points-to 结果。旧产物另显示 `deepseek 273.apk` 的 Manifest 为 versionName `2.5.2` / versionCode `273`，与矩阵标签 2.7.3 不一致；在替换或确认 APK 身份前，不把它计为已验证的 2.7.3 版本证据。
- Hook 候选现输出 E0–E3 静态证据等级与证据族；等级不代表设备运行时确认，也不授权 Hook。运行时确认与 Hook 授权字段在静态审计产物中始终为 false，避免将字符串命中或静态候选误报为已验证 Hook。

**当前限制：** 这是引擎核心原型，不是已完成的 DEX 自动语义发现器，也没有接入 LSPosed Android Backend。Agent、提示词、本地 API 等全功能域已列入覆盖目标，但必须逐域完成静态证据、运行时验证、桥接和回归测试后才能标记完成。详情：[全功能覆盖矩阵](docs/universal-hook/README.md) · [Kotlin Semantic Core](engine/semantic-core/)。

## 1. 仓库材料盘点

本仓库当前保留五个宿主版本输入（2.7.1 APK、2.7.2 APK、2.7.3 APK、2.7.4 APKM、2.7.5 APK）、两份运行日志和一份 SSE/Hook 证据包。2.7.3 / 2.7.5 已有静态证据；2.7.1 / 2.7.4 纳入本轮统一重审。2.7.2 APK `deepseek-2-7-2.apk` 已上传，需与 code289-cn 动态日志核对构建身份。

| 文件 | 大小 | 本轮处理状态 |
|---|---:|---|
| deepseek271.apk | 22,006,745 bytes | 2.7.1 输入；本轮重新核对实际包身份和 DEX |
| deepseek-2-7-2.apk | 22,205,160 bytes | 2.7.2 新上传输入；与 code289-cn 动态日志交叉验证 |
| deepseek 273.apk | 14,211,169 bytes | 2.7.3；既有 JADX/Smali 结果，本轮重新统一扫描 |
| com.deepseek.chat_2.7.4-294_...apkm | 19,476,565 bytes | 2.7.4 / code294 分包容器；按内嵌 APK 组件逐个扫描 |
| DeepSeek_2.7.5.apk | 22,210,268 bytes | 2.7.5；既有 JADX/Smali 结果，本轮重新统一扫描 |
| deekseep_vision.log | 6,440,972 bytes / 19,747 行 | 动态 observer 大日志；统一汇总调用角色和方法标记 |
| dsprobe.log | 12,320 bytes / 50 行 | 2.7.2/code289-cn 版本误选 2.7.1/code257 映射及重复安装失败 |
| deepseek-sse-hook-evidence.zip | 329,086 bytes | 已有 SSE/Hook 证据包；本轮重新盘点条目和哈希 |

2.7.3 APK SHA-256：a6d025c14c98118a5a67849e04aaef6f3c9c13aaf0fa62caaee0e47091374ea3

2.7.5 APK SHA-256：ddc52ef868b991fd33e634de834a3e2c022b0cd7ff9e854f4f141996aaeadb70

静态审计产物包含：JADX 源码子集、第一方类/方法索引、关键词交叉引用、原生库清单、原生库 ZIP 和质量报告。完整产物由 GitHub Actions 保存，见第 16 节。

## 2. 核心结论

1. 2.7.2 动态日志已经证明请求、Continuation 和 Callback 存在可观测调用链，但它们属于 2.7.2 / code289-cn，不能直接当作 2.7.5 的类名映射。
2. 2.7.5 静态源码已确认网络请求路由、请求序列化、PoW 挑战与响应、SSE 事件分派，以及工具结果片段的数据模型。
3. 2.7.5 聊天主链路可以追到消息提交、网络请求构造、Flow 返回、SSE 收集、增量消息更新和断线自动恢复。
4. PoW 的 Java 调用和 JNI 入口已经确认；原生库使用 Rust SHA3/Keccak 相关实现，但由于库被剥离，精确哈希变体、输入拼接和难度判定条件仍未完全还原。
5. 2.7.5 存在 ToolOpen、ToolFind、Search 等服务端消息片段模型；当前证据支持“客户端接收并渲染结构化工具结果”，不支持“客户端本地执行完整 Agent 工具”的结论。
6. allow_parallel_streams 和 interrupt_and_send_enabled 会进入发送策略判定；它们不是单纯 UI 开关。
7. 当前静态分析不是设备运行验证。2.7.5 的真实 Hook 触发、请求头实际值、SSE 断线恢复时序仍需在目标设备上验证。

## 3. 运行时启动与 Hook 安装链

`dsprobe.log` 中可直接确认的启动事件顺序：

```text
模块加载
  ├─ native dual-root capture: ComposeView.setContent
  ├─ Activity font-scale Hook
  └─ module loaded (universal)
       package=com.deepseek.chat
       hostGeneration=2.7.2/code289-cn
          ↓
Cold start: license verified
          ↓
installAllFeatureHooks (authorized)
          ↓
选择 2.7.1 full mode via HostRemap (classes=7636)
          ├─ v271 page_show dispatcher 未找到
          │    └─ fallback: always-visible entry
          ├─ 2.7.2 navigation controller capture
          │    └─ class=p16
          └─ code257 agent tool-log Canvas renderer
               └─ ClassNotFoundException:
                  deekseep unmapped mf6
          ↓
installAllFeatureHooks failed
          ↓
lifecycle bootstrap 再次尝试安装
          ↓
activity lifecycle callbacks registered
          ↓
captured DeepSeek native root
  content=zy1
          ↓
后续 lifecycle / 多次安装重试
          └─ 同一 mf6 映射错误再次出现
```

### 3.1 版本路由异常

日志原文包含：

- `module loaded (universal), package=com.deepseek.chat, hostGeneration=2.7.2/code289-cn`
- `installAllFeatureHooks: 2.7.1 full mode via HostRemap classes=7636`
- `2.7.2/code289-cn navigation controller capture installed class=p16`
- `code257 agent tool-log Canvas renderer unavailable`
- `ClassNotFoundException: Didn't find class "deekseep unmapped mf6"`

这说明至少存在三个版本标识同时参与运行：

| 标识 | 日志所示含义 | 风险 |
|---|---|---|
| 2.7.2/code289-cn | 宿主实际识别结果 | 当前运行目标 |
| 2.7.1 full mode | 功能 Hook 所选配置 | 与宿主版本不一致 |
| code257 | Agent tool-log Canvas 相关映射标签 | 与 code289 宿主不匹配的可能性高 |

**判断：** 这不是单纯一个 Canvas View 找不到的问题。更可能是宿主 generation 检测结果、HostRemap 选择结果和功能 Hook 使用的映射版本没有统一。需要检查版本识别到 Hook 安装之间的配置传递，不能通过给 `mf6` 随便补一个类名来掩盖问题。

### 3.2 优先审计的模块边界

以下是根据日志暴露出的职责划分提出的源码审计目标，不代表这些源码文件已存在于本仓库：

- `HostGenerationDetector`：宿主包名、版本名、versionCode / code 标识识别。
- `HostProfileSelector`：将识别结果映射到唯一 Host Profile。
- `HostRemap`：类名、方法签名和版本映射表选择。
- `HookRegistry`：Hook 定义及其适用版本约束。
- `HookInstallCoordinator`：启动期与 Activity lifecycle 阶段的安装编排、去重和失败隔离。

建议版本选择以宿主实际包名 + versionCode + build/code 标识为联合键；不得在 code289 未命中时静默降级到 2.7.1 或 code257 的完整映射集。未知版本应进入明确的只读/诊断状态。

## 4. 请求构造调用链

`deekseep_vision.log` 中记录了 2 个请求构造器候选：

```java
ly1.<init>(
  int, String, Integer, String, List,
  boolean, boolean, String, boolean, String, String
)

ly1.<init>(
  String, Integer, String, ArrayList,
  boolean, boolean, String, boolean, String, String, int
)
```

本次实际触发的是第二个构造器，日志记录到 4 次构造事件。请求对象结构：

```text
ly1 implements wu1
fields:
  Companion : ky1
  a : String
  b : Integer
  c : String
  d : List
  e : boolean
  f : boolean
  g : String
  h : boolean
  i : String
  j : String
  k : String
  l : qh6[]
```

请求工厂候选：

- `mw1.y(Object) -> Object`
- `mw1.e(Object, Object, Object) -> Object`
- `jr2.y(Object) -> Object`
- `jr2.m(Object, Object, Object, Object) -> Object`
- `mr2.h(ys, ds2, nr2, String, long, boolean, xr, xr, xr, vy4, hy4, xy4, zb3) -> Object`

日志中的构造器调用栈为：

```text
mr2.h
  → jr2.m
    → jr2.y
      → mw1.e
        → mw1.y
          → ly1.<init>(...)
```

**Hook 优先级：**

1. `ly1.<init>`：确认请求对象字段赋值、构造器重载和请求参数来源。
2. `mr2.h / jr2.m / jr2.y / mw1.e / mw1.y`：逐层确认工厂职责，避免把任一候选直接认定为唯一入口。
3. `zn3.o`：作为请求对象进入传输层的首选观察点。

日志只记录了参数类型/对象形状，没有保存用户消息正文、凭据或完整请求体。当前不能仅凭字段名 `a-l` 为每个字段赋予业务含义。

## 5. 网络传输调用链

这是当前最明确、可直接用于后续 Hook 验证的链路：

```text
ly1 (implements wu1)
      │
      ▼
zn3.o(wu1, Long) -> y60
  role = transport-dispatch
      │ parent
      ▼
jw3.g(wu1, Long) -> y60
  role = transport-low-level
      │
      ▼
y60 (implements el4)
  fields: a:int, b:Object
  continuation method:
      y60.b(fl4, yb3) -> Object
```

日志明确记录：

- `zn3.o(wu1, java.lang.Long) -> y60` 是 transport-dispatch。
- `jw3.g(wu1, java.lang.Long) -> y60` 是 transport-low-level。
- `jw3.g` 的 parent 是 `zn3.o`。
- 两层收到的是同一个请求对象（`sameRequestObjectAsRoot=true`）。
- 两层都返回 `y60`。
- `y60` 实现 `el4`，并暴露 `b(fl4, yb3) -> Object`。

本次日志共记录 4 次请求构造和 4 次传输 dispatch / low-level 进入，均返回 `y60`。

### 5.1 Hook 入口建议

| 优先级 | 目标 | 用途 |
|---|---|---|
| P0 | `zn3.o(wu1, Long)` | 观察完整请求对象进入传输层；适合作为主请求入口 |
| P0 | `jw3.g(wu1, Long)` | 观察低层传输分发；用于确认是否发生二次封装/重试 |
| P0 | `y60.b(fl4, yb3)` | 观察响应/continuation 的异步回调入口 |
| P1 | `ly1.<init>` | 请求构造字段和构造器重载验证 |
| P1 | callback 实际类的目标方法 | 追踪 continuation 内部状态传递与终态 |

应先在只读 observer 模式验证调用次数、线程、对象身份和返回类型，再决定功能 Hook。不要在请求构造器或传输入口修改参数。

## 6. Continuation 与 callback 调用链

`y60.b(fl4, yb3) -> Object` 是当前响应链最重要的入口。日志显示它在不同线程上运行，包含 `main` 和 `DefaultDispatcher-worker-8`，并在调用过程中进入成对的 callback 对象。

观察到的典型结构：

```text
transport:
  zn3.o(wu1, Long)
    → jw3.g(wu1, Long)
      → y60

asynchronous continuation:
  y60.b(fl4, yb3)
    ├─ callback-0: concrete callback object
    │    └─ callback-0 method, commonly a(Object, yb3)
    └─ callback-1: concrete callback object
         ├─ q(Object, Object)
         ├─ w(yb3, Object)
         └─ y(Object)
```

日志中 callback 对象的接口/字段形状存在重复模式，例如：

- 一类对象实现 `vy4`，常见方法为 `q(Object,Object)`、`w(yb3,Object)`、`y(Object)`。
- 另一类 callback 对象通常暴露 `a(Object,yb3)`。
- `y60.b` 的参数对象形状随事件变化，不能把某一次的参数类当成固定响应 DTO。

### 6.1 已观测 callback 类

| Role | 类 |
|---|---|
| callback-0 | `cr9`, `ec0`, `r3`, `b5`, `qa`, `s5`, `kr1`, `k13`, `hm4` |
| callback-1 | `k41`, `mm4`, `il5`, `qj3`, `x0`, `f0`, `g0`, `je2`, `ir1`, `pg1`, `d0`, `jm4` |

以上分类来自 observer 的角色标记，不代表已确认每个类的业务语义。共观察到 21 个具体 callback 类；每个类只 Hook 其声明的方法，日志中的策略为 `concrete-class-declared-only`，单类扫描上限 `maxMethods=12`。

### 6.2 高频 callback 方法

| 方法 | 日志出现次数（enter/exit/throw 合计） |
|---|---:|
| `qj3.y(Object)` | 5,692 |
| `qa.a(Object, yb3)` | 2,136 |
| `qj3.w(yb3, Object)` | 1,858 |
| `qj3.q(Object, Object)` | 1,836 |
| `k13.a(Object, yb3)` | 1,150 |
| `cr9.a(Object, yb3)` | 1,132 |
| `qa.d(n88, yb3)` | 660 |
| `s5.a(Object, yb3)` | 556 |
| `hm4.a(Object, yb3)` | 458 |
| `b5.a(Object, yb3)` | 450 |
| `ir1.y(Object)` | 428 |
| `kr1.a(Object, yb3)` | 418 |
| `ir1.q(Object, Object)` | 412 |
| `ir1.w(yb3, Object)` | 412 |
| `pg1.y(Object)` | 332 |

这里的“出现次数”是 enter、exit、throw 三类事件总和，不等同于独立请求数或独立对象数。

## 7. Observer 运行统计与异常

`deekseep_vision.log` 覆盖时间：`02:37:11.549–02:38:55.863`，共 19,747 行。

| 事件 | 次数 |
|---|---:|
| 请求构造器进入 | 4 |
| transport-dispatch 进入 | 4 |
| transport-low-level 进入 | 4 |
| continuation 进入 | 129 |
| continuation 抛异常 | 42 |
| callback 类观察记录 | 21 |
| callback-enter | 9,578 |
| callback-exit | 8,634 |
| callback-throw | 944 |

callback-enter 与 callback-exit + callback-throw 数量相等，说明本次日志记录到的 9,578 个 callback 调用均有结束事件。

### 7.1 异常集中点

callback-throw 共 944 次，其中：

| 方法 | throw 次数 |
|---|---:|
| `qj3.y(Object)` | 771 |
| `pg1.y(Object)` | 72 |
| `x0.y(Object)` | 39 |
| `f0.y(Object)` | 35 |
| `il5.y(Object)` | 15 |
| 其他方法合计 | 12 |

另有 continuation-throw 42 次。日志里可见异常缩写如 `e06`、`ck7`、`us4`，但没有足够信息将这些混淆异常类型映射为业务错误。

**判断：** `qj3.y(Object)` 是异常最集中的 callback 方法，值得作为第一优先级分析对象。但不能仅凭异常次数断言它是错误根因：日志显示 callback 仍持续运行，必须进一步还原其调用条件、返回值语义和异常处理方。

### 7.2 DEX / 反射扫描异常

日志还记录：

- `dex.methodInventoryError.6649=java.lang.NoClassDefFoundError`
- `dex.methodInventoryError.7154=java.lang.NoClassDefFoundError`
- `manager.fieldInventoryError.8=java.lang.NoClassDefFoundError`

这些错误在日志中重复出现。它们说明探针的类/方法/字段清点并非全覆盖；不能把“未观察到”解释为“宿主不存在”。

## 8. 当前可以画出的调用链与不能画出的调用链

### 8.1 2.7.2 动态日志链

动态日志能够支持的调用链和统计仍见第 4～7、12～15 节。该链只描述日志对应的 2.7.2 / code289-cn 运行实例。

### 8.2 2.7.5 静态源码链

2.7.5 已确认以下链路：

~~~text
消息提交 gx1.b
  → rr2 会话/流编排
  → nw3.e 请求类型分派、路由选择和序列化
  → b70（实现 il4 / Flow）
  → gr2
  → pv1.j / pv1.l 收集流
  → ot1 事件收集器
  → pv1.a 按 SSE event 名称分派
  → pv1.e 等处理 DeltaCommand / 消息片段
  → iv1 记录 SSE 生命周期
  → rr2.h 执行自动恢复流
~~~

PoW 相关链路：

~~~text
nw3.c / ChatChallengeRequest
  → POST /api/v0/chat/create_pow_challenge
  → ServerChatChallenge
  → of2 预取/缓存管理
  → of2.k 按 algorithm 选择算法
  → PowCalculator JNI
  → lib/arm64-v8a/librscrypto.so
  → AuthedPowSolution
  → nw3.e 将 PoW 响应放入 X-DS-PoW-Response
~~~

### 8.3 当前仍不能下结论的部分

- 2.7.5 的 l5.z 与 ot1.z 是多用途协程状态机方法：l5 的 e=8 分支由 nw3.e 创建并用于请求执行路径；ot1 的 e=3 分支由 pv1.l 创建并用于 Flow 收集。它们不是原始 SSE 行解析器。原始 SSE 解析器已由 smali 确认为 vs1.z；2.7.3 对应解析器为 jz0.A。
- 原生 PoW 库已确认 JNI 导出符号、Rust SHA3/Keccak 相关依赖和 Keccak 计算路径；精确的 digest 变体、nonce 搜索条件和输入字节拼接仍需更深的原生反汇编。
- ToolOpen、ToolFind、Search 等片段的数据模型已确认；完整工具执行发生在服务端还是某个未识别的本地子系统，尚未被当前 APK 静态证据完全证明。
- 2.7.5 真实设备运行、Hook 可用性和请求/响应时序尚未验证。
- 2.7.3 APK 已完成同等级 JADX 与 smali 静态采集；跨版本语义映射见第 24 节。

## 9. 下一轮逆向与 Hook 验证顺序

### P0：版本隔离

- 每个 APK 独立生成类名、方法描述符、路由、序列化器和 Hook profile。
- 2.7.2 / code289-cn 的动态映射与 2.7.5 静态映射分开存储。
- 2.7.5 中同名类已出现不同语义；仅按混淆类名对齐会产生错误 Hook。

### P1：2.7.5 核心 Hook 验证点

优先在目标设备验证以下稳定语义边界，并在安装前解析完整方法描述符：

1. gx1.b：消息提交入口。
2. nw3.e：请求类型、路由、请求体序列化和 PoW 头附加。
3. of2.k：PoW 算法选择与计算入口。
4. oq1.c：Challenge / PoW 请求头组装。
5. pv1.a：SSE 事件分派。
6. pv1.j / pv1.l：SSE Flow 收集与异常出口。
7. rr2.h：自动恢复流编排。
8. gh2.h / fh2.b：并行发送、打断发送和发送阻断策略。
9. tz0：历史消息、停止流、挑战请求等辅助 API。

### P2：补足反编译失败

- 对 l5.z、ot1.z 及其他 JADX 失败方法做 DEX/smali 级别审计。
- 重点还原 HTTP response 到 il4 Flow 的转换、SSE 行解析、异常映射和取消传播。
- 不以伪代码或方法名推断替代实际指令证据。

### P3：原生 PoW

- 以 librscrypto.so 的 JNI 符号为入口继续分析 Rust 计算函数。
- 还原 challenge、salt、difficulty 到 nonce 的精确输入关系和判定条件。
- 在 arm64 设备上验证 nativeCalculateDeepSeekHashV1Pow 的输入输出和耗时。
- 为每个 ABI 单独验证库是否存在；本次 APK 仅发现 arm64-v8a 原生库。

### P4：Agent / 工具边界

- 继续追踪 ToolOpenFragment、ToolFindFragment、SearchFragment 的 SSE DeltaCommand 输入和 UI 渲染路径。
- 若要证明本地工具执行，必须找到本地执行器、权限/参数校验、工具调用结果回传链；当前仅有服务端工具结果片段模型，不能提前宣称本地 Agent 闭环。

## 10. 安全与日志采集约束

- 默认不记录用户消息正文、访问令牌、Cookie、Authorization header 或完整请求体。
- 优先记录类名、方法签名、参数类型、对象身份、线程、调用深度、耗时、返回类型和异常类型。
- 如需字段级分析，使用字段名、类型和长度等元信息；敏感字段值必须脱敏。
- 任何功能 Hook 先经过只读观察和版本匹配验证，不允许通过未知映射强行执行。
- 日志中的类名均为混淆符号；未经静态反编译确认，不得赋予业务名称。

## 11. 交付状态

| 项目 | 状态 | 证据边界 |
|---|---|---|
| 2.7.2 动态日志统计 | 已完成 | 日志计数、线程、异常和耗时统计已写入本 README |
| 2.7.5 DEX 提取与 JADX 源码采集 | 已完成（部分方法失败） | 3 个 DEX、13,940 个源文件；JADX exit code 3，仍有 344 项错误 |
| 2.7.5 第一方类/方法索引 | 已完成 | 12,596 个类、46,473 个方法签名、25,451 个字段签名 |
| 2.7.5 网络路由与请求模型 | 已完成静态审计 | 路由、请求体字段、Serializer 和 PoW header 已定位 |
| 2.7.5 SSE 事件分派 | 已完成静态审计 | event 名称、事件模型、Flow 收集和生命周期埋点已定位 |
| 2.7.5 PoW Java/JNI 链路 | 已完成静态审计 | JNI 导出符号与 arm64 原生库已定位 |
| PoW 原生算法细节 | 部分完成 | SHA3/Keccak 路径已识别，精确目标判定未完全还原 |
| Agent 工具结果片段 | 已完成静态审计 | ToolOpen / ToolFind / Search 等模型已定位 |
| 本地 Agent 工具执行闭环 | 未证实 | 未找到足以证明本地执行的完整调用链 |
| 2.7.5 设备运行验证 | 未完成 | 尚无本版本真实设备 Hook 运行记录 |
| 2.7.3 静态反编译与版本映射 | 已完成 | 3 个 DEX、12,319 个 Java 源文件、13,311 个 smali 文件；JADX 304 项错误 |

本轮没有把 JADX 的部分反编译结果包装成完整成功，也没有把静态调用链包装成设备运行验证。

## 分析记录元信息

- 主仓库：qingjian0/apps
- 文档分支：main
- 2.7.5 静态审计分支：work/deepseek-275-apk-audit
- 2.7.5 静态审计工作流：<https://github.com/qingjian0/apps/actions/runs/42335918440>
- 双版本审计分支：work/deepseek-version-comparison-audit
- 双版本审计工作流：<https://github.com/qingjian0/apps/actions/runs/42338674344>
- 审计工作流源码：<https://github.com/qingjian0/apps/blob/work/deepseek-275-apk-audit/.github/workflows/deepseek-275-apk-audit.yml>
- 审计工具：JADX 1.5.6，启用 show-bad-code
- 目标 APK：DeepSeek_2.7.5.apk
- APK SHA-256：ddc52ef868b991fd33e634de834a3e2c022b0cd7ff9e854f4f141996aaeadb70
- 工作流产物：decompiled-first-party.zip、first-party-class-index.json、cross-references.json、native-libraries.zip、native-library-index.md、report.md
- 质量状态：JADX exit code 3；344 项反编译错误；本 README 明确区分已确认与待还原部分。

## 12. 动态事件深挖：线程、异常、返回值与重试

本节是对原始日志逐行重新聚合后的补充统计。统计口径以 observer 事件行为准：`enter`、`exit`、`throw` 是独立日志记录，不可把记录总数直接当成业务请求数。

### 12.1 Continuation 事件闭合情况

| 事件 | 数量 |
|---|---:|
| `continuation-enter` | 129 |
| `continuation-exit` | 87 |
| `continuation-throw` | 42 |
| enter 与 exit + throw 是否闭合 | 是，129 = 87 + 42 |

continuation 的正常返回对象只有两类：

| 返回类型 | 次数 |
|---|---:|
| `cd3` | 71 |
| `zgb` | 16 |

continuation 异常类型：

| 异常类 | 次数 |
|---|---:|
| `us4` | 39 |
| `o` | 3 |

这表明 continuation 的返回结果呈现明显的两种对象形状，但在没有反编译 `cd3` / `zgb` 前，不把它们命名为成功、失败、完成或取消状态。

### 12.2 Callback 事件与角色分布

| 事件 | 数量 |
|---|---:|
| callback-enter | 9,578 |
| callback-exit | 8,634 |
| callback-throw | 944 |
| callback-enter 与结束事件是否闭合 | 是，9,578 = 8,634 + 944 |

按角色统计所有 callback 事件记录（enter + exit + throw）：

| 角色 | 事件记录 | throw |
|---|---:|---:|
| callback-0 | 7,074 | 3 |
| callback-1 | 12,082 | 941 |
| 合计 | 19,156 | 944 |

**关键判断：** 异常高度集中在 callback-1，而不是两个 callback 角色平均分布。后续需要重点分析 callback-1 的创建者、输入对象和状态转换路径；callback-0 可作为对照组。

### 12.3 Callback 异常类型分布

| 异常类 | 次数 |
|---|---:|
| `e06` | 839 |
| `us4` | 81 |
| `ck7` | 15 |
| `zt2` | 5 |
| `o` | 4 |
| 合计 | 944 |

异常类仍是混淆类型。此处只报告 observer 捕获到的类型标识，不推断其对应 HTTP 错误、解析错误、取消信号或业务异常。

### 12.4 异常最多的 Callback 方法

| 方法 | throw 次数 |
|---|---:|
| `qj3.y(java.lang.Object)` | 771 |
| `pg1.y(java.lang.Object)` | 72 |
| `x0.y(java.lang.Object)` | 39 |
| `f0.y(java.lang.Object)` | 35 |
| `il5.y(java.lang.Object)` | 15 |
| `ir1.y(java.lang.Object)` | 5 |
| `hm4.a(java.lang.Object,yb3)` | 3 |
| `je2.y(java.lang.Object)` | 1 |
| `d0.y(java.lang.Object)` | 1 |
| `k41.y(java.lang.Object)` | 1 |
| `f0.C(java.lang.Object)` | 1 |

`qj3.y` 的 771 次异常占全部 callback throw 的约 81.7%。这是优先反编译对象，但仍需区分：
- 输入数据不满足前置条件；
- 上游状态不完整或时序不满足；
- continuation 重入或重复回调；
- 正常控制流使用异常机制；
- observer 记录的异常是否被上层捕获并继续运行。

### 12.5 Callback 高频方法事件量

下表按同一方法的 enter + exit + throw 事件总数统计：

| 方法 | 事件记录 |
|---|---:|
| `qj3.y(Object)` | 5,692 |
| `qa.a(Object,yb3)` | 2,136 |
| `qj3.w(yb3,Object)` | 1,858 |
| `qj3.q(Object,Object)` | 1,836 |
| `k13.a(Object,yb3)` | 1,150 |
| `cr9.a(Object,yb3)` | 1,132 |
| `qa.d(n88,yb3)` | 660 |
| `s5.a(Object,yb3)` | 556 |
| `hm4.a(Object,yb3)` | 458 |
| `b5.a(Object,yb3)` | 450 |
| `ir1.y(Object)` | 428 |
| `kr1.a(Object,yb3)` | 418 |
| `ir1.q(Object,Object)` | 412 |
| `ir1.w(yb3,Object)` | 412 |
| `pg1.y(Object)` | 332 |

`qj3` 同时拥有 `q/w/y` 三个方法，符合一个多方法回调对象的形状；但其方法间调用关系、状态字段和输入/输出语义仍待静态分析。

### 12.6 线程分布与耗时

callback-enter 线程分布：

| 线程 | 次数 |
|---|---:|
| `main#2` | 9,055 |
| `DefaultDispatcher-worker-6#142` | 357 |
| `DefaultDispatcher-worker-3#103` | 65 |
| `DefaultDispatcher-worker-8#97` | 50 |
| `DefaultDispatcher-worker-7#140` | 20 |
| 其他 worker | 31 |

continuation-enter 线程分布：

| 线程 | 次数 |
|---|---:|
| `main#2` | 105 |
| `DefaultDispatcher-worker-6#142` | 10 |
| `DefaultDispatcher-worker-8#97` | 6 |
| `DefaultDispatcher-worker-3#103` | 4 |
| `DefaultDispatcher-worker-7#140` | 3 |
| `DefaultDispatcher-worker-2#69` | 1 |

callback 的耗时样本（exit + throw，共 9,578 条）：

| 统计量 | 耗时 |
|---|---:|
| 最小值 | 1 ms |
| 中位数 | 3 ms |
| P90 | 15 ms |
| 最大值 | 3,744 ms |

绝大多数 callback 很短，但存在最长 3.744 秒的调用。应把长尾样本单独提取，按 method、thread、receiverId、事件前后顺序关联，检查是否有锁等待、同步 I/O、阻塞调用或异常堆栈采集开销。当前日志不能证明是哪一种。

### 12.7 Callback 返回对象形状

callback-exit 的返回对象类型分布：

| 返回类型 | 次数 |
|---|---:|
| `cd3` | 4,688 |
| `zgb` | 2,597 |
| `qj3` | 929 |
| `ir1` | 206 |
| `pg1` | 94 |
| `f0` | 57 |
| `k41` | 22 |
| `il5` | 20 |
| `zs0` | 8 |
| `g0` | 6 |
| `d0` | 6 |
| `Boolean` | 1 |

这里的返回类型统计来自 observer 反射到的运行时对象形状。尤其 `cd3`、`zgb` 出现频率高，值得优先反编译其字段、静态常量、构造器和调用者，判断是否为状态/结果包装对象；目前不赋予业务名称。

### 12.8 Hook 安装失败是重复性问题

`dsprobe.log` 共 50 行，相关事件统计：

| 事件 | 次数 |
|---|---:|
| `installAllFeatureHooks` 安装尝试 | 10 |
| 安装失败 | 10 |
| `code257 ... Canvas renderer unavailable` | 10 |
| lifecycle callbacks 注册 | 1 |
| DeepSeek native root 捕获 | 1 |
| 2.7.2 navigation controller 捕获 | 1 |

10 次安装尝试全部出现相同的 `deekseep unmapped mf6` 类加载失败。这说明当前失败具有稳定可复现性，并且被多个启动/lifecycle 路径反复触发。

**需要区分两个问题：**
1. **映射错误**：code289 宿主为什么会选择 2.7.1 full mode / code257 Canvas 映射。
2. **安装幂等性**：同一 Hook 安装失败后，为什么后续 lifecycle 继续触发完整安装流程；安装器是否对已成功安装的 Hook 去重，是否能将单个可选 Hook 失败隔离。

不能只增加 `mf6` 的替代映射；应先修正 Profile 选择，再验证安装协调器的状态机。

## 13. 下一轮具体反编译任务单

### A. 版本识别与 Hook 安装器

- 保留未知版本只读策略。
- 将 2.7.2 / code289-cn 的动态映射与 2.7.5 静态映射分开存储。
- 审计 Hook 安装器的幂等性、失败隔离、生命周期重试和版本回退。
- 2.7.5 新 Hook 入口必须先通过 descriptor 匹配和真实设备探针验证。

### B. SSE 与网络执行器

- 已从 smali 还原 2.7.3 / 2.7.5 的 Ktor 响应处理、ByteReadChannel SSE 行解析、超时、事件封装和下游分派。
- l5.z / ot1.z 的职责已纠正：它们是请求执行与 Flow 收集的多用途协程状态机，不是 SSE parser。
- 剩余工作转为设备端验证：真实响应状态、心跳超时、取消传播和断线恢复时序。

### C. 原生 PoW

- 已静态追踪 JNI 导出、核心候选搜索函数和 Keccak-family 置换路径；2.7.3 / 2.7.5 的原生库二进制完全相同。
- 精确输入拼接、比较谓词和标准算法变体仍未完全证明。
- 设备端输入输出、耗时与真实服务端 challenge 验证仍待执行；不使用模拟值或伪造 PoW header。

### D. Agent / 工具数据流

- 追踪 DeltaCommand 的 h26 多态数据如何变成 ToolOpenFragment、ToolFindFragment、SearchFragment 和引用对象。
- 检查服务端返回片段的状态机：WIP、finished、no-result、failed。
- 只有找到本地执行器及其授权/回传闭环后，才将其标记为本地 Agent 工具能力。

### E. 2.7.3 对照审计

- 已完成 deepseek 273.apk 与 DeepSeek_2.7.5.apk 的并行 JADX / APKTool smali 审计。
- 已完成 API 路由、请求模型、SSE parser、事件分派、自动恢复、PoW 和原生库差异表，见第 24～26 节。
- 所有类映射均按语义、调用点和描述符建立，不按混淆类名猜测。

## 14. 自动验证与分析质量门槛

后续每次静态审计必须满足：

1. APK 文件名、大小、SHA-256 可复现。
2. DEX 数量、类数量和反编译源文件数量必须记录。
3. JADX 非零退出码必须记录；反编译失败的方法不得写成已还原。
4. 请求路由必须同时有 endpoint 字符串和请求构造调用点证据。
5. Serializer 必须由模型字段名和序列化器注册/调用点共同确认。
6. SSE 必须区分底层传输、事件解析、事件分派、UI 渲染和生命周期埋点。
7. PoW 必须区分挑战获取、算法选择、原生计算、答案封装、请求头附加。
8. Agent 工具必须区分服务端工具结果模型与本地执行器。
9. Hook 建议必须记录类、方法、完整描述符、版本范围、触发条件和失败关闭行为。
10. 静态审计与真实设备验证分开报告。

本轮自动采集结果：

| 指标 | 结果 |
|---|---:|
| DEX 数量 | 3 |
| JADX Java 源文件 | 13,940 |
| 第一方类索引 | 12,596 |
| 方法签名 | 46,473 |
| 字段签名 | 25,451 |
| 交叉引用关键词 | 55 |
| 原生库 | 16 |
| 原生库归档 | 9,126,084 bytes |
| JADX exit code | 3 |
| JADX errors | 344 |

## 15. 本轮结论修订

本轮将此前“网络协议、Serializer、SSE parser 和 Agent 工具链尚未被静态证实”的结论修订为：

- 网络请求路由、请求模型和主要 Serializer：已由 2.7.5 静态源码确认。
- SSE：已由 SseLifecycleContext、SseMessageRoot、事件分派方法和 Flow 收集链确认；底层两个复杂方法仍需 DEX 级补足。
- PoW：Java 到 JNI 的完整调用入口、挑战模型、答案模型、header 和 arm64 原生库已确认；算法内部只完成到 SHA3/Keccak 路径级别。
- Agent：服务端下发的 ToolOpen、ToolFind、Search 等结构化片段已确认；本地工具执行器未证实。
- 2.7.2 动态日志仍是独立证据集，不与 2.7.5 混淆类名直接合并。

## 16. DeepSeek 2.7.5 静态审计产物

本轮工作流与产物：

- GitHub Actions：<https://github.com/qingjian0/apps/actions/runs/42335918440>
- 工作流源码：<https://github.com/qingjian0/apps/blob/work/deepseek-275-apk-audit/.github/workflows/deepseek-275-apk-audit.yml>
- 目标文件：DeepSeek_2.7.5.apk
- APK SHA-256：ddc52ef868b991fd33e634de834a3e2c022b0cd7ff9e854f4f141996aaeadb70
- 产物保留期以 GitHub Actions 显示为准。

工作流启用 JADX 1.5.6 的 show-bad-code，并生成：
- 第一方 Java 源码子集；
- 第一方类/方法/字段索引；
- 关键词交叉引用；
- JADX 错误和质量报告；
- 原生库 ZIP；
- 原生库 ELF、符号和字符串清单。

注意：JADX exit code 为 3，报告 344 项错误。源码采集成功不等于所有方法均已还原；l5.z、ot1.z 等方法仍需 DEX/smali 级分析。

## 17. 2.7.5 网络请求与序列化调用链

### 17.1 主请求构造

nw3.e(yu1, Long) 根据请求对象类型选择路由和 PoW 数据，再通过 mdb Serializer、sg5 请求构造对象和 Ktor 执行链发起请求。该方法返回 b70；b70 实现 il4（Flow）接口，后续进入流处理链。

| 请求对象 | 路由 | PoW 数据来源 |
|---|---|---|
| qy1 / ChatFullCompletionRequest | POST /api/v0/chat/completion | qy1.k |
| rf2 / Regenerate request | POST /api/v0/chat/regenerate | rf2.f |
| jx1 / Continue request | POST /api/v0/chat/continue | jx1.d |
| rx1 / Edit request | POST /api/v0/chat/edit_message | rx1.i |
| yf2 / Resume request | POST /api/v0/chat/resume_stream | 此分支不附加该 PoW 字段 |

主请求的 HTTP method 由 cg5.c 提供；历史记录查询使用 cg5.b（GET）。

### 17.2 ChatFullCompletionRequest 字段

oy1 Serializer 对外序列化的字段包括：

- chat_session_id
- parent_message_id
- prompt
- ref_file_ids
- thinking_enabled
- search_enabled
- audio_id
- preempt
- model_type
- action
- shumei_device_id

模型内部的 qy1.k 不进入请求 JSON；nw3.e 单独读取它并写入 X-DS-PoW-Response。这是“请求体”和“PoW 请求头”分离的直接证据。

### 17.3 辅助 API

tz0 的协程分支还确认：

- POST /api/v0/chat/create_pow_challenge
- GET /api/v0/chat/history_messages
- POST /api/v0/chat/stop_stream
- /api/v0/call/config
- /api/v0/call/update

history_messages 的查询构造包含 chat_session_id、scenario、cache_version 和 cache_reset_at 等参数。

## 18. PoW 挑战、答案封装与原生库

### 18.1 Java 层调用链

~~~text
ChatChallengeRequest（wt1）
  → /api/v0/chat/create_pow_challenge
  → ChatChallengeResponseBizData（zt1）
  → ServerChatChallenge（ts9）
  → of2.j / of2.k
  → PowCalculator
  → nativeCalculateDeepSeekHashV1Pow
  → AuthedPowSolution（hf0）
  → X-DS-PoW-Response
~~~

ServerChatChallenge 的 Serializer 字段包括 algorithm、challenge、salt、signature、difficulty、expire_at、expire_after、target_path。

当 algorithm 为 DeepSeekHashV1 时，of2.k 调用 PowCalculator.a(difficulty, challenge, salt)。PowCalculator 将结果作为 long 返回；Java 层将 nonce 转成字符串并封装进 AuthedPowSolution。该模型包含 algorithm、challenge、salt、signature、answer、target_path 和有效期。

of2 继承通用预取管理器 ik0：
- pow_prefetch 控制是否启用预取；
- pow_prefetch_count 控制预取数量；
- 预取管理器以 10 秒周期调度补充；
- 生成的 PoW 方案在 expire_after 基础上提前 20 秒失效，避免临界过期。

### 18.2 两类 Challenge Header 不可混淆

- X-DS-PoW-Response：PoW 算法计算所得的 AuthedPowSolution。
- X-DS-Challenge-Response：ChallengeResponse 验证数据，字段包括 provider、challenge_id、shumei_verification、shumei_device_id、hcaptcha_token。

oq1.c 负责把 Challenge / PoW 数据放入请求头。两种 Header 不是同一种挑战，也不能用空字符串或伪造值替代。

### 18.3 原生实现证据与边界

APK 中存在 lib/arm64-v8a/librscrypto.so，导出 JNI 符号：

Java_com_deepseek_crypto_PowCalculator_nativeCalculateDeepSeekHashV1Pow

原生库字符串包含 Rust sha3c 与 keccak crate 的源码路径和 KECCAK_F_ROUND_COUNT 相关信息；AArch64 反汇编也能看到 Keccak 状态/轮函数路径（包含 0x88 字节状态/速率相关操作）。JNI 符号位于 0x18e40，函数长度 484 bytes；librscrypto.so SHA-256 为 4571b9bcf08d5f070a47a495bdcd4c77f4a088feee560ed11701ca93c7b56053。该库没有可用的完整 DWARF 调试信息，精确 SHA3 变体、nonce 搜索条件和难度判定尚未完全恢复。

本次 APK 的 16 个 .so 均位于 arm64-v8a；不能据此宣称其他 ABI 也具备相同 JNI 实现。

## 19. 2.7.5 SSE 流式响应与自动恢复

### 19.1 数据流

~~~text
nw3.e
  → b70（il4 / Flow）
  → rr2.d
  → gr2
  → pv1.j
  → pv1.l
  → ot1 收集器
  → pv1.a(event envelope)
  → pv1.e(DeltaCommand / fragment)
  → UI 消息状态
~~~

gx1.b 是消息提交编排入口；rr2 负责流编排和自动恢复。方法元数据将 rr2.h 标记为 executeAutoResumeStreamFlow。pv1 使用 iv1 记录 SSE 生命周期。

### 19.2 已确认的 SSE event 分派

| event | 数据模型 / 处理 |
|---|---|
| ready | ChatCompletionReadyEventData；含 request_message_id、response_message_id、model_type、request_content |
| finish / 默认增量事件 | DeltaCommand；含 p、o、v，交给片段增量处理 |
| toast | ChatCompletionToastEventData |
| hint | ChatCompletionHintEventData |
| title | ChatCompletionTitleEventData |
| update_session | ChatCompletionUpdateSessionEventData |
| update_file | AppChatFile |
| update_parent_message | ChatCompletionUpdateParentMessageEventData |
| close | ChatCompletionCloseEventData |
| check_client_update | ChatCompletionCheckClientUpdateEventData |
| auto_tts_capability | ChatCompletionAutoTtsCapabilityEventData |

SSE envelope 由 bia 表示，包含事件名称和数据内容。DeltaCommand 的多态数据进入消息片段处理流程。

### 19.3 生命周期与异常

iv1 记录 sse_request、sse_created、sse_ready、sse_first_delta、sse_finished、sse_disconnected、sse_auto_resume 等生命周期节点。pv1.l 对取消、连接异常和业务异常分别处理；rr2.h 承担自动恢复流编排。

smali 级分析已补齐底层 SSE 字节/行读取。2.7.5 的 vs1.z 才是原始解析器；ot1.z 是 pv1.l 使用的 Flow collector 状态机，l5.z 的 e=8 分支则由 nw3.e 创建用于请求执行。2.7.3 对应链为 e0(e=1) → jz0(e=0) → g5(e=5) → ix / k11.a。

## 20. Agent / 工具片段：已确认的数据模型与未确认的执行端

2.7.5 的消息片段模型中存在：

- ToolOpenFragment：包含状态、内容、结果、引用和 stage_id。
- ToolFindFragment：包含状态、查找 pattern、内容、引用和 stage_id。
- SearchFragment：包含状态、results、queries、content 和 stage_id。
- 还存在 ToolOpenFragmentReference、ToolFindFragmentReference、ToolSearchFragmentReference 等引用模型。
- 消息片段集合还包含 Response、Think、Search、ReadLink、Tip 等类型。

这些模型由 SSE DeltaCommand 进入客户端消息片段更新链，UI 对 WIP、finished、no-result、failed 等状态进行展示。

当前没有找到标准 OpenAI tool_calls / function_call 请求 schema，也没有找到足以证明 Android 本地执行完整工具调用的 ToolExecutor。当前最稳妥结论是：服务端返回结构化工具执行过程/结果片段，Android 负责接收、合并和渲染；本地工具执行闭环尚未证实。

另外，/api/v0/call/start 的 TrtcCallStartBizData 中也有 agent 字段，但它属于实时语音通话业务模型，不应被误判为通用 Agent 工具执行器。

## 21. 并行流与打断发送策略

allow_parallel_streams 和 interrupt_and_send_enabled 会进入 fh2.b 的发送模式判定，并由 gh2.h 与聊天输入 UI 使用。

- 并行流启用时，存在流任务的情况下可走并行发送分支。
- interrupt_and_send_enabled 控制打断当前流后发送的分支。
- 其他状态会被阻断或提示，不是简单地把按钮设为可点击。
- 具体模式整数在 UI 层被转换成发送/提示状态；Hook 时应拦截策略边界，而不是直接伪造开关值。

sse_auto_scroll_one_screen_v2 是流式消息滚动体验配置，不是 SSE 协议本身的证据；SSE 已由 pv1 / iv1 的事件分派和生命周期代码独立确认。

## 22. 2.7.2 与 2.7.5 的类名隔离规则

2.7.2 动态日志中的混淆名在 2.7.5 APK 中出现同名类，但语义明显不同。例如：

- 2.7.5 的 jw3 是 Android ID 辅助类，不是 2.7.2 日志中的传输候选。
- 2.7.5 的 qj3 与 ActivityOptions 相关，不是 2.7.2 中高频 callback 异常方法 qj3.y。
- 2.7.5 的 mr2 是自动恢复流的协程包装类；mw1 是 gx1.b 消息提交的协程状态机。
- 2.7.5 的 zn3 是空接口，y60 是另一处协程 continuation。

因此跨版本对齐必须基于完整描述符、接口/父类、调用点、字符串常量和动态行为共同确认，不能只按混淆类名映射。

## 23. SSE 底层字节流与行解析：DEX/smali 已还原

本节依据两版 APK 的 APKTool smali，而不是仅依赖 JADX 生成的 Java 伪代码。

### 23.1 2.7.5 真实传输解析链

~~~text
nw3.e(yu1, Long)
  → b70（Flow wrapper）
  → Ktor request execution
  → g0.z（synthetic coroutine branch e=1，HTTP response handler）
  → vs1.z（branch e=0，SSE parser）
  → Ktor ByteReadChannel（kw0）
  → qp0（line-read coroutine）
  → bia(eventName, data)
  → t5.a（branch e=7）
  → ev1(bia)
  → r3.c(fv1)
  → DeltaCommand / named-event dispatch
~~~

响应处理器 g0 的成功分支从响应头读取 x-ds-sse-heartbeat-timeout-secs，创建 cv1 心跳/连接状态事件，再创建 vs1(e=0) 解析 Flow，通过 b70 与 t5(e=7) 收集并把 bia 转换成 ev1。

非成功响应分支会读取响应体、解析结构化错误对象并包装为 dv1(gt9)，不会把错误响应当作正常 SSE Delta。

### 23.2 2.7.3 对应链

~~~text
hx2.g(u01, Long)
  → z40（Flow wrapper）
  → e0.A（synthetic coroutine branch e=1，HTTP response handler）
  → jz0.A（branch e=0，SSE parser）
  → Ktor ByteReadChannel（zq0）
  → fl0（line-read coroutine）
  → gw8(eventName, data)
  → g5.a（branch e=5）
  → a11(gw8)
  → ix
  → k11.a(k11, gw8, Continuation)
  → DeltaCommand / named-event dispatch
~~~

2.7.3 的成功响应分支创建 y01 心跳/连接状态事件、jz0(e=0) 解析 Flow 和 g5(e=5) 适配器；错误响应分支生成结构化错误结果。

### 23.3 SSE 行解析规则

| 解析职责 | 2.7.3 | 2.7.5 |
|---|---|---|
| Parser coroutine | jz0.A，e=0 | vs1.z，e=0 |
| Ktor ByteReadChannel 类型 | zq0 | kw0 |
| 行读取协程 | fl0 | qp0 |
| timeout wrapper | p75.P | m07.R |
| 事件数据对象 | gw8 | bia |
| 下游事件包装 | a11 | ev1 |
| 连接/心跳事件 | y01 | cv1 |
| 错误响应包装 | z01 | dv1(gt9) |

解析步骤：

1. 从 Ktor response body 获取 ByteReadChannel。
2. 读取 x-ds-sse-heartbeat-timeout-secs，按十进制解析；缺失或无法解析时默认 10 秒。
3. 将秒数乘以 1000，作为每次异步读取行的超时。
4. 在协程仍 active 且 channel 未关闭时持续读取。
5. 行以 event: 开头时，保存事件名。
6. 行以 data: 开头时，立即构造事件名/数据对象并发送到下游，然后清空当前事件名。
7. 正常结束或异常退出时关闭 ByteReadChannel。

**协议实现边界：**
- 解析器明确处理 event: 与 data: 两种行。
- 未发现 id:、retry: 的处理。
- 未发现多行 data: 合并；每条 data: 行会立即触发一次下游发送。
- 未发现注释行处理逻辑，非 event/data 行会被忽略。
- 两版 DEX 均未发现 text/event-stream 或 readUTF8Line 字面量；行读取通过混淆后的 Ktor ByteReadChannel helper 完成。
- 这说明它是面向当前服务端格式的定制解析路径，不应宣称完整覆盖 SSE 标准的所有字段和多行规则。

### 23.4 事件分派

2.7.3 的 k11.a 接收 gw8；2.7.5 的 r3.c 接收 fv1，其中 ev1 包装 bia，cv1 表示心跳/连接状态。

两版均能确认：
- event name 为 null：进入 DeltaCommand 默认增量路径。
- ready：解析 ChatCompletionReadyEventData。
- finish：处理完成事件。
- toast、hint、title。
- update_session、update_file、update_parent_message。
- close、check_client_update、auto_tts_capability。

因此，SSE 数据通路已经从 HTTP response、ByteReadChannel、行解析、事件封装追踪到业务事件分派。剩余的主要缺口是设备端时序验证，而不是静态 parser 入口未知。

## 24. DeepSeek 2.7.3 与 2.7.5 跨版本语义映射

### 24.1 APK 与反编译规模

| 指标 | 2.7.3 | 2.7.5 |
|---|---:|---:|
| APK | deepseek 273.apk | DeepSeek_2.7.5.apk |
| APK bytes | 14,211,169 | 22,210,268 |
| APK SHA-256 | a6d025c14c98118a5a67849e04aaef6f3c9c13aaf0fa62caaee0e47091374ea3 | ddc52ef868b991fd33e634de834a3e2c022b0cd7ff9e854f4f141996aaeadb70 |
| DEX 数量 | 3 | 3 |
| JADX Java 文件 | 12,319 | 13,940 |
| APKTool smali 文件 | 13,311 | 15,364 |
| JADX exit code | 3 | 3 |
| JADX errors | 304 | 344 |
| 原生库数量 | 11 | 16 |

JADX 两版均以 exit code 3 结束，但源码输出和 smali 反汇编均成功。JADX 错误方法必须继续以 smali 为准，不能把生成的 Java 错误 stub 当作真实实现。

### 24.2 关键调用角色映射

| 角色 | 2.7.3 | 2.7.5 |
|---|---|---|
| 请求路由/序列化入口 | hx2.g(u01, Long) → z40 | nw3.e(yu1, Long) → b70 |
| HTTP response handler | e0.A，e=1 | g0.z，e=1 |
| SSE parser | jz0.A，e=0 | vs1.z，e=0 |
| SSE adapter | g5.a，e=5 | t5.a，e=7 |
| SSE event dispatcher | k11.a(k11, gw8, Continuation) | r3.c(fv1, Continuation) |
| Auto-resume | qu1.h | rr2.h |
| SSE lifecycle telemetry | e11.f(lr8) | iv1.c(fda) |
| PoW algorithm selector | ap9.c(n88, Continuation) | of2.k(ts9, Continuation) |

Auto-resume 两版均在 DEX 中包含 executeAutoResumeStreamFlow 的 Kotlin 函数元数据签名；类名和协程状态机类型不同，但语义入口可以对应。

### 24.3 API 与协议变化

两版均能确认以下请求路由：
- POST /api/v0/chat/completion
- POST /api/v0/chat/regenerate
- POST /api/v0/chat/continue
- POST /api/v0/chat/edit_message
- POST /api/v0/chat/resume_stream
- POST /api/v0/chat/create_pow_challenge
- POST /api/v0/chat/stop_stream
- GET /api/v0/chat/history_messages

两版主请求路由均会在存在 PoW 响应时附加 X-DS-PoW-Response。

**2.7.5 新增/变化的挑战头证据：**
- 2.7.3 的全部 smali 中未找到 X-DS-Challenge-Response。
- 2.7.5 在 oq1.c ChallengePlugin 中同时设置 X-DS-Challenge-Response 与 X-DS-PoW-Response。
- 2.7.5 还出现 X-Debug-Recaptcha-Challenge 等相关 header 路径。
- 这证明 2.7.5 的挑战请求头体系发生变化；不能把 2.7.3 的挑战 header 行为直接套用到 2.7.5。

### 24.4 原生库差异

- 2.7.3 有 11 个 arm64-v8a 原生库；2.7.5 有 16 个。
- 2.7.5 新增 libimage_processing_util_jni.so、libliteavsdk.so、libsurface_util_jni.so、libtxffmpeg.so、libtxsoundtouch.so。
- libEncryptorP.so、libapminsighta.so、libapminsightb.so、libsmsdk.so 在相同路径下发生变化。
- 两版均没有移除旧路径原生库。
- 两版 librscrypto.so 都是 336,568 bytes，SHA-256 完全相同：4571b9bcf08d5f070a47a495bdcd4c77f4a088feee560ed11701ca93c7b56053。

### 24.5 混淆类名不能跨版本直连

实际发现同名类在两个版本中承担完全不同职责：

- 2.7.3 的 vs1 是 ChatSessionUpdateTitleResponseBizData Serializer；2.7.5 的 vs1 是 SSE ByteReadChannel parser。
- 2.7.3 的 nw3 不是请求路由类；2.7.5 的 nw3.e 是请求路由/序列化入口。
- 2.7.3 的 rr2 是 lock-free queue；2.7.5 的 rr2.h 是 executeAutoResumeStreamFlow。
- 2.7.5 的 l5 与 ot1 也不能仅凭方法名 z 认定为 parser 或 transport；必须先确认合成协程实例的 e 分支和创建点。

跨版本映射必须基于完整描述符、接口、调用点、函数元数据、协议字符串和行为共同确认。

## 25. PoW 原生算法：两版二进制一致，内部路径进一步收敛

### 25.1 跨版本一致性

2.7.3 与 2.7.5 的 PowCalculator Java native API 相同：

~~~java
nativeCalculateDeepSeekHashV1Pow(String base, String challenge, long difficulty)
~~~

两版 APK 的 librscrypto.so：
- 大小：336,568 bytes
- SHA-256：4571b9bcf08d5f070a47a495bdcd4c77f4a088feee560ed11701ca93c7b56053

因此 PoW 的 native binary 没有随 2.7.3 → 2.7.5 改变；差异主要在 Java 层 Challenge/PoW 方案封装和 header 管理。

### 25.2 AArch64 反汇编观察

- JNI export：Java_com_deepseek_crypto_PowCalculator_nativeCalculateDeepSeekHashV1Pow
- JNI symbol offset：0x18e40
- 符号长度：484 bytes
- JNI wrapper 调用内部候选计算路径，核心 helper 位于 0x19bc0。
- 置换 helper 位于 0x1a7e8，操作 25 个 64-bit lane 的 Keccak-family 状态。
- 可见 0x88（136 bytes）块/rate 处理、候选计数器格式化和 32-byte 比较路径。
- 内部置换调用使用参数 23；在没有完全恢复其参数语义前，不把它直接命名为标准 SHA3-256 或标准 Keccak-256。

### 25.3 仍未证明的细节

- challenge 与 salt 的精确输入拼接顺序。
- 候选计数器在 preimage 中的精确编码和位置。
- 32-byte 比较究竟是完整相等、前缀比较还是中间转换后的判定。
- difficulty 的准确数值语义及最大搜索边界。
- 设备端真实输入输出与服务端验证结果。

当前结论是 Keccak-family PoW 候选搜索路径已识别，不能宣称精确算法公式已完全还原。

## 26. 双版本自动审计与证据产物

### 26.1 自动化工作流

- 主分支：main（已纳入仓库，后续 APK 或工作流文件变更会触发）
- 开发验证分支：work/deepseek-version-comparison-audit
- 工作流：<https://github.com/qingjian0/apps/blob/main/.github/workflows/deepseek-version-comparison.yml>
- 工作流采用 matrix 并行审计 2.7.3 / 2.7.5，再合并生成比较报告。
- 每个版本分别生成 APK SHA-256、DEX inventory、JADX 源码、APKTool smali、symbol hits、native library hash。
- 自动验证要求 smali 数量非零、JSON 可解析、报告和 smali archive 非空。
- 产物保留期 14 天。

### 26.2 本轮证据包

- 主分支自动审计运行和产物：<https://github.com/qingjian0/apps/actions/runs/42339059934>
- 目标 APK 与摘要见第 24 节。
- 精简的 SSE/Hook/PoW 关键类证据包：deepseek-sse-hook-evidence.zip（本轮交付附件）。
- 完整 smali archive 包含 2.7.3 的 13,311 个和 2.7.5 的 15,364 个 smali 文件。

### 26.3 最终验证边界

- 双版本静态采集和跨版本语义映射：已完成。
- SSE ByteReadChannel 行解析与事件分派静态链：已完成。
- PoW JNI/native binary 对比：已完成到置换/候选路径级别。
- 精确 PoW 数学公式：未完成。
- 真实设备 Hook 安装、触发、网络时序和断线恢复：未完成。
- Agent 本地工具执行闭环：仍未证实。

本轮交付是可复核的静态证据，不代表目标设备上所有 Hook 已经可用。


## 27. 2.7.3 / 2.7.5 版本化 Hook Profile

以下入口由静态 DEX/smali 证据建立。它们是 Hook 候选，不代表已经在 LSPosed 设备上验证成功。

| 语义入口 | 2.7.3 | 2.7.5 | 建议 |
|---|---|---|---|
| 请求路由/序列化 | hx2.g(u01, Long) → z40 | nw3.e(yu1, Long) → b70 | P1；观察请求对象类型、路由和 Serializer 选择 |
| HTTP response handler | e0.A，实例分支 e=1 | g0.z，实例分支 e=1 | P2；只观察状态码、响应类别和分支 |
| SSE 行解析 | jz0.A，实例分支 e=0 | vs1.z，实例分支 e=0 | P3；只观察 event/data 行边界与耗时，不记录正文 |
| SSE event adapter | g5.a，分支 e=5 | t5.a，分支 e=7 | P3；一般不作为首选 Hook |
| 业务事件分派 | k11.a(k11, gw8, Continuation) | r3.c(fv1, Continuation) | P1；观察事件类型和状态迁移 |
| Auto-resume | qu1.h | rr2.h | P2；观察重试触发、结束原因和重复事件 |
| SSE lifecycle | e11.f(lr8) | iv1.c(fda) | P2；用于生命周期闭合与重复事件检测 |
| PoW 方案选择 | ap9.c(n88, Continuation) | of2.k(ts9, Continuation) | P2；观察算法分支，不修改结果 |
| Challenge header | 未发现同名 header 实现 | oq1.c，ChallengePlugin | 仅 2.7.5；观察 header 是否由插件生成，不伪造值 |

### 27.1 Hook 选择原则

1. 首选请求路由入口与业务事件分派入口，它们比协程状态机内部指令更接近稳定语义边界。
2. 对 e0.A / g0.z、jz0.A / vs1.z 等合成协程方法，必须检查实例 e 字段；同一个方法体承载多个协程状态机分支，不能无条件拦截。
3. l5.z / ot1.z 不应被当作 SSE parser Hook 点；它们的 e 分支和创建点已经证明其职责不同。
4. fl0 / qp0 属于底层行读取辅助类，只有排查行读取超时或取消问题时才考虑临时探针。
5. PoW JNI 默认只读观测。不得替换挑战、伪造 nonce、跳过难度校验或修改 X-DS-PoW-Response。
6. 2.7.3 和 2.7.5 必须使用独立 profile。版本识别失败时维持只读，不尝试猜测映射。

### 27.2 低敏诊断字段

建议仅采集：
- APK version / versionCode / DEX profile id。
- Hook 类、方法和完整 descriptor。
- Hook 安装结果、安装次数、线程名和耗时。
- HTTP status、路由类别、响应类型。
- SSE event name、事件序号、数据字节长度、读取耗时。
- Continuation / Flow 的完成、取消、异常类别。
- Auto-resume 次数、触发原因和结束原因。

禁止采集 prompt、完整响应正文、Authorization、Cookie、API key、挑战原文、salt、nonce 和完整请求头。

## 28. 设备端验证矩阵与完成标准

静态链路已还原；真实 Hook 仍需在目标设备完成以下验证：

| 测试场景 | 重点观察 | 通过标准 |
|---|---|---|
| 冷启动 / 版本识别 | package version、versionCode、profile | 正确选择 2.7.3 或 2.7.5；未知版本只读 |
| 普通聊天请求 | hx2.g / nw3.e | 一次用户发送只建立一个预期请求流 |
| 成功响应与首个 Delta | e0/jz0 或 g0/vs1 | response → parser → event dispatcher 顺序闭合 |
| 完成事件 | finish / close | 状态终结一次，不重复完成 |
| 心跳超时 | x-ds-sse-heartbeat-timeout-secs | 默认 10 秒；服务端 header 可覆盖；超时后按设计结束 |
| 非 2xx 响应 | e0 / g0 错误分支 | 结构化错误进入错误对象，不误当作 Delta |
| 断线与自动恢复 | qu1.h / rr2.h | 恢复触发可追踪，不重复追加已确认消息 |
| 用户取消 | Flow / Continuation cancel | 取消向上游传播，连接与资源关闭 |
| 并行流 | allow_parallel_streams | 多流任务彼此隔离，事件不串线 |
| 打断并发送 | interrupt_and_send_enabled | 旧流按策略终止，新请求只创建一次 |
| PoW challenge | ap9 / of2 / JNI | 真实 challenge 输入输出一致，不跳过校验 |
| 重复 lifecycle | Hook installer | 同一 Hook 不重复安装，单点失败不阻断其他独立 Hook |

**设备验收通过条件：**
- 版本 profile 与 APK 身份一致。
- 每个 Hook 精确匹配完整 descriptor 和分支条件。
- Hook 安装幂等；单个可选 Hook 失败不会导致全部功能 Hook 重复安装。
- 请求、SSE 事件、完成、取消和 auto-resume 的状态链闭合。
- 无敏感数据进入日志。
- 未完成设备测试前，不将任何候选标记为“生产可用”。


## 29. 跨版本通用 Hook 重新审计

本轮将分析范围扩展到仓库内全部 DeepSeek 宿主 APK/APKM：2.7.1、2.7.2/code289-cn、2.7.3、2.7.4/code294、2.7.5；2.7.2 APK 与设备日志作为关联证据集。2.7.4 是 APKM，必须按内嵌 APK 组件拆分分析；2.7.2 已有 APK 输入，需先核对签名、versionCode 与日志设备构建身份，再生成静态 Profile。

- 通用 Hook 设计文档：[docs/universal-hook/README.md](docs/universal-hook/README.md)
- 审计脚本：[scripts/audit_deepseek_apk.py](scripts/audit_deepseek_apk.py)
- 跨版本聚合脚本：[scripts/aggregate_deepseek_hook_audit.py](scripts/aggregate_deepseek_hook_audit.py)
- 独立工作流：[.github/workflows/deepseek-universal-hook-audit.yml](.github/workflows/deepseek-universal-hook-audit.yml)
- 工作分支：`work/deepseek-universal-hook-audit`

设计原则：以业务语义角色定位 Hook，通过调用图、完整方法描述符、类型结构、稳定框架调用、协议锚点和字节码形状交叉验证；未知版本、候选歧义和 ClassLoader 解析失败时 fail-closed。静态分析、动态观察和真机 Hook 验证分开标记。自动审计结果将直接写回本仓库 `audit/`，不以本地文件作为交付。


- Points-to storage quotas use deterministic quotient/remainder allocation. When roots outnumber record slots, zero-quota roots are still traversed and diagnosed; the global cap is never exceeded. Call-context and contextual-receiver record families have independent caps.


## 最终审计交付（2026-11-08）

本轮五版本静态审计、版本身份隔离、Points-to root 预算修复、E0–E3 候选证据分级和旧探针日志根因分析已统一归档。最终交付入口：[Universal Hook 最终审计与交接报告](docs/universal-hook/FINAL-AUDIT-AND-HANDOFF-2026-11-08.md)。

关键结论：
- Matrix Run [#203](https://github.com/qingjian0/apps/actions/runs/42448208970) 五版本任务与 aggregate 均成功；产物对应提交 `3769fb3b99047bb41ceb52c322c04c93aeda710b`。
- 输入标签 2.7.3 的 APK Manifest 实际为 2.5.2 / code273，已从可信跨版本匹配隔离。
- E0–E3 是静态证据等级，不代表 runtime-confirmed 或 Hook authorized；当前静态产物两项计数均为 0。
- Points-to 存储硬上限与 root 公平配额已验证，但上下文展开仍可能不完整，必须保持 diagnostic-only / fail-closed。
- `dsprobe.log` 证实 2.7.2/code289-cn 宿主误选 2.7.1 full mapping，随后 unmapped 类名触发 ClassNotFoundException；探针源码修复和真机回归仍未交付。
- 最新 PR HEAD 的两个 CI workflow 为 `action_required`，不可写成通过；详见最终交接报告。

