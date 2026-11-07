# DeepSeek APK / 运行链路分析归档

> 本仓库用于保存 DeepSeek Android APK、运行探针日志及其逆向分析记录。当前分析目标限定为 **DeepSeek 官方 Android 宿主应用**，重点是版本识别、Agent 请求构造、网络传输、流式 continuation/callback 链，以及可用于后续 Hook 的稳定边界。
>
> **证据等级约定**
> - **日志直接证实**：日志中存在明确的类名、方法签名、调用栈或事件计数。
> - **强推断**：由多个调用栈和对象关系共同支持，但尚未通过 APK 静态反编译确认语义。
> - **未确认**：当前日志没有足够证据，不得写成已定位。
>
> 本文是基于当前仓库文件与日志的分析归档，不把混淆类名臆测成业务语义，也不把未检查的 APK 二进制说成已完成反编译。

## 1. 仓库材料盘点

本仓库当前保留两份 APK 和两份运行日志。2.7.5 已完成一次完整的静态证据采集；2.7.3 仍未执行同等级静态审计。

| 文件 | 大小 | 本轮处理状态 |
|---|---:|---|
| DeepSeek_2.7.5.apk | 22,210,268 bytes | 已提取 3 个 DEX；JADX 1.5.6 输出 13,940 个 Java 源文件；第一方索引覆盖 12,596 个类 |
| deepseek 273.apk | 14,211,169 bytes | 已盘点，尚未执行同等级静态反编译 |
| deekseep_vision.log | 6,440,972 bytes / 19,747 行 | 已完成动态事件、线程、异常、Continuation 与 Callback 统计 |
| dsprobe.log | 12,320 bytes / 50 行 | 已完成 Hook 安装失败和版本映射分析 |

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

- 2.7.5 的 l5.z 网络执行器和 ot1.z 底层 SSE 收集方法仍有 JADX 反编译失败；可以确认它们的调用位置和接口关系，但不能把未反编译方法体补写成事实。
- 原生 PoW 库已确认 JNI 导出符号、Rust SHA3/Keccak 相关依赖和 Keccak 计算路径；精确的 digest 变体、nonce 搜索条件和输入字节拼接仍需更深的原生反汇编。
- ToolOpen、ToolFind、Search 等片段的数据模型已确认；完整工具执行发生在服务端还是某个未识别的本地子系统，尚未被当前 APK 静态证据完全证明。
- 2.7.5 真实设备运行、Hook 可用性和请求/响应时序尚未验证。
- 2.7.3 APK 尚未完成同等级反编译，因此不能给出完整跨版本映射。

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
| 2.7.3 静态反编译与版本映射 | 未完成 | APK 已在仓库，待单独审计 |

本轮没有把 JADX 的部分反编译结果包装成完整成功，也没有把静态调用链包装成设备运行验证。

## 分析记录元信息

- 主仓库：qingjian0/apps
- 文档分支：main
- 静态审计分支：work/deepseek-275-apk-audit
- 2.7.5 静态审计工作流：<https://github.com/qingjian0/apps/actions/runs/42335918440>
- 审计工作流源码：<https://github.com/qingjian0/apps/blob/work/deepseek-275-apk-audit/.github/workflows/deepseek-275-apk-audit.yml>
- 审计工具：JADX 1.5.6，启用 show-bad-code
- 目标 APK：DeepSeek_2.7.5.apk
- APK SHA-256：ddc52ef868b991fd33e634de834a3e2c022b0cd7ff9e854f4f141996aaeadb70
- 工作流产物：decompiled-first-party.zip、first-party-class-index.json、cross-references.json、native-libraries.zip、native-library-index.md、report.md
- 质量状态：JADX exit code 3；344 项反编译错误；本 README 明确区分已确认与待还原部分。

## 13. 下一轮具体反编译任务单

### A. 版本识别与 Hook 安装器

- 保留未知版本只读策略。
- 将 2.7.2 / code289-cn 的动态映射与 2.7.5 静态映射分开存储。
- 审计 Hook 安装器的幂等性、失败隔离、生命周期重试和版本回退。
- 2.7.5 新 Hook 入口必须先通过 descriptor 匹配和真实设备探针验证。

### B. SSE 与网络执行器

- 从 DEX/smali 还原 l5.z 和 ot1.z。
- 追踪 Ktor HttpClient response 到 il4 Flow 的转换。
- 还原 SSE event 行解析、data 解码、DeltaCommand 应用、异常分类、取消传播和 auto-resume 的重试边界。
- 对照动态事件验证 ready、finish、toast、hint、title、update_file、close 等事件是否按静态分派执行。

### C. 原生 PoW

- 从 JNI 导出函数继续追踪 librscrypto.so 内部调用。
- 还原 Keccak/SHA3 变体、挑战和盐的拼接顺序、nonce 搜索及 difficulty 判定。
- 在 arm64 设备上验证 nativeCalculateDeepSeekHashV1Pow 的输入输出和耗时。
- 不用模拟值替代真实 PoW，不伪造 X-DS-PoW-Response。

### D. Agent / 工具数据流

- 追踪 DeltaCommand 的 h26 多态数据如何变成 ToolOpenFragment、ToolFindFragment、SearchFragment 和引用对象。
- 检查服务端返回片段的状态机：WIP、finished、no-result、failed。
- 只有找到本地执行器及其授权/回传闭环后，才将其标记为本地 Agent 工具能力。

### E. 2.7.3 对照审计

- 对 deepseek 273.apk 运行同一静态采集工作流。
- 对比 API 路由、请求模型、Serializer、SSE event、PoW 算法、Hook 入口和原生库。
- 输出跨版本差异表，不按混淆类名猜测对应关系。

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

原生库字符串包含 Rust sha3c 与 keccak crate 的源码路径和 KECCAK_F_ROUND_COUNT 相关信息；AArch64 反汇编也能看到 Keccak 状态/轮函数路径。该库没有可用的完整 DWARF 调试信息，精确 SHA3 变体、nonce 搜索条件和难度判定尚未完全恢复。

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

底层 ot1.z 和网络执行器 l5.z 尚未被 JADX 完整还原，因此当前结论覆盖事件分派和调用关系，不覆盖底层 SSE 字节/行解析的每个实现细节。

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