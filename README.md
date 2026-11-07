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

当前 `main` 分支文件：

| 文件 | 大小 | 当前可确认内容 |
|---|---:|---|
| `DeepSeek_2.7.5.apk` | 22,210,268 bytes | DeepSeek 2.7.5 APK；本轮尚未完成二进制静态反编译 |
| `deepseek 273.apk` | 14,211,169 bytes | DeepSeek 2.7.3 APK；本轮尚未完成二进制静态反编译 |
| `dsprobe.log` | 12,320 bytes / 50 行 | 模块启动、宿主版本识别、Hook 安装与失败日志 |
| `deekseep_vision.log` | 6,440,972 bytes / 19,747 行 | `OPEN_NATIVE_CALL_OBSERVER` 的请求构造、传输、continuation 和 callback 观测 |
| `README.md` | 本文件 | 分析归档 |

当前文件树中**没有 2.7.2 APK**，但运行日志记录的宿主为 `2.7.2/code289-cn`。因此，2.7.2 的版本识别和映射问题只能先依据运行日志分析，不能与本仓库 APK 做同版本静态交叉验证。

## 2. 核心结论

1. 已从运行日志定位到请求对象：`ly1`，实现接口 `wu1`。
2. 已定位到两层传输调用：`zn3.o(wu1, Long) -> y60` 和 `jw3.g(wu1, Long) -> y60`。
3. 已定位到返回对象上的 continuation 方法：`y60.b(fl4, yb3) -> Object`；返回对象 `y60` 实现接口 `el4`。
4. 请求构造调用栈可追到 `mr2.h → jr2.m → jr2.y → mw1.e → mw1.y → ly1.<init>`。这是日志中的调用栈反向还原结果，方向按“外层调用者到被调用者”排列。
5. continuation 内部存在大量双回调对象。当前观测到 21 个 callback 类、9,578 次 callback-enter；其中 944 次以异常结束，8,634 次正常结束。
6. 另一份启动日志显示宿主识别为 `2.7.2/code289-cn`，但功能 Hook 安装选择了 `2.7.1 full mode`，同时触发 code257 Canvas 类映射失败。版本路由/映射混用是当前最高优先级问题。
7. 当前证据足以建立请求—传输—continuation 的 Hook 入口候选，但**还不能声称已识别 HTTP endpoint、序列化器、SSE/JSON 解析器或 Agent 工具执行语义**。

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

### 8.1 已有日志证据支持

```text
mr2.h
  → jr2.m
    → jr2.y
      → mw1.e
        → mw1.y
          → ly1.<init>          [request object]
            → zn3.o(wu1, Long)  [transport-dispatch]
              → jw3.g(wu1, Long) [transport-low-level]
                → y60             [response/continuation holder]
                  → y60.b(fl4, yb3)
                    → callback-0 / callback-1
                      → concrete callback methods
```

### 8.2 尚未被当前日志证实

- HTTP endpoint / path、请求方法、headers、认证字段。
- 实际网络库及其内部 Call / Request / Response 类型。
- 请求体序列化器、JSON adapter 或 protobuf 等协议。
- SSE / WebSocket / chunked response 的具体解析实现。
- `y60.b` 的 `fl4`、`yb3` 参数的正式语义。
- 哪个 callback 对应文本增量、工具调用、Agent 状态、完成/失败终态。
- Agent tool call 的完整执行链、工具结果如何回注模型。
- 2.7.5 与 2.7.3 的类名映射差异。

这些内容需要对 APK 做静态反编译，并与动态日志交叉验证。不能用 callback 类名或对象字段形状直接推测协议语义。

## 9. 下一轮逆向与 Hook 验证顺序

### P0：先修正版本识别与映射边界

1. 核对宿主 package、versionName、versionCode、build/code 标识。
2. 追踪识别结果如何进入 Host Profile。
3. 检查为何 code289 被路由到 2.7.1 full mode。
4. 检查 code257 的 `mf6` 映射为何进入 code289 的安装流程。
5. 安装失败必须按单 Hook 隔离；不能导致其他已匹配 Hook 被整体中止。
6. 未知版本禁止静默套用最近版本的完整映射。

### P1：请求与传输

