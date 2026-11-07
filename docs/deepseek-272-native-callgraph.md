# DeepSeek 国内版 2.7.2 / code289-cn：Native API 静态调用链审计

> 审计对象严格限定为本仓库分支中的 `deepseek-2-7-2.apk`。本报告不引用 2.7.3 / 2.7.5 的混淆符号作为 code289 的静态证据。

## 1. APK 身份与审计覆盖

| 项目 | 结果 |
|---|---|
| Package | `com.deepseek.chat` |
| versionName | `2.7.2` |
| versionCode | `289` |
| APK bytes | `22,205,160` |
| SHA-256 | `3c2fe31c73575400b9d59e46dde05daa2ef06491498ebfef658801e99eca1aff` |
| DEX | `classes.dex`、`classes2.dex`、`classes3.dex` |
| DEX count | 3 |
| Smali class files | 15,365 |
| Method declarations | 72,258 |
| Runtime candidate classes | 23 / 23 |
| Candidate methods | 117 |
| Candidate call sites | 3,369 |
| Native libraries | 16 (arm64-v8a) |
| JADX | exit=3, 346 diagnostics; smali/DEX inventory is the authoritative evidence for this report |

审计脚本通过 Android binary XML 解析 Manifest，明确断言 package/versionName/versionCode 必须匹配上述值；不再把 Apktool `-r` 输出的二进制 Manifest 当成 XML parse error。候选类名匹配也只接受 default-package descriptor，避免把 `Lj$/time/.../d0;` 之类第三方包内类误算成同名混淆类。

## 2. Request / Transport 入口

### 2.1 请求模型 ly1

DEX descriptor：

```text
Lly1; implements Lwu1;
<init>(String, Integer, String, ArrayList,
       boolean, boolean, String, boolean, String, String, int)
```

Serializer `jy1` 对外字段：

| Java 字段 | JSON 字段 | 含义（由构造和调用点确认） |
|---|---|---|
| a | `chat_session_id` | 会话 ID |
| b | `parent_message_id` | 父消息 ID |
| c | `prompt` | 用户提示词 |
| d | `ref_file_ids` | 引用文件 ID 列表 |
| e | `thinking_enabled` | 思考模式开关 |
| f | `search_enabled` | 搜索开关 |
| g | `audio_id` | 音频 ID |
| h | `preempt` | 请求抢占标记 |
| i | `model_type` | 模型类型 |
| j | `action` | 请求动作；合成构造器默认值为 `retry` |

字段 k **不在 JSON Serializer 中**。调用点将其读取为字符串并设置 HTTP header `X-DS-PoW-Response`，所以不能把 k 当作 JSON 请求字段。

### 2.2 Repository Request Factory

`nn0` 的 11 参数主构造器将 `zn3` 注入字段 b；其请求方法 `d(Lys, String, Integer, List, boolean, boolean, String, Lada, Lnr2, Continuation)` 创建 `mw1` 协程工厂。该工厂根据 `ys` 会话模型、parent ID、附件、thinking/search/audio 参数构造 `ly1`，再交给传输层。

这说明 `ly1` 并非孤立 DTO；正常产品路径还包含 `ys` 会话状态和 `nn0` repository。直接构造 `ly1` 时必须显式处理 session ID、parent ID、model_type、action 和 preempt，不能仅填 prompt。

### 2.3 Transport / Cold Flow

```text
nn0 request factory
  → mw1 builds ly1
  → zn3.o(Lwu1, Long): Ly60
  → jw3.g(Lwu1, Long): Ly60
  → Ly60 implements el4 (cold Flow)
  → collect via b(fl4, Continuation)
  → l5 coroutine executes bi5.b(Ktor request, response handler)
```