1. 对 `ly1` 两个构造器做字段写入点追踪，建立字段表。
2. 逐层反编译 `mr2.h / jr2.m / jr2.y / mw1.e / mw1.y`，确定工厂职责。
3. 以 `zn3.o` 为请求入口、`jw3.g` 为低层入口做只读 Hook。
4. 比较四次请求的对象字段变化，确认请求类别/重试/会话差异。
5. 追踪 `y60` 的创建位置及 `a/b` 字段赋值。

### P2：响应与 Agent

1. 反编译 `y60.b(fl4, yb3)` 的调用者、参数构造点和返回路径。
2. 从 continuation 中 callback-0 / callback-1 的实例创建位置回溯。
3. 优先分析 `qj3.y` 的 771 次异常和 `qj3.q/w` 的高频调用。
4. 结合 UI 状态变化识别文本增量、工具调用、Agent 中间状态和终态。
5. 找到工具调用从模型响应到本地执行，再到结果回注请求的闭环。

### P3：序列化与流协议

1. 从 `ly1` 字段消费点追踪到最终编码器。
2. 从 `y60` / continuation 的数据源追踪到解码器和事件分发器。
3. 确认协议后再建立 serializer / stream parser Hook，不提前认定 JSON 或 SSE。
4. 对照 2.7.3、2.7.5 APK，建立版本差异表和映射回归测试。

## 10. 安全与日志采集约束

- 默认不记录用户消息正文、访问令牌、Cookie、Authorization header 或完整请求体。
- 优先记录类名、方法签名、参数类型、对象身份、线程、调用深度、耗时、返回类型和异常类型。
- 如需字段级分析，使用字段名、类型和长度等元信息；敏感字段值必须脱敏。
- 任何功能 Hook 先经过只读观察和版本匹配验证，不允许通过未知映射强行执行。
- 日志中的类名均为混淆符号；未经静态反编译确认，不得赋予业务名称。

## 11. 交付状态

| 分析项 | 状态 |
|---|---|
| 仓库文件盘点 | 已完成 |
| dsprobe 启动 / 版本路由日志分析 | 已完成 |
| 请求类 `ly1` 与构造器候选 | 日志已定位，字段语义待反编译 |
| 请求工厂调用栈 | 日志已定位 |
| 传输层 `zn3.o → jw3.g` | 日志已定位 |
| 返回对象 `y60` 与 continuation | 日志已定位 |
| callback 类和频次统计 | 已完成日志统计 |
| 高频 callback 异常统计 | 已完成日志统计，根因待分析 |
| HTTP / 序列化 / SSE / Agent 工具闭环 | 未确认 |
| 2.7.3 / 2.7.5 APK 静态反编译 | 未完成 |
| 2.7.2 同版本 APK 交叉验证 | 仓库缺少 2.7.2 APK |

---

## 分析记录元信息

- 仓库：[`qingjian0/apps`](https://github.com/qingjian0/apps)
- 分支：`main`
- 分析对象：DeepSeek Android APK 与运行日志
- 目标宿主包：`com.deepseek.chat`
- 已观测宿主版本：`2.7.2/code289-cn`
- 当前核心动态入口候选：`ly1`、`zn3.o`、`jw3.g`、`y60.b`
- 当前最高优先级问题：code289 宿主被路由到 2.7.1 full mode，并触发 code257 的 `mf6` 类映射失败
- 证据来源：仓库中的 `dsprobe.log`、`deekseep_vision.log` 及文件树元数据
- 状态：日志调用链已归档；APK 静态反编译与完整 Agent / 序列化链仍待完成


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

按依赖关系拆成四条并行工作流：

### 工作流 A：版本与安装器

- [ ] 找到 `hostGeneration` 的产生位置和数据类型。
- [ ] 找到 `HostRemap` 选择 2.7.1 full mode 的条件。
- [ ] 找到 code257 Canvas renderer Hook 的注册入口。
- [ ] 找到 `mf6` 字符串/映射表的来源，确认是缺失映射、错误 profile，还是错误的类加载器。
- [ ] 查清 `installAllFeatureHooks` 的所有调用点和触发时机。
- [ ] 验证安装成功项是否有全局去重；失败项是否被重复尝试；单项失败是否中断批次。

**验收：** code289 不得安装 2.7.1/code257 专属 Hook；单个可选 Hook 失败不应使其他匹配 Hook 回滚或阻断；重复 lifecycle 不应重复安装同一 Hook。

### 工作流 B：请求构造和传输

- [ ] 反编译 `ly1` 两个构造器，标出每个字段的写入点。
- [ ] 找到 `mw1.y/e`、`jr2.y/m`、`mr2.h` 的完整方法体。
- [ ] 确认 `zn3.o` 是否包装、转换或排队请求。
- [ ] 确认 `jw3.g` 的真实网络调用边界。
- [ ] 追踪 `jw3` 字段、其初始化位置及其网络依赖。
- [ ] 对比 4 个请求对象的字段差异，避免把请求构造器参数位置误认为业务字段语义。

**验收：** 得到字段级请求模型、请求工厂调用图、传输层调用图；所有字段语义必须有读写点或调用点证据。

### 工作流 C：Continuation / Callback

- [ ] 反编译 `y60.b`，确认 `fl4`、`yb3` 的参数来源和返回语义。
- [ ] 找到 21 个 callback 对象的实例创建位置。
- [ ] 优先反编译 `qj3.y/q/w`、`pg1.y`、`x0.y`、`f0.y`。
- [ ] 将 `e06` 异常发生前的输入对象类型、receiverId、线程和上游调用者关联起来。
- [ ] 检查 callback-1 是否由 callback-0 派生、包装或串联；不能仅凭角色编号推断。
- [ ] 对长耗时 3,744 ms 的 callback 事件定位具体方法和线程。

**验收：** 明确 callback 对象创建链、方法调用关系、异常传播边界、返回对象含义；至少能够把一次完整请求的 continuation 事件串成可复现时序。

### 工作流 D：序列化、流协议和 Agent 工具闭环

- [ ] 从 `ly1` 字段使用位置找到编码/序列化入口。
- [ ] 从 `jw3.g` 向下追到真实网络库与请求执行方法。
- [ ] 从响应数据源向上追到 `y60.b` 的 callback 输入。
- [ ] 确认文本增量、工具调用、Agent 状态、终态分别对应什么事件对象。
- [ ] 追踪工具调用参数从响应对象到本地工具执行，再到结果回注。
- [ ] 对照 UI 更新位置验证 callback 语义。

**验收：** 得到端到端链路：请求对象 → 序列化 → 网络发送 → 响应解码 → 事件分发 → Agent 工具执行（若存在）→ 结果回注 → UI 更新。每条边必须由反编译调用点或动态事件佐证。

## 14. 自动验证与分析质量门槛

后续每次新增分析结论，按以下规则自动核对：

1. **计数闭合**：callback-enter 必须等于 callback-exit + callback-throw；continuation 同理。
2. **调用链闭合**：每个 parent/child 关系要有同一事件 ID、对象身份或明确栈证据。
3. **版本一致**：每条 Hook 结论必须注明 APK/宿主版本与映射 profile。
4. **类名与语义分离**：混淆类名定位不等于业务语义定位。
5. **静态与动态交叉验证**：静态反编译结论需要动态日志验证；动态推断不能替代方法体分析。
6. **敏感信息最小化**：不保存消息正文、token、Cookie、Authorization header 或完整请求体。
7. **可复现性**：记录 APK SHA-256、工具版本、反编译参数、DEX 编号、类/方法描述符和证据位置。当前仓库还未提供这些完整元数据。

## 15. 本轮结论修订

- 原调用链 `mr2.h → jr2.m → jr2.y → mw1.e → mw1.y → ly1.<init> → zn3.o → jw3.g → y60.b → callbacks` 保留为**动态日志证实的调用路径**，但它不是所有请求分支都必然经过的完整静态调用图。
- callback 异常总数 944，其中 `qj3.y` 为 771；异常高度集中在 callback-1。
- continuation 129 次进入中 87 次正常退出、42 次抛异常。
- `dsprobe.log` 的 10 次功能 Hook 安装尝试全部失败，均遇到同一个 `mf6` 类加载错误。
- 当前最重要的工程问题是 code289 → 2.7.1/code257 profile 错配，以及失败后安装流程重复触发。
- APK 的静态反编译尚未在本轮实际执行。因此 HTTP endpoint、serializer、SSE parser、Agent tool executor 仍列为待证，不宣称完成。