- `zn3` 构造器接收 `bi5`，并构造 `jw3` 及网络依赖。
- `zn3.o` 将请求委托给其 `jw3`。
- `jw3.g` 按 `wu1` 的具体请求类选择 endpoint / serializer，构建 Ktor request。
- `jw3.g` 返回 `Ly60`，不是在调用时立即完成网络请求；真正执行发生在 Flow 被 collect 后。
- `jw3.g` 中可确认的 endpoint 包括：
  - `/api/v0/chat/completion`
  - `/api/v0/chat/regenerate`
  - `/api/v0/chat/continue`
  - `/api/v0/chat/edit_message`
  - `/api/v0/chat/resume_stream`
- 请求 builder 会在 `ly1.k` 非空时设置 `X-DS-PoW-Response`。

**适配器影响：** 仅调用 `zn3.o` 不会自动产生网络请求，必须 collect 返回的 Flow；不能把 `y60.b` 当成底层 HTTP/SSE parser。

## 3. Challenge / PoW

### 3.1 Challenge 请求

- endpoint：`/api/v0/chat/create_pow_challenge`
- request model：`ut1`
- serializer 字段：`target_path`
- 目标路径由调用方传入，例如 `/api/v0/chat/completion`。
- Challenge response model：`ms9`，Serializer `ks9` 字段如下：

| 字段 | JSON 名 |
|---|---|
| a | `algorithm` |
| b | `challenge` |
| c | `salt` |
| d | `signature` |
| e | `difficulty` |
| f | `expire_at` |
| g | `expire_after` |
| h | `target_path` |

### 3.2 PoW 计算

- `df0.d(String, ms9, Continuation)` 根据 challenge 算法生成 `gf0`。
- `gf0` 是 `AuthedPowSolution`，Serializer `ef0` 字段：
  `algorithm`、`challenge`、`salt`、`signature`、`answer`、`target_path`。
- `PowCalculator` 位于 `com.deepseek.crypto.PowCalculator`，加载 `librscrypto.so`。
- Java wrapper：`a(long difficulty, String base, String challenge): long`。
- JNI：`nativeCalculateDeepSeekHashV1Pow(String base, String challenge, long difficulty): long`。
- code289 的调用构造 base 为 `salt + "_" + expire_at + "_"`，并传入 challenge 和 difficulty。
- PoW 结果由宿主的 ChallengePlugin 流程使用；不要用模块自行猜测的算法替代原生 `librscrypto`。

### 3.3 ChallengePlugin

`nq1` 是 Ktor ChallengePlugin 的核心实现：

- `nq1.a(...)` 读取当前请求的 `X-DS-PoW-Response`。
- 它通过 `nq1.c(...)` 执行带 Challenge headers 的请求。
- 当响应包含 challenge 时，使用 `AtomicReference` 协调并发 challenge 处理，再调用 `hq1.a` 求解并重试。
- `nq1.c` 明确设置：
  - `X-DS-Challenge-Response`
  - `X-DS-PoW-Response`
  - `X-Debug-Recaptcha-Challenge`（仅在对应参数存在时）

**适配器影响：** 最优实现是复用已配置的 `zn3/bi5` Ktor client，让宿主 Plugin 自己完成 Challenge、PoW、缓存、并发协调和重试。不要在 Local API 层再实现一套不完整 PoW。

## 4. HTTP Response / SSE / Event Decoder

### 4.1 HTTP 响应处理

`g0` 是 Ktor response handler：

- 检查响应状态与 Content-Type。
- 成功流式响应读取 `x-ds-sse-heartbeat-timeout-secs`，默认值为 10 秒。
- 成功分支建立 SSE Flow。
- 非成功/JSON 错误分支读取响应体并反序列化服务端错误模型，形成错误事件，而不是将其误当成正常 delta。

### 4.2 SSE 行解析

`ts1` 读取 Ktor `ByteReadChannel`，解析 SSE 的 event/data 行，构造：

```text
sha(eventName: String, data: String)
  → s5 collector adapter
  → cv1(sha)
  → dv1 event stream
```

`cv1.a` 指向 `sha`；`sha.a` 是 event name，`sha.b` 是 data JSON 字符串。

### 4.3 业务事件分发

`r3.c(Ldv1, Continuation)` 是业务事件分发位置。可确认的 event 分支：

| Event | 解码 / 处理 |
|---|---|
| `ready` | `ChatCompletionReadyEventData`；字段包括 request_message_id、response_message_id、model_type、request_content |
| `delta` | `DeltaCommand`（JsonElement）；转为 `st3(path, operation, value)`，交给状态树更新 |
| `hint` | `ChatCompletionHintEventData` |
| `title` | 标题事件数据 |
| `update_session` | Session 更新事件 |
| `close` | 关闭流事件 |
| HTTP 错误事件 | 解析错误包装模型，不应伪装成 delta |

### 4.4 DeltaCommand 是 JSON Patch，而不是普通字符串

- `DeltaCommand`（`c26`）是 JsonElement sealed type，包含 JsonPrimitive / JsonObject / JsonArray 表示。
- `st3` 有三个字段：path、operation、value。
- `doc.W(st3, gv1)` 将 patch 转成 `xq1(path, operation, value)`，再调用 `ll23.y` 更新状态树。
- 已确认 patch 操作包括 `SET`、`APPEND`、`BATCH`。
- 根状态 `zca` 的 `response` 字段映射到 `gy`。
- `gy` 保存 fragments；继承自 `xr` 的 `B()` 遍历文本 fragment 并拼接内容。

**适配器影响：** 不可把 SSE 的 `data` 字符串直接当作用户文本。应按 event name 解码，并应用 DeltaCommand patch；从 `response.fragments` / `gy.B()` 获取最终可见文本。Reasoning、工具调用和 Search/Find/Open fragments 需要分别映射，不能全部压成普通文本。

## 5. 对 Native Adapter 的直接实现建议

1. 在 code289 专用 profile 中捕获 `nn0` 主构造器注入的 `zn3` 实例；不要使用 2.3.x 的 `liveQ71/liveR92`。
2. 通过 code289 的 `ly1` request model 进入 `zn3.o`；对冷 Flow 执行 collect。
3. 复用 `bi5` 中已安装的 Ktor plugins，尤其 `nq1` ChallengePlugin。
4. 在 collector 中识别 `cv1 → sha`，按 event name 分流。
5. `delta` 按 `st3(path, operation, value)` 的 patch 协议应用到 response state；从 `gy.B()` 提取累计文本，并以稳定前缀差分输出 OpenAI delta。
6. 单独映射 reasoning、finish、tool/search/find/open 等事件；不支持的 fragment 必须显式报告，不可静默丢弃。
7. 用 request ID / chat_session_id 隔离 collector、cancel handle、timeout、resume state；请求取消必须取消对应 Flow Job，而不是只关闭 HTTP socket。
8. 在真实设备验证非流式、流式、PoW challenge、resume、cancel、错误响应和并发 session。

## 6. 尚未完成的验证

- 目前已完成 APK 身份验证、DEX/Smali 全量提取、动态候选静态相关、Request/Transport、Challenge/PoW、SSE parser 和 event reducer 的静态调用链还原。
- 尚未在 Android 设备上验证通过反射调用 `zn3.o` 并 collect Flow。
- 尚未完成 Local API 到 `CompletionResult` 的端到端文本、reasoning、tool-call 映射。
- 尚未通过 code289 实机验证取消、超时、resume 和并发隔离。
- JADX 退出码 3 且报告 346 条诊断；对关键调用链以 APK 中的 DEX/Smali 和 serializer descriptor 为准。
- 本报告只证明静态结构和调用关系，不代表 Native Adapter 已经运行成功。

## 7. 可复现产物

- Workflow：`.github/workflows/deepseek-272-static-audit.yml`
- Branch：`work/deepseek-272-static-audit`
- Successful run：`42342447740`
- Artifact：`deepseek-272-static-evidence`
- Artifact SHA-256：`923b1f319803f87e27d0f3e44b65cc7148cdcd82c7713826ec9631f0bfb0d61e`
- Artifact contains: full smali archive, candidate class descriptors, candidate call-site inventory, method inventory, DEX list, APK hash, summary and report.
