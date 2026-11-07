# DeepSeek 通用 Hook 跨版本语义审计

> 本报告由 GitHub Actions 从 apps 仓库内的宿主 APK/APKM、日志和 SSE 证据包生成。静态候选不等于设备 Hook 已成功。

## APK / DEX 总览

| 版本标签 | 文件 | 组件数 | DEX 数 | 类数 | 方法数 | 调用边 | 字段读/写 | CFG 分支方法/分支数 | 候选方法数 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2.7.1 | deepseek271.apk | 1 | 3 | 14906 | 71243 | 453718 | 152946/70534 | 27309/250308 | 2233 |
| 2.7.2 | deepseek-2-7-2.apk | 1 | 3 | 15055 | 72258 | 462894 | 156175/71761 | 27804/256989 | 2263 |
| 2.7.3 | deepseek 273.apk | 1 | 3 | 13043 | 64557 | 400184 | 133829/61032 | 24387/221348 | 1886 |
| 2.7.4 | com.deepseek.chat_2.7.4-294_1arch_3dpi_23lang_8b3ec3b6e7e5bfc2253e9c86dfc4c4e7_apkmirror.com.apkm | 28 | 4 | 15370 | 73611 | 472017 | 158420/72875 | 28351/261392 | 2283 |
| 2.7.5 | DeepSeek_2.7.5.apk | 1 | 3 | 15054 | 72257 | 463096 | 156189/71813 | 27803/257263 | 2262 |

## 版本标签核验

| 矩阵标签 | Manifest versionName | versionCode | 身份状态 | 是否参与跨版本匹配 |
|---|---|---:|---|---|
| 2.7.1 | 2.7.1 | 287 | verified | yes |
| 2.7.2 | 2.7.2 | 289 | verified | yes |
| 2.7.3 | 2.5.2 | 273 | label-mismatch | no |
| 2.7.4 | 2.7.4 | 294 | verified | yes |
| 2.7.5 | 2.7.5 | 295 | verified | yes |

2.7.3 当前输入的 Manifest versionName=2.5.2，与矩阵标签 2.7.3 冲突；该输入仍保留独立静态索引，但不会参与可信跨版本候选匹配。需要替换正确 APK 或确认该构建的版本标识后再纳入。

## 组件身份核对

| 版本 | 组件 | 包名 | versionCode | versionName | split | 签名证书 SHA-256 | 身份完整度 | APK SHA-256 |
|---|---|---|---|---|---|---|---|---|
| 2.7.1 | deepseek271.apk | com.deepseek.chat | 287 | 2.7.1 | None | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+version+signer+hash | `86e77d419fed957dde8857a14d2f5340499ea40549f10cc3180c596e3f77efc8` |
| 2.7.2 | deepseek-2-7-2.apk | com.deepseek.chat | 289 | 2.7.2 | None | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+version+signer+hash | `3c2fe31c73575400b9d59e46dde05daa2ef06491498ebfef658801e99eca1aff` |
| 2.7.3 | deepseek 273.apk | com.deepseek.chat | 273 | 2.5.2 | None | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+version+signer+hash | `a6d025c14c98118a5a67849e04aaef6f3c9c13aaf0fa62caaee0e47091374ea3` |
| 2.7.4 | component-0-base.apk | com.deepseek.chat | 294 | 2.7.4 | None | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+version+signer+hash | `2e898602374ed75f53d8e4c162fa625f5f4e1793b16fbd567f6dd02f6277a709` |
| 2.7.4 | component-1-split_config.ar.apk | com.deepseek.chat | 294 | None | config.ar | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `293fe0329d975432a39887a08166d5d81d0dc7423360f2b73bc2d1842e6180ed` |
| 2.7.4 | component-2-split_config.arm64_v8a.apk | com.deepseek.chat | 294 | None | config.arm64_v8a | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `482af60defab32a280810bcbdb2a96d9505cb3214eab0d2c46b41d6a34bee03c` |
| 2.7.4 | component-3-split_config.de.apk | com.deepseek.chat | 294 | None | config.de | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `02be66ae9c5911d788c19b1ac2c0ed2bd5f94076d53bd1bcbd99f22f9f0983c3` |
| 2.7.4 | component-4-split_config.es.apk | com.deepseek.chat | 294 | None | config.es | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `7de28dce9152e065cfa7627f9cc8fe3fb4790700cc88c5b07fa2c7a42a071e11` |
| 2.7.4 | component-5-split_config.et.apk | com.deepseek.chat | 294 | None | config.et | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `d34b1e6fdc43251c96db6829f7b3251b7a82c35685d5432c1292ef6d311e608d` |
| 2.7.4 | component-6-split_config.fi.apk | com.deepseek.chat | 294 | None | config.fi | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `7cac52a64af8a0a2315a07cbde54e6de7dcb724fb1647622e30d496a8dfa0f8c` |
| 2.7.4 | component-7-split_config.fr.apk | com.deepseek.chat | 294 | None | config.fr | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `a59c05c16be6acc332808fbc091f4dfedb60c4c0128a365aa435fa97f8d4b1ef` |
| 2.7.4 | component-8-split_config.hi.apk | com.deepseek.chat | 294 | None | config.hi | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `a97f7a4fa616ad68704704fce87025697aeb214938a79be20d74d9b716cdd15d` |
| 2.7.4 | component-9-split_config.hu.apk | com.deepseek.chat | 294 | None | config.hu | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `5d1906f1fb181b3b28067cb4a8f864f6f735a16b40094ad6a617028655ec28a4` |
| 2.7.4 | component-10-split_config.in.apk | com.deepseek.chat | 294 | None | config.in | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `a030373bed90d360392879fa53607a2c01a83b39280ab7869a9a4ef9b0a036bd` |
| 2.7.4 | component-11-split_config.it.apk | com.deepseek.chat | 294 | None | config.it | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `a0e2a3449f0416b42539e5805bade589babcb6add2e4bd17c006aae0cd6d3993` |
| 2.7.4 | component-12-split_config.ja.apk | com.deepseek.chat | 294 | None | config.ja | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `52b527b0400f61a0bc07029feb69aa2a4136fc537c3ac203843e69501316b376` |
| 2.7.4 | component-13-split_config.xxhdpi.apk | com.deepseek.chat | 294 | None | config.xxhdpi | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `94e99356132a1c063e06c05f81de129dcaefe9567aad0eca1a622d4904365356` |
| 2.7.4 | component-14-split_config.ko.apk | com.deepseek.chat | 294 | None | config.ko | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `0ce9ca19a8e97e891727be2a88495ae0845c8c5935c4bc1009416247d3338dbe` |
| 2.7.4 | component-15-split_config.ms.apk | com.deepseek.chat | 294 | None | config.ms | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `8e9538e19dee5c5c58a1780889ca7ddfbde76c316ab8c2d764838d9ffdab7b58` |
| 2.7.4 | component-16-split_config.nl.apk | com.deepseek.chat | 294 | None | config.nl | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `80c4d4b0f049bfcc69649c831764ed874985b7e0d54f32b130dd11ce820686a3` |
| 2.7.4 | component-17-split_config.pl.apk | com.deepseek.chat | 294 | None | config.pl | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `23cb96b75f984d04ec00aa7ac260496234c02e38de1a000f6360f3031786ebd2` |
| 2.7.4 | component-18-split_config.pt.apk | com.deepseek.chat | 294 | None | config.pt | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `59a81d69b6f8117e88659923b0474661b27a7ac88cdb191c541f15d2b79c0ed6` |
| 2.7.4 | component-19-split_config.ru.apk | com.deepseek.chat | 294 | None | config.ru | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `03814bc963c6d45168709aa564fb62dd86a4c8f486555f10978869d9d368a1aa` |
| 2.7.4 | component-20-split_config.sv.apk | com.deepseek.chat | 294 | None | config.sv | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `91baa4e705464970c22ea4f043d09c46400ad605874581e932b53c9d3522a4cf` |
| 2.7.4 | component-21-split_config.th.apk | com.deepseek.chat | 294 | None | config.th | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `5434d73f2d5c50c56c64e10b641290db1d1340285f647309b68e5eb1c23144f0` |
| 2.7.4 | component-22-split_config.tr.apk | com.deepseek.chat | 294 | None | config.tr | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `9ae32b39bb80a6556a869936e3882d02d55be8dd525ee950f6d0fb650f648108` |
| 2.7.4 | component-23-split_config.uk.apk | com.deepseek.chat | 294 | None | config.uk | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `e8bdb1a71af311427c4d07528964cc4d556a6b075ec1d9366fefbdd808f22070` |
| 2.7.4 | component-24-split_config.vi.apk | com.deepseek.chat | 294 | None | config.vi | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `e94fbdb7a8b5b9e7796073e1d1d9b2601bc6647742403c5da3e556742934b211` |
| 2.7.4 | component-25-split_config.xxxhdpi.apk | com.deepseek.chat | 294 | None | config.xxxhdpi | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `b8d2eb12aa499ff56739a73c72d3ca06c71145e5869d8617af058b325aba707a` |
| 2.7.4 | component-26-split_config.zh.apk | com.deepseek.chat | 294 | None | config.zh | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `22662db8db58f1e4195027f8f842cd211e47360885ac5bc47205d106ad9d0bdd` |
| 2.7.4 | component-27-split_config.hdpi.apk | com.deepseek.chat | 294 | None | config.hdpi | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+signer+hash | `8515a693c420f6cc7b53f1d313d88fcd5baff6e2c1460e79ea9bfaed5ffb11be` |
| 2.7.5 | DeepSeek_2.7.5.apk | com.deepseek.chat | 295 | 2.7.5 | None | `c6893c5368f7b5122fecdafc6c4ecf49e0b3dc4e42bd166cdb646907788c7ffa` | package+version+signer+hash | `ddc52ef868b991fd33e634de834a3e2c022b0cd7ff9e854f4f141996aaeadb70` |

## 语义候选匹配

匹配分数由语义锚点、稳定框架/API 调用族和规范化 opcode 分布组成；候选截取前先按锚点数量、稳定 API 调用量和方法体规模排序。仅保留至少共享一个协议锚点、稳定 API 调用或协议字符串，且双向最佳并领先第二名至少 0.06 的匹配；仅角色相同、并列或非互选候选均被拒绝。分数仅用于排序，必须回看源码/Smali 和调用者/被调用者证据。

| 角色 | 来源版本 | 来源方法 | 目标版本 | 候选方法 | 相似度 |
|---|---|---|---|---|---:|
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.2 | `Ln65;-><clinit>()V` | 0.9973 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.9947 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.9947 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.2 | `Lfcc;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.4 | `Lvgc;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 0.9707 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 0.9707 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 0.9707 |
| account_capability | 2.7.1 | `Lmna;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.2 | `Lqsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.8914 |
| account_capability | 2.7.1 | `Lmna;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.5 | `Lzsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.8914 |
| account_capability | 2.7.1 | `Lmna;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.4 | `Lwwa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.8905 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnz6;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lhv7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9037 |
| account_capability | 2.7.1 | `Lnz6;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lav7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9029 |
| account_capability | 2.7.1 | `Lnz6;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Luw7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9029 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.2 | `Lth7;-><clinit>()V` | 1.0000 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9915 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.4 | `Lmj7;-><clinit>()V` | 0.9834 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.2 | `Lt74;-><clinit>()V` | 0.9985 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.9985 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.9977 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.2 | `Ld45;-><clinit>()V` | 0.9933 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9927 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.4 | `Ln65;-><clinit>()V` | 0.9881 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.2 | `Lj9b;->a()V` | 1.0000 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.4 | `Ltdb;->a()V` | 1.0000 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.5 | `Lr9b;->a()V` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.2 | `Lfia;->e()Z` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.4 | `Lima;->e()Z` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.2 | `Lav7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Luw7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.2 | `Lav7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lhv7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9991 |
| account_capability | 2.7.2 | `Ld45;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9994 |
| account_capability | 2.7.2 | `Ld45;-><clinit>()V` | 2.7.4 | `Ln65;-><clinit>()V` | 0.9946 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.4 | `Lvgc;->j()J` | 1.0000 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.4 | `Lima;->e()Z` | 1.0000 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.2 | `Lj9b;->a()V` | 2.7.4 | `Ltdb;->a()V` | 1.0000 |
| account_capability | 2.7.2 | `Lj9b;->a()V` | 2.7.5 | `Lr9b;->a()V` | 1.0000 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 1.0000 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.9973 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.9973 |
| account_capability | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lqsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.5 | `Lzsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 1.0000 |
| account_capability | 2.7.2 | `Lqsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.4 | `Lwwa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9991 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 1.0000 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.9992 |
| account_capability | 2.7.2 | `Lth7;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9915 |
| account_capability | 2.7.2 | `Lth7;-><clinit>()V` | 2.7.4 | `Lmj7;-><clinit>()V` | 0.9834 |
| account_capability | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lima;->e()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.4 | `Lmj7;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9915 |
| account_capability | 2.7.4 | `Ln65;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9952 |
| account_capability | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lt94;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.9992 |
| account_capability | 2.7.4 | `Ltdb;->a()V` | 2.7.5 | `Lr9b;->a()V` | 1.0000 |
| account_capability | 2.7.4 | `Luw7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lhv7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9991 |
| account_capability | 2.7.4 | `Lvgc;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lwwa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.5 | `Lzsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9991 |
| account_capability | 2.7.4 | `Lx85;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.4 | `Lx9b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.4 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.5 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.4 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.4 | `Lrhc;->o(Lo19;Ly99;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.5 | `Ladc;->o(Lfy8;Lo69;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.4 | `Laab;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.5 | `Lx5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.2 | `Lq5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.4 | `Lbab;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.5 | `Ly5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;->d(Lbn3;)Ljava/lang/Object;` | 2.7.2 | `Lq5b;->d(Lrn3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;->d(Lbn3;)Ljava/lang/Object;` | 2.7.4 | `Lbab;->e(Lrp3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;->d(Lbn3;)Ljava/lang/Object;` | 2.7.5 | `Ly5b;->d(Lwn3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.2 | `Lnv4;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.4 | `Lvx4;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.5 | `Lrv4;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lh1b;-><clinit>()V` | 2.7.2 | `Lq6b;-><clinit>()V` | 0.9843 |
| agent_planning | 2.7.1 | `Lh1b;-><clinit>()V` | 2.7.5 | `Lx6b;-><clinit>()V` | 0.9843 |
| agent_planning | 2.7.1 | `Lh1b;-><clinit>()V` | 2.7.4 | `Labb;-><clinit>()V` | 0.9697 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.2 | `Lyc5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.4 | `Lif5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.5 | `Lcd5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.2 | `Ldrb;-><clinit>()V` | 0.9948 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.5 | `Ldrb;-><clinit>()V` | 0.9933 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.4 | `Lqvb;-><clinit>()V` | 0.9912 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.2 | `Lov4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.4 | `Lwx4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.5 | `Lsv4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.2 | `Loca;-><clinit>()V` | 0.9984 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.5 | `Lxca;-><clinit>()V` | 0.9975 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.4 | `Lqga;-><clinit>()V` | 0.9952 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.2 | `Ls6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.4 | `Lnt5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.5 | `Lhr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lm1a;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lux9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 0.9983 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.4 | `Lvpc;->b(Lorg/json/JSONObject;)Z` | 0.9983 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.5 | `Ljlc;->b(Lorg/json/JSONObject;)Z` | 0.9983 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.2 | `Lbf9;-><clinit>()V` | 0.9970 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 0.9970 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.4 | `Lxi9;-><clinit>()V` | 0.9941 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.2 | `Lyp;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.4 | `Laq;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.5 | `Lzp;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.2 | `Ll03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.4 | `Li23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.5 | `Lq03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.4 | `Lr19;->f(IIILo19;Lne4;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 0.9980 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.5 | `Liy8;->f(IIILfy8;Loc4;)V` | 0.9980 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.2 | `Ln03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.4 | `Lk23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.2 | `Lp21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.4 | `Le41;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.5 | `Lr21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lfj9;->C(Lvd3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqf9;->C(Ldc3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.2 | `Lsmc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.4 | `Ldrc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.5 | `Lrmc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.2 | `Lsr0;->a(Liy8;)Lg89;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.4 | `Lit0;->a(Ly19;)Lxb9;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.5 | `Ltr0;->a(Lpy8;)Ln89;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 0.9870 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.5 | `Lm08;->a(Ltg5;Lec3;)Ljava/lang/Object;` | 0.9870 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.4 | `La28;->a(Lyi5;Lwd3;)Ljava/lang/Object;` | 0.9853 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.2 | `Lwcc;->e()Lxjc;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.4 | `Lmhc;->e()Lioc;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.4 | `Lgha;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.5 | `Lnda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.2 | `Ljkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.4 | `Lvob;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.2 | `Lwjc;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.4 | `Lhoc;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.5 | `Lvjc;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.2 | `Lxt9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.4 | `Lwx9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.5 | `Leu9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.2 | `Ldx6;-><clinit>()V` | 0.9971 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.4 | `Lc07;-><clinit>()V` | 0.9971 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.5 | `Ljx6;-><clinit>()V` | 0.9971 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.4 | `Lrhc;->o(Lo19;Ly99;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.5 | `Ladc;->o(Lfy8;Lo69;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.4 | `Lxi9;-><clinit>()V` | 0.9970 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.5 | `Liy8;->f(IIILfy8;Loc4;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.4 | `Lr19;->f(IIILo19;Lne4;)V` | 0.9980 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.4 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.5 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.4 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.4 | `Lnt5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.5 | `Lhr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Ldrb;-><clinit>()V` | 2.7.5 | `Ldrb;-><clinit>()V` | 0.9985 |
| agent_planning | 2.7.2 | `Ldrb;-><clinit>()V` | 2.7.4 | `Lqvb;-><clinit>()V` | 0.9963 |
| agent_planning | 2.7.2 | `Ldx6;-><clinit>()V` | 2.7.4 | `Lc07;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ldx6;-><clinit>()V` | 2.7.5 | `Ljx6;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 2.7.4 | `Lgha;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 2.7.5 | `Lnda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 2.7.5 | `Lm08;->a(Ltg5;Lec3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 2.7.4 | `La28;->a(Lyi5;Lwd3;)Ljava/lang/Object;` | 0.9982 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lhj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lgj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lfj9;->C(Lvd3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqf9;->C(Ldc3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.4 | `Lvob;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 2.7.4 | `Lvpc;->b(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 2.7.5 | `Ljlc;->b(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.2 | `Ll03;-><clinit>()V` | 2.7.4 | `Li23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ll03;-><clinit>()V` | 2.7.5 | `Lq03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.4 | `Lx9b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.4 | `Lk23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.4 | `Lvx4;->run()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.5 | `Lrv4;->run()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lm1a;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lux9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Loca;-><clinit>()V` | 2.7.5 | `Lxca;-><clinit>()V` | 0.9992 |
| agent_planning | 2.7.2 | `Loca;-><clinit>()V` | 2.7.4 | `Lqga;-><clinit>()V` | 0.9968 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lov4;->onGlobalLayout()V` | 2.7.4 | `Lwx4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lov4;->onGlobalLayout()V` | 2.7.5 | `Lsv4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.4 | `Le41;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.5 | `Lr21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.4 | `Laab;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.5 | `Lx5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lq5b;-><clinit>()V` | 2.7.4 | `Lbab;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lq5b;-><clinit>()V` | 2.7.5 | `Ly5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lq5b;->d(Lrn3;)Ljava/lang/Object;` | 2.7.4 | `Lbab;->e(Lrp3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lq5b;->d(Lrn3;)Ljava/lang/Object;` | 2.7.5 | `Ly5b;->d(Lwn3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lq6b;-><clinit>()V` | 2.7.5 | `Lx6b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lq6b;-><clinit>()V` | 2.7.4 | `Labb;-><clinit>()V` | 0.9843 |
| agent_planning | 2.7.2 | `Ls6b;->toString()Ljava/lang/String;` | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Ls6b;->toString()Ljava/lang/String;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lsmc;->a(Lorg/json/JSONObject;)Z` | 2.7.4 | `Ldrc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.2 | `Lsmc;->a(Lorg/json/JSONObject;)Z` | 2.7.5 | `Lrmc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.2 | `Lsr0;->a(Liy8;)Lg89;` | 2.7.4 | `Lit0;->a(Ly19;)Lxb9;` | 1.0000 |
| agent_planning | 2.7.2 | `Lsr0;->a(Liy8;)Lg89;` | 2.7.5 | `Ltr0;->a(Lpy8;)Ln89;` | 1.0000 |
| agent_planning | 2.7.2 | `Lwcc;->e()Lxjc;` | 2.7.4 | `Lmhc;->e()Lioc;` | 1.0000 |
| agent_planning | 2.7.2 | `Lwcc;->e()Lxjc;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 1.0000 |
| agent_planning | 2.7.2 | `Lwjc;->b(Ljava/util/LinkedList;)I` | 2.7.4 | `Lhoc;->b(Ljava/util/LinkedList;)I` | 1.0000 |
| agent_planning | 2.7.2 | `Lwjc;->b(Ljava/util/LinkedList;)I` | 2.7.5 | `Lvjc;->b(Ljava/util/LinkedList;)I` | 1.0000 |
| agent_planning | 2.7.2 | `Lxt9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.4 | `Lwx9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lxt9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.5 | `Leu9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lyc5;-><clinit>()V` | 2.7.4 | `Lif5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lyc5;-><clinit>()V` | 2.7.5 | `Lcd5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lyp;->run()V` | 2.7.4 | `Laq;->run()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lyp;->run()V` | 2.7.5 | `Lzp;->run()V` | 1.0000 |
| agent_planning | 2.7.4 | `La28;->a(Lyi5;Lwd3;)Ljava/lang/Object;` | 2.7.5 | `Lm08;->a(Ltg5;Lec3;)Ljava/lang/Object;` | 0.9982 |
| agent_planning | 2.7.4 | `Laab;->toString()Ljava/lang/String;` | 2.7.5 | `Lx5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Labb;-><clinit>()V` | 2.7.5 | `Lx6b;-><clinit>()V` | 0.9843 |
| agent_planning | 2.7.4 | `Laq;->run()V` | 2.7.5 | `Lzp;->run()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lbab;-><clinit>()V` | 2.7.5 | `Ly5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lbab;->e(Lrp3;)Ljava/lang/Object;` | 2.7.5 | `Ly5b;->d(Lwn3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.4 | `Lc07;-><clinit>()V` | 2.7.5 | `Ljx6;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.5 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.4 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.4 | `Ldrc;->a(Lorg/json/JSONObject;)Z` | 2.7.5 | `Lrmc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Le41;-><clinit>()V` | 2.7.5 | `Lr21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lfj9;->C(Lvd3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqf9;->C(Ldc3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.4 | `Lgha;->h(Ljava/lang/Object;)V` | 2.7.5 | `Lnda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lhj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lgj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.4 | `Lhoc;->b(Ljava/util/LinkedList;)I` | 2.7.5 | `Lvjc;->b(Ljava/util/LinkedList;)I` | 1.0000 |
| agent_planning | 2.7.4 | `Li23;-><clinit>()V` | 2.7.5 | `Lq03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lif5;-><clinit>()V` | 2.7.5 | `Lcd5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lit0;->a(Ly19;)Lxb9;` | 2.7.5 | `Ltr0;->a(Lpy8;)Ln89;` | 1.0000 |
| agent_planning | 2.7.4 | `Lk23;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lm1a;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lux9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.4 | `Lmhc;->e()Lioc;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 1.0000 |
| agent_planning | 2.7.4 | `Lnt5;->b()Ljava/lang/String;` | 2.7.5 | `Lhr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lqga;-><clinit>()V` | 2.7.5 | `Lxca;-><clinit>()V` | 0.9976 |
| agent_planning | 2.7.4 | `Lqvb;-><clinit>()V` | 2.7.5 | `Ldrb;-><clinit>()V` | 0.9978 |
| agent_planning | 2.7.4 | `Lr19;->f(IIILo19;Lne4;)V` | 2.7.5 | `Liy8;->f(IIILfy8;Loc4;)V` | 0.9980 |
| agent_planning | 2.7.4 | `Lrhc;->o(Lo19;Ly99;)V` | 2.7.5 | `Ladc;->o(Lfy8;Lo69;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Lvob;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lvpc;->b(Lorg/json/JSONObject;)Z` | 2.7.5 | `Ljlc;->b(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.4 | `Lvx4;->run()V` | 2.7.5 | `Lrv4;->run()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lwx4;->onGlobalLayout()V` | 2.7.5 | `Lsv4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.4 | `Lwx9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.5 | `Leu9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.4 | `Lx9b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.4 | `Lxi9;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 0.9970 |
| agent_tool | 2.7.1 | `Laaa;-><clinit>()V` | 2.7.2 | `Lhfa;-><clinit>()V` | 0.9674 |
| agent_tool | 2.7.1 | `Laaa;-><clinit>()V` | 2.7.4 | `Ljja;-><clinit>()V` | 0.9674 |
| agent_tool | 2.7.1 | `Laaa;-><clinit>()V` | 2.7.5 | `Lqfa;-><clinit>()V` | 0.9674 |
| agent_tool | 2.7.1 | `Lde;->k(IZLjava/util/List;ILjp3;Lyt2;Lkp3;Lbx4;Lbx4;Ldx4;Ldx4;Leg7;Ln05;I)V` | 2.7.2 | `Lq60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.7433 |
| agent_tool | 2.7.1 | `Lde;->k(IZLjava/util/List;ILjp3;Lyt2;Lkp3;Lbx4;Lbx4;Ldx4;Ldx4;Leg7;Ln05;I)V` | 2.7.4 | `Lv60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.7433 |
| agent_tool | 2.7.1 | `Lde;->k(IZLjava/util/List;ILjp3;Lyt2;Lkp3;Lbx4;Lbx4;Ldx4;Ldx4;Leg7;Ln05;I)V` | 2.7.5 | `Lt60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.7433 |
| agent_tool | 2.7.1 | `Lgk0;-><clinit>()V` | 2.7.2 | `Lzk0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lgk0;-><clinit>()V` | 2.7.4 | `Ljm0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lgk0;-><clinit>()V` | 2.7.5 | `Lal0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Llk0;-><clinit>()V` | 2.7.2 | `Lel0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Llk0;-><clinit>()V` | 2.7.4 | `Lom0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Llk0;-><clinit>()V` | 2.7.5 | `Lfl0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lmt4;-><clinit>()V` | 2.7.2 | `Ltu4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lmt4;-><clinit>()V` | 2.7.4 | `Lbx4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lmt4;-><clinit>()V` | 2.7.5 | `Lxu4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lpt4;-><clinit>()V` | 2.7.2 | `Lwu4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lpt4;-><clinit>()V` | 2.7.4 | `Lex4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lpt4;-><clinit>()V` | 2.7.5 | `Lav4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.1 | `Lst4;-><clinit>()V` | 2.7.2 | `Lzu4;-><clinit>()V` | 0.9741 |
| agent_tool | 2.7.1 | `Lst4;-><clinit>()V` | 2.7.4 | `Lhx4;-><clinit>()V` | 0.9741 |
| agent_tool | 2.7.1 | `Lst4;-><clinit>()V` | 2.7.5 | `Ldv4;-><clinit>()V` | 0.9741 |
| agent_tool | 2.7.1 | `Lwj0;->r(ILn05;)Lbx4;` | 2.7.2 | `Lpk0;->r(ILr15;)Lfy4;` | 1.0000 |
| agent_tool | 2.7.1 | `Lwj0;->r(ILn05;)Lbx4;` | 2.7.4 | `Lzl0;->r(ILa45;)Ln05;` | 1.0000 |
| agent_tool | 2.7.1 | `Lwj0;->r(ILn05;)Lbx4;` | 2.7.5 | `Lqk0;->r(ILv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.1 | `Lwj0;->s(Ln05;)Lbx4;` | 2.7.2 | `Lpk0;->s(Lr15;)Lfy4;` | 1.0000 |
| agent_tool | 2.7.1 | `Lwj0;->s(Ln05;)Lbx4;` | 2.7.4 | `Lzl0;->s(La45;)Ln05;` | 1.0000 |
| agent_tool | 2.7.1 | `Lwj0;->s(Ln05;)Lbx4;` | 2.7.5 | `Lqk0;->s(Lv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.1 | `Lz44;->f(Ln05;)Ljava/util/ArrayList;` | 2.7.2 | `Lv54;->c(Lr15;)Ljava/util/ArrayList;` | 1.0000 |
| agent_tool | 2.7.1 | `Lz44;->f(Ln05;)Ljava/util/ArrayList;` | 2.7.4 | `Lv74;->b(La45;)Ljava/util/ArrayList;` | 1.0000 |
| agent_tool | 2.7.1 | `Lz44;->f(Ln05;)Ljava/util/ArrayList;` | 2.7.5 | `Ly54;->c(Lv15;)Ljava/util/ArrayList;` | 1.0000 |
| agent_tool | 2.7.1 | `Lz44;->l(Ln05;)Lbx4;` | 2.7.2 | `Lv54;->l(Lr15;)Lfy4;` | 1.0000 |
| agent_tool | 2.7.1 | `Lz44;->l(Ln05;)Lbx4;` | 2.7.4 | `Lv74;->l(La45;)Ln05;` | 1.0000 |
| agent_tool | 2.7.1 | `Lz44;->l(Ln05;)Lbx4;` | 2.7.5 | `Ly54;->l(Lv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.2 | `Lel0;-><clinit>()V` | 2.7.4 | `Lom0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lel0;-><clinit>()V` | 2.7.5 | `Lfl0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lhfa;-><clinit>()V` | 2.7.4 | `Ljja;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lhfa;-><clinit>()V` | 2.7.5 | `Lqfa;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lpk0;->r(ILr15;)Lfy4;` | 2.7.4 | `Lzl0;->r(ILa45;)Ln05;` | 1.0000 |
| agent_tool | 2.7.2 | `Lpk0;->r(ILr15;)Lfy4;` | 2.7.5 | `Lqk0;->r(ILv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.2 | `Lpk0;->s(Lr15;)Lfy4;` | 2.7.4 | `Lzl0;->s(La45;)Ln05;` | 1.0000 |
| agent_tool | 2.7.2 | `Lpk0;->s(Lr15;)Lfy4;` | 2.7.5 | `Lqk0;->s(Lv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.2 | `Lq60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lv60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_tool | 2.7.2 | `Lq60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lt60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_tool | 2.7.2 | `Lqfa;-><clinit>()V` | 2.7.4 | `Lsja;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lqfa;-><clinit>()V` | 2.7.5 | `Lzfa;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Ltfa;-><clinit>()V` | 2.7.4 | `Lvja;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Ltfa;-><clinit>()V` | 2.7.5 | `Lcga;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Ltu4;-><clinit>()V` | 2.7.4 | `Lbx4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Ltu4;-><clinit>()V` | 2.7.5 | `Lxu4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lv54;->c(Lr15;)Ljava/util/ArrayList;` | 2.7.4 | `Lv74;->b(La45;)Ljava/util/ArrayList;` | 1.0000 |
| agent_tool | 2.7.2 | `Lv54;->c(Lr15;)Ljava/util/ArrayList;` | 2.7.5 | `Ly54;->c(Lv15;)Ljava/util/ArrayList;` | 1.0000 |
| agent_tool | 2.7.2 | `Lv54;->l(Lr15;)Lfy4;` | 2.7.4 | `Lv74;->l(La45;)Ln05;` | 1.0000 |
| agent_tool | 2.7.2 | `Lv54;->l(Lr15;)Lfy4;` | 2.7.5 | `Ly54;->l(Lv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.2 | `Lwu4;-><clinit>()V` | 2.7.4 | `Lex4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lwu4;-><clinit>()V` | 2.7.5 | `Lav4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lzk0;-><clinit>()V` | 2.7.4 | `Ljm0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lzk0;-><clinit>()V` | 2.7.5 | `Lal0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lzu4;-><clinit>()V` | 2.7.4 | `Lhx4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.2 | `Lzu4;-><clinit>()V` | 2.7.5 | `Ldv4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lbx4;-><clinit>()V` | 2.7.5 | `Lxu4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lex4;-><clinit>()V` | 2.7.5 | `Lav4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lhx4;-><clinit>()V` | 2.7.5 | `Ldv4;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Ljja;-><clinit>()V` | 2.7.5 | `Lqfa;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Ljm0;-><clinit>()V` | 2.7.5 | `Lal0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lom0;-><clinit>()V` | 2.7.5 | `Lfl0;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lsja;-><clinit>()V` | 2.7.5 | `Lzfa;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lv60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lt60;->e(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_tool | 2.7.4 | `Lv74;->b(La45;)Ljava/util/ArrayList;` | 2.7.5 | `Ly54;->c(Lv15;)Ljava/util/ArrayList;` | 1.0000 |
| agent_tool | 2.7.4 | `Lv74;->l(La45;)Ln05;` | 2.7.5 | `Ly54;->l(Lv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.4 | `Lvja;-><clinit>()V` | 2.7.5 | `Lcga;-><clinit>()V` | 1.0000 |
| agent_tool | 2.7.4 | `Lzl0;->r(ILa45;)Ln05;` | 2.7.5 | `Lqk0;->r(ILv15;)Ljy4;` | 1.0000 |
| agent_tool | 2.7.4 | `Lzl0;->s(La45;)Ln05;` | 2.7.5 | `Lqk0;->s(Lv15;)Ljy4;` | 1.0000 |
| attachment_file | 2.7.1 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 2.7.2 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 2.7.4 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.2 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.4 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.5 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.2 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.4 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.5 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.2 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.4 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.5 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.2 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.4 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.5 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.2 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.4 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.5 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `La1c;->j()Landroid/net/Uri;` | 2.7.2 | `Lw6c;->j()Landroid/net/Uri;` | 1.0000 |
| attachment_file | 2.7.1 | `La1c;->j()Landroid/net/Uri;` | 2.7.4 | `Lkbc;->j()Landroid/net/Uri;` | 1.0000 |
| attachment_file | 2.7.1 | `La1c;->j()Landroid/net/Uri;` | 2.7.5 | `Lw6c;->j()Landroid/net/Uri;` | 1.0000 |
| attachment_file | 2.7.1 | `La9;->run()V` | 2.7.2 | `Lc9;->run()V` | 0.9938 |
| attachment_file | 2.7.1 | `La9;->run()V` | 2.7.5 | `Ld9;->run()V` | 0.9938 |
| attachment_file | 2.7.1 | `La9;->run()V` | 2.7.4 | `Ld9;->run()V` | 0.7612 |
| attachment_file | 2.7.1 | `Laa7;-><clinit>()V` | 2.7.2 | `Lde7;-><clinit>()V` | 0.9977 |
| attachment_file | 2.7.1 | `Laa7;-><clinit>()V` | 2.7.5 | `Lke7;-><clinit>()V` | 0.9954 |
| attachment_file | 2.7.1 | `Laa7;-><clinit>()V` | 2.7.4 | `Lxf7;-><clinit>()V` | 0.9842 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->b()Lkg4;` | 2.7.2 | `Landroidx/core/content/FileProvider;->b()Lsh4;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->b()Lkg4;` | 2.7.4 | `Landroidx/core/content/FileProvider;->b()Lzj4;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->b()Lkg4;` | 2.7.5 | `Landroidx/core/content/FileProvider;->b()Lwh4;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lkg4;` | 2.7.2 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lsh4;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lkg4;` | 2.7.4 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lzj4;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lkg4;` | 2.7.5 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lwh4;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 2.7.2 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 2.7.4 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 2.7.5 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 2.7.2 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 2.7.4 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 2.7.5 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 2.7.2 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 2.7.4 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 2.7.5 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 2.7.2 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 2.7.4 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 1.0000 |
| attachment_file | 2.7.1 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 2.7.5 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 1.0000 |
| attachment_file | 2.7.1 | `Lau4;->h(Lyz5;)Lt86;` | 2.7.2 | `Lhv4;->h(Lc26;)Lva6;` | 0.9903 |
| attachment_file | 2.7.1 | `Lau4;->h(Lyz5;)Lt86;` | 2.7.4 | `Lpx4;->h(Ls46;)Lnd6;` | 0.9903 |
| attachment_file | 2.7.1 | `Lau4;->h(Lyz5;)Lt86;` | 2.7.5 | `Llv4;->h(Lh26;)Lbb6;` | 0.9903 |
| attachment_file | 2.7.1 | `Lba7;->c(Leg7;Lxdb;ZLd48;Ljava/util/Map;Ldx4;Ldx4;Ldx4;Ln05;I)V` | 2.7.2 | `Lk37;->e(Lyj7;Lijb;ZLk78;Ljava/util/Map;Lhy4;Lhy4;Lhy4;Lr15;I)V` | 0.9965 |
| attachment_file | 2.7.1 | `Lba7;->c(Leg7;Lxdb;ZLd48;Ljava/util/Map;Ldx4;Ldx4;Ldx4;Ln05;I)V` | 2.7.4 | `Lfc8;->d(Lrl7;Lqnb;ZLh98;Ljava/util/Map;Lp05;Lp05;Lp05;La45;I)V` | 0.9965 |
| attachment_file | 2.7.1 | `Lba7;->c(Leg7;Lxdb;ZLd48;Ljava/util/Map;Ldx4;Ldx4;Ldx4;Ln05;I)V` | 2.7.5 | `Lq37;->a(Lfk7;Lpjb;ZLq78;Ljava/util/Map;Lly4;Lly4;Lly4;Lv15;I)V` | 0.9960 |
| attachment_file | 2.7.1 | `Lbr3;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lqr3;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9996 |
| attachment_file | 2.7.1 | `Lbr3;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lrt3;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9996 |
| attachment_file | 2.7.1 | `Lbr3;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lrw1;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9857 |
| attachment_file | 2.7.1 | `Lbr8;->toString()Ljava/lang/String;` | 2.7.2 | `Llu8;->toString()Ljava/lang/String;` | 0.5800 |
| attachment_file | 2.7.1 | `Lbr8;->toString()Ljava/lang/String;` | 2.7.4 | `Lzx8;->toString()Ljava/lang/String;` | 0.5800 |
| attachment_file | 2.7.1 | `Lbr8;->toString()Ljava/lang/String;` | 2.7.5 | `Lsu8;->toString()Ljava/lang/String;` | 0.5800 |
| attachment_file | 2.7.1 | `Lcb7;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lmqa;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.7114 |
| attachment_file | 2.7.1 | `Lcb7;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lnva;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.7083 |
| attachment_file | 2.7.1 | `Lcb7;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lqta;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.6620 |
| attachment_file | 2.7.1 | `Lcn/fly/verify/df$1;->run()V` | 2.7.2 | `Lcn/fly/verify/df$1;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcn/fly/verify/df$1;->run()V` | 2.7.4 | `Lcn/fly/verify/df$1;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcn/fly/verify/df$1;->run()V` | 2.7.5 | `Lcn/fly/verify/df$1;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 2.7.2 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 2.7.4 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 2.7.5 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 2.7.2 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 0.9940 |
| attachment_file | 2.7.1 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 2.7.4 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 0.9940 |
| attachment_file | 2.7.1 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 2.7.5 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 0.9940 |
| attachment_file | 2.7.1 | `Lcom/bytedance/apm/internal/ApmDelegate$8;->uploadFiles(Ljava/lang/String;Ljava/util/List;Ljava/util/Map;)Lcom/bytedance/services/apm/api/HttpResponse;` | 2.7.2 | `Lcom/bytedance/apm/internal/ApmDelegate$8;->uploadFiles(Ljava/lang/String;Ljava/util/List;Ljava/util/Map;)Lcom/bytedance/services/apm/api/HttpResponse;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/bytedance/apm/internal/ApmDelegate$8;->uploadFiles(Ljava/lang/String;Ljava/util/List;Ljava/util/Map;)Lcom/bytedance/services/apm/api/HttpResponse;` | 2.7.5 | `Lcom/bytedance/apm/internal/ApmDelegate$8;->uploadFiles(Ljava/lang/String;Ljava/util/List;Ljava/util/Map;)Lcom/bytedance/services/apm/api/HttpResponse;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.2 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.4 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.5 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.2 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.4 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 0.9965 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.5 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 0.9965 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 2.7.2 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 2.7.2 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 2.7.4 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 2.7.5 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 2.7.4 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 2.7.5 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 2.7.4 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 2.7.5 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 2.7.4 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 2.7.5 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 2.7.2 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 2.7.4 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 2.7.5 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 2.7.2 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 2.7.4 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 2.7.5 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 2.7.2 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 2.7.4 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 2.7.5 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ld1c;->b(Lx8b;)V` | 2.7.2 | `Lz6c;->b(Lf9b;)V` | 0.9959 |
| attachment_file | 2.7.1 | `Ld1c;->b(Lx8b;)V` | 2.7.4 | `Lnbc;->c(Lw0d;)V` | 0.9959 |
| attachment_file | 2.7.1 | `Ld1c;->b(Lx8b;)V` | 2.7.5 | `Lz6c;->b(Ln9b;)V` | 0.9959 |
| attachment_file | 2.7.1 | `Ldr8;->a(Lorg/json/JSONObject;)Ldr8;` | 2.7.2 | `Lnu8;->a(Lorg/json/JSONObject;)Lnu8;` | 1.0000 |
| attachment_file | 2.7.1 | `Ldr8;->a(Lorg/json/JSONObject;)Ldr8;` | 2.7.5 | `Luu8;->a(Lorg/json/JSONObject;)Luu8;` | 1.0000 |
| attachment_file | 2.7.1 | `Ldr8;->a(Lorg/json/JSONObject;)Ldr8;` | 2.7.4 | `Lby8;->a(Lorg/json/JSONObject;)Lby8;` | 0.9990 |
| attachment_file | 2.7.1 | `Ldz7;->u(Leg7;Ldx4;Ldx4;Ln05;I)V` | 2.7.2 | `Lf23;->C(Lyj7;Lhy4;Lhy4;Lr15;I)V` | 0.9771 |
| attachment_file | 2.7.1 | `Ldz7;->u(Leg7;Ldx4;Ldx4;Ln05;I)V` | 2.7.4 | `Lo07;->q(Lrl7;Lp05;Lp05;La45;I)V` | 0.9771 |
| attachment_file | 2.7.1 | `Ldz7;->u(Leg7;Ldx4;Ldx4;Ln05;I)V` | 2.7.5 | `Lk23;->o(Lfk7;Lly4;Lly4;Lv15;I)V` | 0.9771 |
| attachment_file | 2.7.1 | `Le3c;->c(Lorg/json/JSONObject;)V` | 2.7.2 | `La9c;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Le3c;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Lndc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Le3c;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `La9c;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lf72;->u(Ls02;)V` | 2.7.2 | `Lc82;->u(Ll12;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lf72;->u(Ls02;)V` | 2.7.4 | `Lt92;->u(Lc32;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lf72;->u(Ls02;)V` | 2.7.5 | `Lh82;->u(Lq12;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lf7c;->run()V` | 2.7.2 | `Lddc;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lf7c;->run()V` | 2.7.4 | `Lthc;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lf7c;->run()V` | 2.7.5 | `Lcdc;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lfr0;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lbs0;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.6115 |
| attachment_file | 2.7.1 | `Lfr0;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lcs0;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 0.6115 |
| attachment_file | 2.7.1 | `Lfr0;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lqt0;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.6111 |
| attachment_file | 2.7.1 | `Lg7c;->c(Lorg/json/JSONObject;)V` | 2.7.2 | `Ledc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lg7c;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Luhc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lg7c;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `Lddc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lgb0;->a(Ljava/lang/Object;Lnb3;)Ljava/lang/Object;` | 2.7.2 | `Lec0;->a(Ljava/lang/Object;Lyb3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgb0;->a(Ljava/lang/Object;Lnb3;)Ljava/lang/Object;` | 2.7.4 | `Lkc0;->a(Ljava/lang/Object;Lvd3;)Ljava/lang/Object;` | 0.9992 |
| attachment_file | 2.7.1 | `Lgb0;->a(Ljava/lang/Object;Lnb3;)Ljava/lang/Object;` | 2.7.5 | `Ljv;->a(Ljava/lang/Object;Ldc3;)Ljava/lang/Object;` | 0.9632 |
| attachment_file | 2.7.1 | `Lgb7;->w(Ln05;)Lxdb;` | 2.7.2 | `Lr37;->y(Lr15;)Lijb;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgb7;->w(Ln05;)Lxdb;` | 2.7.4 | `Lod8;->B(La45;)Lqnb;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgb7;->w(Ln05;)Lxdb;` | 2.7.5 | `Ly37;->z(Lv15;)Lpjb;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgmc;->c(Landroid/content/Context;)Lsx6;` | 2.7.2 | `Lbsc;->n(Landroid/content/Context;)Lh07;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgmc;->c(Landroid/content/Context;)Lsx6;` | 2.7.4 | `Lmwc;->l(Landroid/content/Context;)Lb37;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgmc;->c(Landroid/content/Context;)Lsx6;` | 2.7.5 | `Lasc;->n(Landroid/content/Context;)Lp07;` | 1.0000 |
| attachment_file | 2.7.1 | `Lgt0;->E(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 2.7.2 | `Leu0;->z(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lgt0;->E(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 2.7.4 | `Ltv0;->A(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lgt0;->E(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 2.7.5 | `Lfu0;->z(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lgt0;->F(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 2.7.2 | `Leu0;->A(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lgt0;->F(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 2.7.4 | `Ltv0;->B(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lgt0;->F(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 2.7.5 | `Lfu0;->A(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhbc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.2 | `Lhhc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhbc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.4 | `Lslc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhbc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.5 | `Lghc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhjc;->b(Lorg/json/JSONObject;)V` | 2.7.2 | `Lcpc;->b(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhjc;->b(Lorg/json/JSONObject;)V` | 2.7.4 | `Lntc;->b(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhjc;->b(Lorg/json/JSONObject;)V` | 2.7.5 | `Lbpc;->b(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lhjc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 2.7.2 | `Lcpc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 0.9979 |
| attachment_file | 2.7.1 | `Lhjc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 2.7.4 | `Lntc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 0.9975 |
| attachment_file | 2.7.1 | `Lhjc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 2.7.5 | `Lbpc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 0.9975 |
| attachment_file | 2.7.1 | `Lhw2;->w()Ljava/lang/Object;` | 2.7.2 | `Lbx2;->v()Ljava/lang/Object;` | 0.9849 |
| attachment_file | 2.7.1 | `Lhw2;->w()Ljava/lang/Object;` | 2.7.4 | `Lwy2;->v()Ljava/lang/Object;` | 0.9849 |
| attachment_file | 2.7.1 | `Lhw2;->w()Ljava/lang/Object;` | 2.7.5 | `Lgx2;->w()Ljava/lang/Object;` | 0.9849 |
| attachment_file | 2.7.1 | `Lhx1;->a(Lwg4;ZLjava/lang/String;Ldx4;Lnb3;)Ljava/lang/Object;` | 2.7.2 | `Lay1;->a(Lei4;ZLjava/lang/String;Lhy4;Lyb3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lhx1;->a(Lwg4;ZLjava/lang/String;Ldx4;Lnb3;)Ljava/lang/Object;` | 2.7.4 | `Lrz1;->a(Llk4;ZLjava/lang/String;Lp05;Lvd3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lhx1;->a(Lwg4;ZLjava/lang/String;Ldx4;Lnb3;)Ljava/lang/Object;` | 2.7.5 | `Lfy1;->a(Lii4;ZLjava/lang/String;Lly4;Ldc3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Li45;->c(Landroid/content/Context;)Lsx6;` | 2.7.2 | `Lv6c;->n(Landroid/content/Context;)Lh07;` | 1.0000 |
| attachment_file | 2.7.1 | `Li45;->c(Landroid/content/Context;)Lsx6;` | 2.7.4 | `Loe9;->l(Landroid/content/Context;)Lb37;` | 1.0000 |
| attachment_file | 2.7.1 | `Li45;->c(Landroid/content/Context;)Lsx6;` | 2.7.5 | `Lv6c;->n(Landroid/content/Context;)Lp07;` | 1.0000 |
| attachment_file | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.2 | `Loca;-><clinit>()V` | 0.9984 |
| attachment_file | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.5 | `Lxca;-><clinit>()V` | 0.9975 |
| attachment_file | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.4 | `Lqga;-><clinit>()V` | 0.9952 |
| attachment_file | 2.7.1 | `Liw2;->b()[J` | 2.7.2 | `Lcx2;->b()[J` | 0.9918 |
| attachment_file | 2.7.1 | `Liw2;->b()[J` | 2.7.5 | `Lhx2;->b()[J` | 0.9918 |
| attachment_file | 2.7.1 | `Liw2;->b()[J` | 2.7.4 | `Lxy2;->b()[J` | 0.9909 |
| attachment_file | 2.7.1 | `Liw2;->o()I` | 2.7.2 | `Lcx2;->o()I` | 1.0000 |
| attachment_file | 2.7.1 | `Liw2;->o()I` | 2.7.4 | `Lxy2;->o()I` | 1.0000 |
| attachment_file | 2.7.1 | `Liw2;->o()I` | 2.7.5 | `Lhx2;->o()I` | 1.0000 |
| attachment_file | 2.7.1 | `Liw2;->x(Lw16;ILjava/lang/String;Ljava/lang/String;)V` | 2.7.2 | `Lcx2;->y(La46;ILjava/lang/String;Ljava/lang/String;)V` | 0.9951 |
| attachment_file | 2.7.1 | `Liw2;->x(Lw16;ILjava/lang/String;Ljava/lang/String;)V` | 2.7.5 | `Lhx2;->y(Lf46;ILjava/lang/String;Ljava/lang/String;)V` | 0.9951 |
| attachment_file | 2.7.1 | `Liw2;->x(Lw16;ILjava/lang/String;Ljava/lang/String;)V` | 2.7.4 | `Lxy2;->y(Lq66;ILjava/lang/String;Ljava/lang/String;)V` | 0.9950 |
| attachment_file | 2.7.1 | `Lj2c;->g(Ljava/lang/String;)Z` | 2.7.2 | `Lf8c;->g(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lj2c;->g(Ljava/lang/String;)Z` | 2.7.4 | `Lscc;->g(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lj2c;->g(Ljava/lang/String;)Z` | 2.7.5 | `Lf8c;->g(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Ljd2;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lfe2;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9885 |
| attachment_file | 2.7.1 | `Ljd2;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lke2;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9885 |
| attachment_file | 2.7.1 | `Ljd2;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lwf2;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9872 |
| attachment_file | 2.7.1 | `Lk0c;->a(Lorg/json/JSONObject;)V` | 2.7.2 | `Lg6c;->a(Lorg/json/JSONObject;)V` | 0.9996 |
| attachment_file | 2.7.1 | `Lk0c;->a(Lorg/json/JSONObject;)V` | 2.7.4 | `Luac;->a(Lorg/json/JSONObject;)V` | 0.9996 |
| attachment_file | 2.7.1 | `Lk0c;->a(Lorg/json/JSONObject;)V` | 2.7.5 | `Lg6c;->a(Lorg/json/JSONObject;)V` | 0.9996 |
| attachment_file | 2.7.1 | `Lk4;->w()Ljava/lang/Object;` | 2.7.2 | `Ln4;->v()Ljava/lang/Object;` | 0.9789 |
| attachment_file | 2.7.1 | `Lk4;->w()Ljava/lang/Object;` | 2.7.4 | `Lm4;->v()Ljava/lang/Object;` | 0.9789 |
| attachment_file | 2.7.1 | `Lk4;->w()Ljava/lang/Object;` | 2.7.5 | `Ln4;->w()Ljava/lang/Object;` | 0.9789 |
| attachment_file | 2.7.1 | `Lk9c;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lq5c;)V` | 2.7.2 | `Lkfc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Llbc;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lk9c;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lq5c;)V` | 2.7.4 | `Lyjc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lbgc;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lk9c;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lq5c;)V` | 2.7.5 | `Ljfc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lkbc;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lkg4;->a(Landroid/net/Uri;)Ljava/io/File;` | 2.7.2 | `Lsh4;->a(Landroid/net/Uri;)Ljava/io/File;` | 1.0000 |
| attachment_file | 2.7.1 | `Lkg4;->a(Landroid/net/Uri;)Ljava/io/File;` | 2.7.4 | `Lzj4;->a(Landroid/net/Uri;)Ljava/io/File;` | 1.0000 |
| attachment_file | 2.7.1 | `Lkg4;->a(Landroid/net/Uri;)Ljava/io/File;` | 2.7.5 | `Lwh4;->a(Landroid/net/Uri;)Ljava/io/File;` | 1.0000 |
| attachment_file | 2.7.1 | `Lklc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.2 | `Lfrc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lklc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.4 | `Lqvc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lklc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.5 | `Lerc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lky1;->w()Ljava/lang/Object;` | 2.7.2 | `Ldz1;->v()Ljava/lang/Object;` | 0.9931 |
| attachment_file | 2.7.1 | `Lky1;->w()Ljava/lang/Object;` | 2.7.4 | `Lu02;->v()Ljava/lang/Object;` | 0.9931 |
| attachment_file | 2.7.1 | `Lky1;->w()Ljava/lang/Object;` | 2.7.5 | `Liz1;->w()Ljava/lang/Object;` | 0.9931 |
| attachment_file | 2.7.1 | `Llcc;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lgcc;` | 2.7.2 | `Llic;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lgic;` | 0.9946 |
| attachment_file | 2.7.1 | `Llcc;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lgcc;` | 2.7.5 | `Lkic;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lfic;` | 0.9946 |
| attachment_file | 2.7.1 | `Llcc;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lgcc;` | 2.7.4 | `Lvmc;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lqmc;` | 0.9928 |
| attachment_file | 2.7.1 | `Llcc;->c(La79;)Lorg/json/JSONObject;` | 2.7.2 | `Llic;->c(Lng9;)Lorg/json/JSONObject;` | 0.9980 |
| attachment_file | 2.7.1 | `Llcc;->c(La79;)Lorg/json/JSONObject;` | 2.7.4 | `Lvmc;->c(Lf99;)Lorg/json/JSONObject;` | 0.9980 |
| attachment_file | 2.7.1 | `Llcc;->c(La79;)Lorg/json/JSONObject;` | 2.7.5 | `Lkic;->c(Lug9;)Lorg/json/JSONObject;` | 0.9980 |
| attachment_file | 2.7.1 | `Llcc;->f(Z)V` | 2.7.2 | `Llic;->f(Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Llcc;->f(Z)V` | 2.7.4 | `Lvmc;->f(Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Llcc;->f(Z)V` | 2.7.5 | `Lkic;->f(Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Llcc;->h()V` | 2.7.2 | `Llic;->h()V` | 1.0000 |
| attachment_file | 2.7.1 | `Llcc;->h()V` | 2.7.5 | `Lkic;->h()V` | 1.0000 |
| attachment_file | 2.7.1 | `Llcc;->h()V` | 2.7.4 | `Lvmc;->h()V` | 0.9991 |
| attachment_file | 2.7.1 | `Lle3;->b(Lfz9;)Lb25;` | 2.7.2 | `Lye3;->b(Lk4a;)Lg35;` | 1.0000 |
| attachment_file | 2.7.1 | `Lle3;->b(Lfz9;)Lb25;` | 2.7.4 | `Lwg3;->b(Lj8a;)Lp55;` | 1.0000 |
| attachment_file | 2.7.1 | `Lle3;->b(Lfz9;)Lb25;` | 2.7.5 | `Ldf3;->b(Lr4a;)Ll35;` | 1.0000 |
| attachment_file | 2.7.1 | `Llf9;->N(Lw52;Ln05;I)Ljdb;` | 2.7.2 | `Ln28;->O(Lt62;Lr15;I)Ltib;` | 0.9912 |
| attachment_file | 2.7.1 | `Llf9;->N(Lw52;Ln05;I)Ljdb;` | 2.7.4 | `Ljxc;->G(Lk82;La45;I)Lbnb;` | 0.9912 |
| attachment_file | 2.7.1 | `Llf9;->N(Lw52;Ln05;I)Ljdb;` | 2.7.5 | `Lda8;->H(Ly62;Lv15;I)Lajb;` | 0.9912 |
| attachment_file | 2.7.1 | `Llf9;->P(Ln05;)Z` | 2.7.2 | `Ln28;->Q(Lr15;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Llf9;->P(Ln05;)Z` | 2.7.4 | `Ljxc;->I(La45;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Llf9;->P(Ln05;)Z` | 2.7.5 | `Lda8;->J(Lv15;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Llg4;->toString()Ljava/lang/String;` | 2.7.2 | `Lth4;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Llg4;->toString()Ljava/lang/String;` | 2.7.4 | `Lak4;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Llg4;->toString()Ljava/lang/String;` | 2.7.5 | `Lxh4;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lm80;->a(Ljava/lang/String;)Lm80;` | 2.7.2 | `Lj90;->a(Ljava/lang/String;)Lj90;` | 1.0000 |
| attachment_file | 2.7.1 | `Lm80;->a(Ljava/lang/String;)Lm80;` | 2.7.4 | `Lp90;->a(Ljava/lang/String;)Lp90;` | 1.0000 |
| attachment_file | 2.7.1 | `Lm80;->a(Ljava/lang/String;)Lm80;` | 2.7.5 | `Lm90;->a(Ljava/lang/String;)Lm90;` | 1.0000 |
| attachment_file | 2.7.1 | `Lmnc;-><init>(Lvec;Landroid/content/Context;Ljp5;)V` | 2.7.2 | `Lhtc;-><init>(Lskc;Landroid/content/Context;Lcr5;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lmnc;-><init>(Lvec;Landroid/content/Context;Ljp5;)V` | 2.7.4 | `Lsxc;-><init>(Ldpc;Landroid/content/Context;Lnt5;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lmnc;-><init>(Lvec;Landroid/content/Context;Ljp5;)V` | 2.7.5 | `Lgtc;-><init>(Lrkc;Landroid/content/Context;Lhr5;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lnjc;->b(Ljava/lang/Object;Lkcc;)V` | 2.7.2 | `Lipc;->b(Ljava/lang/Object;Lkic;)V` | 0.9930 |
| attachment_file | 2.7.1 | `Lnjc;->b(Ljava/lang/Object;Lkcc;)V` | 2.7.4 | `Lttc;->b(Ljava/lang/Object;Lumc;)V` | 0.9930 |
| attachment_file | 2.7.1 | `Lnjc;->b(Ljava/lang/Object;Lkcc;)V` | 2.7.5 | `Lhpc;->b(Ljava/lang/Object;Ljic;)V` | 0.9930 |
| attachment_file | 2.7.1 | `Lnjc;->d()V` | 2.7.2 | `Lipc;->d()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lnjc;->d()V` | 2.7.4 | `Lttc;->d()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lnjc;->d()V` | 2.7.5 | `Lhpc;->d()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lnn7;->b(Lqdb;Leg7;Ljava/util/List;Lbx4;Ln05;I)V` | 2.7.2 | `Ly27;->a(Lcjb;Lyj7;Ljava/util/List;Lfy4;Lr15;I)V` | 0.9958 |
| attachment_file | 2.7.1 | `Lnn7;->b(Lqdb;Leg7;Ljava/util/List;Lbx4;Ln05;I)V` | 2.7.4 | `Lkb8;->a(Lknb;Lrl7;Ljava/util/List;Ln05;La45;I)V` | 0.9958 |
| attachment_file | 2.7.1 | `Lnn7;->b(Lqdb;Leg7;Ljava/util/List;Lbx4;Ln05;I)V` | 2.7.5 | `Ls27;->f(Ljjb;Lfk7;Ljava/util/List;Ljy4;Lv15;I)V` | 0.9948 |
| attachment_file | 2.7.1 | `Lnn7;->c(Lqdb;Leg7;Lbx4;Ln05;I)V` | 2.7.2 | `Ly27;->b(Lcjb;Lyj7;Lfy4;Lr15;I)V` | 0.9961 |
| attachment_file | 2.7.1 | `Lnn7;->c(Lqdb;Leg7;Lbx4;Ln05;I)V` | 2.7.4 | `Lkb8;->b(Lknb;Lrl7;Ln05;La45;I)V` | 0.9961 |
| attachment_file | 2.7.1 | `Lnn7;->c(Lqdb;Leg7;Lbx4;Ln05;I)V` | 2.7.5 | `Ls27;->g(Ljjb;Lfk7;Ljy4;Lv15;I)V` | 0.9961 |
| attachment_file | 2.7.1 | `Lnv5;-><clinit>()V` | 2.7.2 | `Lrx5;-><clinit>()V` | 0.9994 |
| attachment_file | 2.7.1 | `Lnv5;-><clinit>()V` | 2.7.4 | `Ld06;-><clinit>()V` | 0.9994 |
| attachment_file | 2.7.1 | `Lnv5;-><clinit>()V` | 2.7.5 | `Lwx5;-><clinit>()V` | 0.9994 |
| attachment_file | 2.7.1 | `Lo5c;->run()V` | 2.7.2 | `Ljbc;->run()V` | 0.9758 |
| attachment_file | 2.7.1 | `Lo5c;->run()V` | 2.7.4 | `Lzfc;->run()V` | 0.9758 |
| attachment_file | 2.7.1 | `Lo5c;->run()V` | 2.7.5 | `Libc;->run()V` | 0.9758 |
| attachment_file | 2.7.1 | `Lo7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lq7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7982 |
| attachment_file | 2.7.1 | `Lo7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lp7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7966 |
| attachment_file | 2.7.1 | `Lo7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lq7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7966 |
| attachment_file | 2.7.1 | `Lodb;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lzib;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9977 |
| attachment_file | 2.7.1 | `Lodb;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lhnb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9977 |
| attachment_file | 2.7.1 | `Lodb;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lgjb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9977 |
| attachment_file | 2.7.1 | `Loq0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lkr0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7660 |
| attachment_file | 2.7.1 | `Loq0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lat0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7660 |
| attachment_file | 2.7.1 | `Loq0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Llr0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7660 |
| attachment_file | 2.7.1 | `Low2;-><init>()V` | 2.7.2 | `Lix2;-><init>()V` | 0.9928 |
| attachment_file | 2.7.1 | `Low2;-><init>()V` | 2.7.5 | `Lnx2;-><init>()V` | 0.9928 |
| attachment_file | 2.7.1 | `Low2;-><init>()V` | 2.7.4 | `Lez2;-><init>()V` | 0.9848 |
| attachment_file | 2.7.1 | `Lp4;->i(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Ls4;->u(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9914 |
| attachment_file | 2.7.1 | `Lp4;->i(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lr4;->u(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9914 |
| attachment_file | 2.7.1 | `Lp4;->i(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Ls4;->u(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9914 |
| attachment_file | 2.7.1 | `Lpa7;->c(Ljava/lang/String;Ln05;I)V` | 2.7.2 | `Lo37;->c(Ljava/lang/String;Lr15;I)V` | 0.9961 |
| attachment_file | 2.7.1 | `Lpa7;->c(Ljava/lang/String;Ln05;I)V` | 2.7.4 | `Lxz9;->b(Ljava/lang/String;La45;I)V` | 0.9961 |
| attachment_file | 2.7.1 | `Lpa7;->c(Ljava/lang/String;Ln05;I)V` | 2.7.5 | `Ls37;->e(Ljava/lang/String;Lv15;I)V` | 0.9961 |
| attachment_file | 2.7.1 | `Lpa7;->f(Ljava/lang/String;Ljava/lang/String;[Ljava/io/File;)Lpq7;` | 2.7.2 | `Lo37;->f(Ljava/lang/String;Ljava/lang/String;[Ljava/io/File;)Lxt7;` | 1.0000 |
| attachment_file | 2.7.1 | `Lpa7;->f(Ljava/lang/String;Ljava/lang/String;[Ljava/io/File;)Lpq7;` | 2.7.4 | `Lao8;->f(Ljava/lang/String;Ljava/lang/String;[Ljava/io/File;)Lrv7;` | 1.0000 |
| attachment_file | 2.7.1 | `Lpa7;->f(Ljava/lang/String;Ljava/lang/String;[Ljava/io/File;)Lpq7;` | 2.7.5 | `Ls37;->h(Ljava/lang/String;Ljava/lang/String;[Ljava/io/File;)Leu7;` | 1.0000 |
| attachment_file | 2.7.1 | `Lpa7;->q(Lcom/apm/insight/MonitorCrash;Ljava/lang/Throwable;Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;)V` | 2.7.2 | `Lo37;->o(Lcom/apm/insight/MonitorCrash;Ljava/lang/Throwable;Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpa7;->q(Lcom/apm/insight/MonitorCrash;Ljava/lang/Throwable;Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;)V` | 2.7.4 | `Lwo8;->l(Lcom/apm/insight/MonitorCrash;Ljava/lang/Throwable;Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpa7;->q(Lcom/apm/insight/MonitorCrash;Ljava/lang/Throwable;Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;)V` | 2.7.5 | `Ls37;->r(Lcom/apm/insight/MonitorCrash;Ljava/lang/Throwable;Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpa;->a(Ljava/lang/Object;Lnb3;)Ljava/lang/Object;` | 2.7.2 | `Lqa;->a(Ljava/lang/Object;Lyb3;)Ljava/lang/Object;` | 0.9959 |
| attachment_file | 2.7.1 | `Lpa;->a(Ljava/lang/Object;Lnb3;)Ljava/lang/Object;` | 2.7.4 | `Lsa;->a(Ljava/lang/Object;Lvd3;)Ljava/lang/Object;` | 0.9959 |
| attachment_file | 2.7.1 | `Lpa;->a(Ljava/lang/Object;Lnb3;)Ljava/lang/Object;` | 2.7.5 | `Lra;->a(Ljava/lang/Object;Ldc3;)Ljava/lang/Object;` | 0.9959 |
| attachment_file | 2.7.1 | `Lpdb;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lbjb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lpdb;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Ljnb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lpdb;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lijb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lpfc;->a(Lx3c;)V` | 2.7.2 | `Lllc;->a(Lt9c;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpfc;->a(Lx3c;)V` | 2.7.4 | `Lwpc;->a(Lgec;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpfc;->a(Lx3c;)V` | 2.7.5 | `Lklc;->a(Lt9c;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lph2;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lli2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9943 |
| attachment_file | 2.7.1 | `Lph2;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lbk2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9943 |
| attachment_file | 2.7.1 | `Lph2;->r(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqi2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9943 |
| attachment_file | 2.7.1 | `Lpp;->run()V` | 2.7.2 | `Lyp;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpp;->run()V` | 2.7.4 | `Laq;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lpp;->run()V` | 2.7.5 | `Lzp;->run()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lqe7;-><clinit>()V` | 2.7.2 | `Lpi7;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lqe7;-><clinit>()V` | 2.7.4 | `Lik7;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lqe7;-><clinit>()V` | 2.7.5 | `Lwi7;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lqz;-><clinit>()V` | 2.7.2 | `Lqz;-><clinit>()V` | 0.9994 |
| attachment_file | 2.7.1 | `Lqz;-><clinit>()V` | 2.7.4 | `Lvz;-><clinit>()V` | 0.9981 |
| attachment_file | 2.7.1 | `Lqz;-><clinit>()V` | 2.7.5 | `Luz;-><clinit>()V` | 0.9981 |
| attachment_file | 2.7.1 | `Lrd2;->B(Loj2;Lob3;)Ljava/lang/Object;` | 2.7.2 | `Loe2;->B(Lik2;Lzb3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lrd2;->B(Loj2;Lob3;)Ljava/lang/Object;` | 2.7.4 | `Lfg2;->B(Lyl2;Lwd3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lrd2;->B(Loj2;Lob3;)Ljava/lang/Object;` | 2.7.5 | `Lte2;->B(Lnk2;Lec3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.1 | `Lrq6;->c(Lorg/json/JSONObject;)Z` | 2.7.2 | `Lps6;->c(Lorg/json/JSONObject;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lrq6;->c(Lorg/json/JSONObject;)Z` | 2.7.4 | `Lpv6;->c(Lorg/json/JSONObject;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lrq6;->c(Lorg/json/JSONObject;)Z` | 2.7.5 | `Lvs6;->c(Lorg/json/JSONObject;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lrq6;->d(Lorg/json/JSONObject;JZLjava/lang/String;ZLjava/lang/String;)Z` | 2.7.2 | `Lps6;->d(Lorg/json/JSONObject;JZLjava/lang/String;ZLjava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lrq6;->d(Lorg/json/JSONObject;JZLjava/lang/String;ZLjava/lang/String;)Z` | 2.7.4 | `Lpv6;->d(Lorg/json/JSONObject;JZLjava/lang/String;ZLjava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lrq6;->d(Lorg/json/JSONObject;JZLjava/lang/String;ZLjava/lang/String;)Z` | 2.7.5 | `Lvs6;->d(Lorg/json/JSONObject;JZLjava/lang/String;ZLjava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Ls1c;-><init>()V` | 2.7.2 | `Lo7c;-><init>()V` | 0.9866 |
| attachment_file | 2.7.1 | `Ls1c;-><init>()V` | 2.7.4 | `Lccc;-><init>()V` | 0.9866 |
| attachment_file | 2.7.1 | `Ls1c;-><init>()V` | 2.7.5 | `Lo7c;-><init>()V` | 0.9866 |
| attachment_file | 2.7.1 | `Ls7c;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.2 | `Lqdc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ls7c;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.4 | `Lgic;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ls7c;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.5 | `Lpdc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ls9c;->c(Landroid/content/Context;)Lsx6;` | 2.7.2 | `Lacc;->n(Landroid/content/Context;)Lh07;` | 1.0000 |
| attachment_file | 2.7.1 | `Ls9c;->c(Landroid/content/Context;)Lsx6;` | 2.7.4 | `Lrgc;->l(Landroid/content/Context;)Lb37;` | 1.0000 |
| attachment_file | 2.7.1 | `Ls9c;->c(Landroid/content/Context;)Lsx6;` | 2.7.5 | `Lzbc;->n(Landroid/content/Context;)Lp07;` | 1.0000 |
| attachment_file | 2.7.1 | `Lsdb;->b(ZLjava/lang/String;Landroid/net/Uri;Lbx4;Ln05;I)V` | 2.7.2 | `Lejb;->b(ZLjava/lang/String;Landroid/net/Uri;Lfy4;Lr15;I)V` | 0.9912 |
| attachment_file | 2.7.1 | `Lsdb;->b(ZLjava/lang/String;Landroid/net/Uri;Lbx4;Ln05;I)V` | 2.7.4 | `Lmnb;->b(ZLjava/lang/String;Landroid/net/Uri;Ln05;La45;I)V` | 0.9912 |
| attachment_file | 2.7.1 | `Lsdb;->b(ZLjava/lang/String;Landroid/net/Uri;Lbx4;Ln05;I)V` | 2.7.5 | `Lljb;->b(ZLjava/lang/String;Landroid/net/Uri;Ljy4;Lv15;I)V` | 0.9912 |
| attachment_file | 2.7.1 | `Lse7;->toString()Ljava/lang/String;` | 2.7.2 | `Lri7;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lse7;->toString()Ljava/lang/String;` | 2.7.4 | `Lkk7;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Lse7;->toString()Ljava/lang/String;` | 2.7.5 | `Lyi7;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.1 | `Ltlc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.2 | `Lorc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ltlc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.4 | `Lzvc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ltlc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.5 | `Lnrc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ltp;->onReady()V` | 2.7.2 | `Ldq;->onReady()V` | 1.0000 |
| attachment_file | 2.7.1 | `Ltp;->onReady()V` | 2.7.5 | `Leq;->onReady()V` | 1.0000 |
| attachment_file | 2.7.1 | `Ltp;->onReady()V` | 2.7.4 | `Lfq;->onReady()V` | 0.9942 |
| attachment_file | 2.7.1 | `Ltp;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Ldq;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Ltp;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Leq;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu1c;->a(Lu14;)V` | 2.7.2 | `Lq7c;->a(Lq24;)V` | 0.9929 |
| attachment_file | 2.7.1 | `Lu1c;->a(Lu14;)V` | 2.7.4 | `Ldcc;->a(Lq44;)V` | 0.9929 |
| attachment_file | 2.7.1 | `Lu1c;->a(Lu14;)V` | 2.7.5 | `Lq7c;->a(Lt24;)V` | 0.9929 |
| attachment_file | 2.7.1 | `Lu3c;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Lq9c;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu3c;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Ldec;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu3c;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lq9c;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu73;->e0(Landroid/content/Context;Ljava/io/File;)Landroid/net/Uri;` | 2.7.2 | `Lysc;->E(Landroid/content/Context;Ljava/io/File;)Landroid/net/Uri;` | 1.0000 |
| attachment_file | 2.7.1 | `Lu73;->e0(Landroid/content/Context;Ljava/io/File;)Landroid/net/Uri;` | 2.7.4 | `Lqwc;->G(Landroid/content/Context;Ljava/io/File;)Landroid/net/Uri;` | 1.0000 |
| attachment_file | 2.7.1 | `Lu73;->e0(Landroid/content/Context;Ljava/io/File;)Landroid/net/Uri;` | 2.7.5 | `Lxsc;->I(Landroid/content/Context;Ljava/io/File;)Landroid/net/Uri;` | 1.0000 |
| attachment_file | 2.7.1 | `Lu8c;-><clinit>()V` | 2.7.2 | `Ltec;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu8c;-><clinit>()V` | 2.7.4 | `Lijc;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu8c;-><clinit>()V` | 2.7.5 | `Lsec;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu8c;->a()V` | 2.7.2 | `Ltec;->a()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu8c;->a()V` | 2.7.4 | `Lijc;->a()V` | 1.0000 |
| attachment_file | 2.7.1 | `Lu8c;->a()V` | 2.7.5 | `Lsec;->a()V` | 1.0000 |
| attachment_file | 2.7.1 | `Luhc;->c(Lorg/json/JSONObject;)V` | 2.7.2 | `Lpnc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Luhc;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Lasc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Luhc;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `Lonc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Luk6;->a(Lorg/json/JSONObject;)V` | 2.7.2 | `Ltm6;->a(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Luk6;->a(Lorg/json/JSONObject;)V` | 2.7.4 | `Lmp6;->a(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Luk6;->a(Lorg/json/JSONObject;)V` | 2.7.5 | `Lzm6;->a(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lun7;->b(Lbx4;Ln05;I)V` | 2.7.2 | `Li37;->a(Lfy4;Lr15;I)V` | 0.9966 |
| attachment_file | 2.7.1 | `Lun7;->b(Lbx4;Ln05;I)V` | 2.7.4 | `Lec8;->e(Ln05;La45;I)V` | 0.9966 |
| attachment_file | 2.7.1 | `Lun7;->b(Lbx4;Ln05;I)V` | 2.7.5 | `Lg37;->a(Ljy4;Lv15;I)V` | 0.9966 |
| attachment_file | 2.7.1 | `Lv1c;->a(Ljava/lang/String;Ljava/io/File;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/HashMap;)Z` | 2.7.2 | `Lr7c;->a(Ljava/lang/String;Ljava/io/File;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/HashMap;)Z` | 0.9925 |
| attachment_file | 2.7.1 | `Lv1c;->a(Ljava/lang/String;Ljava/io/File;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/HashMap;)Z` | 2.7.4 | `Lecc;->a(Ljava/lang/String;Ljava/io/File;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/HashMap;)Z` | 0.9925 |
| attachment_file | 2.7.1 | `Lv1c;->a(Ljava/lang/String;Ljava/io/File;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/HashMap;)Z` | 2.7.5 | `Lr7c;->a(Ljava/lang/String;Ljava/io/File;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/HashMap;)Z` | 0.9925 |
| attachment_file | 2.7.1 | `Lvjc;->c(Lorg/json/JSONObject;)V` | 2.7.2 | `Lqpc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lvjc;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `Lppc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lvjc;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Lbuc;->c(Lorg/json/JSONObject;)V` | 0.9853 |
| attachment_file | 2.7.1 | `Lwac;->c(Lorg/json/JSONObject;)V` | 2.7.2 | `Lxgc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lwac;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Lilc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lwac;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `Lwgc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.1 | `Lwdc;-><init>()V` | 2.7.2 | `Ltjc;-><init>()V` | 0.9829 |
| attachment_file | 2.7.1 | `Lwdc;-><init>()V` | 2.7.5 | `Lsjc;-><init>()V` | 0.9829 |
| attachment_file | 2.7.1 | `Lwdc;-><init>()V` | 2.7.4 | `Leoc;-><init>()V` | 0.9774 |
| attachment_file | 2.7.1 | `Lwdc;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Ltjc;->onRefresh(Lorg/json/JSONObject;Z)V` | 0.9955 |
| attachment_file | 2.7.1 | `Lwdc;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lsjc;->onRefresh(Lorg/json/JSONObject;Z)V` | 0.9955 |
| attachment_file | 2.7.1 | `Lwdc;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Leoc;->onRefresh(Lorg/json/JSONObject;Z)V` | 0.9911 |
| attachment_file | 2.7.1 | `Lxec;->a(Landroid/content/Context;Ljava/lang/String;)Landroid/content/SharedPreferences;` | 2.7.2 | `Lukc;->a(Landroid/content/Context;Ljava/lang/String;)Landroid/content/SharedPreferences;` | 1.0000 |
| attachment_file | 2.7.1 | `Lxec;->a(Landroid/content/Context;Ljava/lang/String;)Landroid/content/SharedPreferences;` | 2.7.4 | `Lfpc;->a(Landroid/content/Context;Ljava/lang/String;)Landroid/content/SharedPreferences;` | 1.0000 |
| attachment_file | 2.7.1 | `Lxec;->a(Landroid/content/Context;Ljava/lang/String;)Landroid/content/SharedPreferences;` | 2.7.5 | `Ltkc;->a(Landroid/content/Context;Ljava/lang/String;)Landroid/content/SharedPreferences;` | 1.0000 |
| attachment_file | 2.7.1 | `Lz1c;->d(Lf99;)Z` | 2.7.2 | `Lv7c;->d(Lrc9;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lz1c;->d(Lf99;)Z` | 2.7.5 | `Lv7c;->d(Lyc9;)Z` | 1.0000 |
| attachment_file | 2.7.1 | `Lz1c;->d(Lf99;)Z` | 2.7.4 | `Licc;->d(Lgf9;)Z` | 0.9870 |
| attachment_file | 2.7.1 | `Lza7;->g(Leg7;Lwe7;Ldx4;Ldx4;Ljava/util/Map;Ldx4;Ldx4;Ldx4;Ln05;I)V` | 2.7.2 | `Lq37;->e(Lyj7;Lvi7;Lhy4;Lhy4;Ljava/util/Map;Lhy4;Lhy4;Lhy4;Lr15;I)V` | 0.9971 |
| attachment_file | 2.7.1 | `Lza7;->g(Leg7;Lwe7;Ldx4;Ldx4;Ljava/util/Map;Ldx4;Ldx4;Ldx4;Ln05;I)V` | 2.7.4 | `Lsc8;->e(Lrl7;Lok7;Lp05;Lp05;Ljava/util/Map;Lp05;Lp05;Lp05;La45;I)V` | 0.9971 |
| attachment_file | 2.7.1 | `Lza7;->g(Leg7;Lwe7;Ldx4;Ldx4;Ljava/util/Map;Ldx4;Ldx4;Ldx4;Ln05;I)V` | 2.7.5 | `Lw37;->e(Lfk7;Lcj7;Lly4;Lly4;Ljava/util/Map;Lly4;Lly4;Lly4;Lv15;I)V` | 0.9971 |
| attachment_file | 2.7.1 | `Lzd7;-><clinit>()V` | 2.7.2 | `Lyh7;-><clinit>()V` | 0.9843 |
| attachment_file | 2.7.1 | `Lzd7;-><clinit>()V` | 2.7.4 | `Lrj7;-><clinit>()V` | 0.9843 |
| attachment_file | 2.7.1 | `Lzd7;-><clinit>()V` | 2.7.5 | `Lfi7;-><clinit>()V` | 0.9843 |
| attachment_file | 2.7.1 | `Lzdc;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Lwjc;->onRefresh(Lorg/json/JSONObject;Z)V` | 0.9578 |
| attachment_file | 2.7.1 | `Lzdc;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lhoc;->onRefresh(Lorg/json/JSONObject;Z)V` | 0.9578 |
| attachment_file | 2.7.1 | `Lzdc;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lvjc;->onRefresh(Lorg/json/JSONObject;Z)V` | 0.9578 |
| attachment_file | 2.7.1 | `Lzy4;->run()V` | 2.7.2 | `Ld05;->run()V` | 0.9982 |
| attachment_file | 2.7.1 | `Lzy4;->run()V` | 2.7.5 | `Lh05;->run()V` | 0.9982 |
| attachment_file | 2.7.1 | `Lzy4;->run()V` | 2.7.4 | `Ll25;->run()V` | 0.9971 |
| attachment_file | 2.7.2 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 2.7.4 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `->getTokenFromWX(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.4 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.5 | `->sendChooseCardFromWX(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.4 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.5 | `->sendFinderOpenFeed(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.4 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 2.7.5 | `->sendOpenBusiLuckyMoney(Landroid/content/Context;Landroid/os/Bundle;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.4 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.5 | `->sendOpenBusinessWebview(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.4 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 2.7.5 | `->sendToWxaRedirectingPage(Landroid/content/Context;Lcom/tencent/mm/opensdk/modelbase/BaseReq;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `La9c;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Lndc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `La9c;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `La9c;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lacc;->n(Landroid/content/Context;)Lh07;` | 2.7.4 | `Lrgc;->l(Landroid/content/Context;)Lb37;` | 1.0000 |
| attachment_file | 2.7.2 | `Lacc;->n(Landroid/content/Context;)Lh07;` | 2.7.5 | `Lzbc;->n(Landroid/content/Context;)Lp07;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->b()Lsh4;` | 2.7.4 | `Landroidx/core/content/FileProvider;->b()Lzj4;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->b()Lsh4;` | 2.7.5 | `Landroidx/core/content/FileProvider;->b()Lwh4;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lsh4;` | 2.7.4 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lzj4;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lsh4;` | 2.7.5 | `Landroidx/core/content/FileProvider;->c(Landroid/content/Context;Ljava/lang/String;)Lwh4;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 2.7.4 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 2.7.5 | `Landroidx/core/content/FileProvider;->delete(Landroid/net/Uri;Ljava/lang/String;[Ljava/lang/String;)I` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 2.7.4 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 2.7.5 | `Landroidx/core/content/FileProvider;->getType(Landroid/net/Uri;)Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 2.7.4 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 2.7.5 | `Landroidx/core/content/FileProvider;->openFile(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 2.7.4 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 1.0000 |
| attachment_file | 2.7.2 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 2.7.5 | `Landroidx/core/content/FileProvider;->query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;` | 1.0000 |
| attachment_file | 2.7.2 | `Lay1;->a(Lei4;ZLjava/lang/String;Lhy4;Lyb3;)Ljava/lang/Object;` | 2.7.4 | `Lrz1;->a(Llk4;ZLjava/lang/String;Lp05;Lvd3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lay1;->a(Lei4;ZLjava/lang/String;Lhy4;Lyb3;)Ljava/lang/Object;` | 2.7.5 | `Lfy1;->a(Lii4;ZLjava/lang/String;Lly4;Ldc3;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbjb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Ljnb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbjb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lijb;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbs0;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lcs0;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbs0;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lqt0;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9963 |
| attachment_file | 2.7.2 | `Lbsc;->n(Landroid/content/Context;)Lh07;` | 2.7.4 | `Lmwc;->l(Landroid/content/Context;)Lb37;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbsc;->n(Landroid/content/Context;)Lh07;` | 2.7.5 | `Lasc;->n(Landroid/content/Context;)Lp07;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbx2;->v()Ljava/lang/Object;` | 2.7.4 | `Lwy2;->v()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lbx2;->v()Ljava/lang/Object;` | 2.7.5 | `Lgx2;->w()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lc82;->u(Ll12;)V` | 2.7.4 | `Lt92;->u(Lc32;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lc82;->u(Ll12;)V` | 2.7.5 | `Lh82;->u(Lq12;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lc9;->run()V` | 2.7.5 | `Ld9;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lc9;->run()V` | 2.7.4 | `Ld9;->run()V` | 0.7652 |
| attachment_file | 2.7.2 | `Lcn/fly/verify/df$1;->run()V` | 2.7.4 | `Lcn/fly/verify/df$1;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcn/fly/verify/df$1;->run()V` | 2.7.5 | `Lcn/fly/verify/df$1;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 2.7.4 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 2.7.5 | `Lcn/fly/verify/util/i;->a(Landroid/content/Context;Ljava/util/List;)Ljava/util/List;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 2.7.4 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 2.7.5 | `Lcom/apm/insight/c;->d(Z)Lorg/json/JSONObject;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/bytedance/apm/internal/ApmDelegate$8;->uploadFiles(Ljava/lang/String;Ljava/util/List;Ljava/util/Map;)Lcom/bytedance/services/apm/api/HttpResponse;` | 2.7.5 | `Lcom/bytedance/apm/internal/ApmDelegate$8;->uploadFiles(Ljava/lang/String;Ljava/util/List;Ljava/util/Map;)Lcom/bytedance/services/apm/api/HttpResponse;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.4 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.5 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l1111l111111Il(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.4 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 0.9965 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 2.7.5 | `Lcom/ishumei/smantifraud/l11l111l1lll;->l111l11111lIl(Ljava/lang/String;)Lcom/ishumei/smantifraud/l11l111l11Il;` | 0.9965 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l11l1Il;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l11llI1l;->l1111l111111Il(Landroid/content/Context;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 2.7.4 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 2.7.5 | `Lcom/ishumei/smantifraud/l1l1l1ll;->l1111l111111Il()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 2.7.4 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 2.7.5 | `Lcom/tencent/liteav/audio/musicdecoder/MediaCodecBridge;->setDataSource(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 2.7.4 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 2.7.5 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->sendInternal(JLcom/tencent/liteav/base/http/HttpClientAndroid$e;Z)J` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 2.7.4 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 2.7.5 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->uploadFile(JLjava/lang/String;Ljava/lang/String;[BLjava/util/Map;ZZLjava/lang/String;[B[B)J` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 2.7.4 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 2.7.5 | `Lcom/tencent/liteav/base/http/HttpClientAndroid;->writeRequestBody(Lcom/tencent/liteav/base/http/HttpClientAndroid$e;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 2.7.4 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 2.7.5 | `Lcom/tencent/mm/opensdk/utils/a;-><clinit>()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 2.7.4 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 2.7.5 | `Lcom/tencent/mmkv/MMKV;->s(Landroid/content/Context;Ljava/lang/String;IILjava/lang/String;)Lcom/tencent/mmkv/MMKV;` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 2.7.4 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 2.7.5 | `Lcom/tencent/trtc/hardwareearmonitor/oplus/HardwareEarMonitorOplus;->authCheck(Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcpc;->b(Lorg/json/JSONObject;)V` | 2.7.4 | `Lntc;->b(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcpc;->b(Lorg/json/JSONObject;)V` | 2.7.5 | `Lbpc;->b(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcpc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 2.7.4 | `Lntc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 0.9996 |
| attachment_file | 2.7.2 | `Lcpc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 2.7.5 | `Lbpc;->d(Lcom/bytedance/services/apm/api/HttpResponse;)Z` | 0.9996 |
| attachment_file | 2.7.2 | `Lcx2;->b()[J` | 2.7.5 | `Lhx2;->b()[J` | 1.0000 |
| attachment_file | 2.7.2 | `Lcx2;->b()[J` | 2.7.4 | `Lxy2;->b()[J` | 0.9990 |
| attachment_file | 2.7.2 | `Lcx2;->o()I` | 2.7.4 | `Lxy2;->o()I` | 1.0000 |
| attachment_file | 2.7.2 | `Lcx2;->o()I` | 2.7.5 | `Lhx2;->o()I` | 1.0000 |
| attachment_file | 2.7.2 | `Lcx2;->y(La46;ILjava/lang/String;Ljava/lang/String;)V` | 2.7.5 | `Lhx2;->y(Lf46;ILjava/lang/String;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lcx2;->y(La46;ILjava/lang/String;Ljava/lang/String;)V` | 2.7.4 | `Lxy2;->y(Lq66;ILjava/lang/String;Ljava/lang/String;)V` | 0.9999 |
| attachment_file | 2.7.2 | `Ld05;->run()V` | 2.7.5 | `Lh05;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Ld05;->run()V` | 2.7.4 | `Ll25;->run()V` | 0.9989 |
| attachment_file | 2.7.2 | `Lddc;->run()V` | 2.7.4 | `Lthc;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lddc;->run()V` | 2.7.5 | `Lcdc;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lde7;-><clinit>()V` | 2.7.5 | `Lke7;-><clinit>()V` | 0.9977 |
| attachment_file | 2.7.2 | `Lde7;-><clinit>()V` | 2.7.4 | `Lxf7;-><clinit>()V` | 0.9864 |
| attachment_file | 2.7.2 | `Ldq;->onReady()V` | 2.7.5 | `Leq;->onReady()V` | 1.0000 |
| attachment_file | 2.7.2 | `Ldq;->onReady()V` | 2.7.4 | `Lfq;->onReady()V` | 0.9942 |
| attachment_file | 2.7.2 | `Ldq;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Leq;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Ldz1;->v()Ljava/lang/Object;` | 2.7.4 | `Lu02;->v()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Ldz1;->v()Ljava/lang/Object;` | 2.7.5 | `Liz1;->w()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lec0;->a(Ljava/lang/Object;Lyb3;)Ljava/lang/Object;` | 2.7.4 | `Lkc0;->a(Ljava/lang/Object;Lvd3;)Ljava/lang/Object;` | 0.9992 |
| attachment_file | 2.7.2 | `Lec0;->a(Ljava/lang/Object;Lyb3;)Ljava/lang/Object;` | 2.7.5 | `Ljv;->a(Ljava/lang/Object;Ldc3;)Ljava/lang/Object;` | 0.9632 |
| attachment_file | 2.7.2 | `Ledc;->c(Lorg/json/JSONObject;)V` | 2.7.4 | `Luhc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Ledc;->c(Lorg/json/JSONObject;)V` | 2.7.5 | `Lddc;->c(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lejb;->a(ILr15;Lyj7;Z)V` | 2.7.4 | `Lmnb;->a(ILa45;Lrl7;Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lejb;->a(ILr15;Lyj7;Z)V` | 2.7.5 | `Lljb;->a(ILv15;Lfk7;Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lejb;->b(ZLjava/lang/String;Landroid/net/Uri;Lfy4;Lr15;I)V` | 2.7.4 | `Lmnb;->b(ZLjava/lang/String;Landroid/net/Uri;Ln05;La45;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lejb;->b(ZLjava/lang/String;Landroid/net/Uri;Lfy4;Lr15;I)V` | 2.7.5 | `Lljb;->b(ZLjava/lang/String;Landroid/net/Uri;Ljy4;Lv15;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Leu0;->A(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 2.7.4 | `Ltv0;->B(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Leu0;->A(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 2.7.5 | `Lfu0;->A(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIZILjava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Boolean;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Leu0;->z(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 2.7.4 | `Ltv0;->A(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Leu0;->z(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 2.7.5 | `Lfu0;->z(Ljava/lang/String;I[Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lf23;->C(Lyj7;Lhy4;Lhy4;Lr15;I)V` | 2.7.4 | `Lo07;->q(Lrl7;Lp05;Lp05;La45;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lf23;->C(Lyj7;Lhy4;Lhy4;Lr15;I)V` | 2.7.5 | `Lk23;->o(Lfk7;Lly4;Lly4;Lv15;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lf8c;->g(Ljava/lang/String;)Z` | 2.7.4 | `Lscc;->g(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Lf8c;->g(Ljava/lang/String;)Z` | 2.7.5 | `Lf8c;->g(Ljava/lang/String;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Lfe2;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lke2;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lfe2;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lwf2;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9986 |
| attachment_file | 2.7.2 | `Lfrc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.4 | `Lqvc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lfrc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 2.7.5 | `Lerc;-><init>(ZLjava/lang/String;Ljava/util/Map;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lg6c;->a(Lorg/json/JSONObject;)V` | 2.7.4 | `Luac;->a(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lg6c;->a(Lorg/json/JSONObject;)V` | 2.7.5 | `Lg6c;->a(Lorg/json/JSONObject;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lhhc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.4 | `Lslc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lhhc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 2.7.5 | `Lghc;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/util/Map;Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lhtc;-><init>(Lskc;Landroid/content/Context;Lcr5;)V` | 2.7.4 | `Lsxc;-><init>(Ldpc;Landroid/content/Context;Lnt5;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lhtc;-><init>(Lskc;Landroid/content/Context;Lcr5;)V` | 2.7.5 | `Lgtc;-><init>(Lrkc;Landroid/content/Context;Lhr5;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lhv4;->h(Lc26;)Lva6;` | 2.7.4 | `Lpx4;->h(Ls46;)Lnd6;` | 1.0000 |
| attachment_file | 2.7.2 | `Lhv4;->h(Lc26;)Lva6;` | 2.7.5 | `Llv4;->h(Lh26;)Lbb6;` | 1.0000 |
| attachment_file | 2.7.2 | `Li37;->a(Lfy4;Lr15;I)V` | 2.7.4 | `Lec8;->e(Ln05;La45;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Li37;->a(Lfy4;Lr15;I)V` | 2.7.5 | `Lg37;->a(Ljy4;Lv15;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lipc;->b(Ljava/lang/Object;Lkic;)V` | 2.7.4 | `Lttc;->b(Ljava/lang/Object;Lumc;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lipc;->b(Ljava/lang/Object;Lkic;)V` | 2.7.5 | `Lhpc;->b(Ljava/lang/Object;Ljic;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lipc;->d()V` | 2.7.4 | `Lttc;->d()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lipc;->d()V` | 2.7.5 | `Lhpc;->d()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lix2;-><init>()V` | 2.7.5 | `Lnx2;-><init>()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lix2;-><init>()V` | 2.7.4 | `Lez2;-><init>()V` | 0.9908 |
| attachment_file | 2.7.2 | `Lj90;->a(Ljava/lang/String;)Lj90;` | 2.7.4 | `Lp90;->a(Ljava/lang/String;)Lp90;` | 1.0000 |
| attachment_file | 2.7.2 | `Lj90;->a(Ljava/lang/String;)Lj90;` | 2.7.5 | `Lm90;->a(Ljava/lang/String;)Lm90;` | 1.0000 |
| attachment_file | 2.7.2 | `Ljbc;->run()V` | 2.7.4 | `Lzfc;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Ljbc;->run()V` | 2.7.5 | `Libc;->run()V` | 1.0000 |
| attachment_file | 2.7.2 | `Lk37;->e(Lyj7;Lijb;ZLk78;Ljava/util/Map;Lhy4;Lhy4;Lhy4;Lr15;I)V` | 2.7.4 | `Lfc8;->d(Lrl7;Lqnb;ZLh98;Ljava/util/Map;Lp05;Lp05;Lp05;La45;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lk37;->e(Lyj7;Lijb;ZLk78;Ljava/util/Map;Lhy4;Lhy4;Lhy4;Lr15;I)V` | 2.7.5 | `Lq37;->a(Lfk7;Lpjb;ZLq78;Ljava/util/Map;Lly4;Lly4;Lly4;Lv15;I)V` | 0.9996 |
| attachment_file | 2.7.2 | `Lkfc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Llbc;)V` | 2.7.4 | `Lyjc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lbgc;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lkfc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Llbc;)V` | 2.7.5 | `Ljfc;->e(Lorg/json/JSONObject;Lorg/json/JSONArray;Lkbc;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lkr0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lat0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lkr0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Llr0;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lli2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lbk2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lli2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqi2;->q(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lgic;` | 2.7.5 | `Lkic;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lfic;` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lgic;` | 2.7.4 | `Lvmc;->a(Ljava/io/File;Lcom/apm/insight/CrashType;Ljava/lang/String;JJ)Lqmc;` | 0.9982 |
| attachment_file | 2.7.2 | `Llic;->c(Lng9;)Lorg/json/JSONObject;` | 2.7.4 | `Lvmc;->c(Lf99;)Lorg/json/JSONObject;` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->c(Lng9;)Lorg/json/JSONObject;` | 2.7.5 | `Lkic;->c(Lug9;)Lorg/json/JSONObject;` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->f(Z)V` | 2.7.4 | `Lvmc;->f(Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->f(Z)V` | 2.7.5 | `Lkic;->f(Z)V` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->h()V` | 2.7.5 | `Lkic;->h()V` | 1.0000 |
| attachment_file | 2.7.2 | `Llic;->h()V` | 2.7.4 | `Lvmc;->h()V` | 0.9991 |
| attachment_file | 2.7.2 | `Lllc;->a(Lt9c;)V` | 2.7.4 | `Lwpc;->a(Lgec;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lllc;->a(Lt9c;)V` | 2.7.5 | `Lklc;->a(Lt9c;)V` | 1.0000 |
| attachment_file | 2.7.2 | `Llu8;->toString()Ljava/lang/String;` | 2.7.4 | `Lzx8;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Llu8;->toString()Ljava/lang/String;` | 2.7.5 | `Lsu8;->toString()Ljava/lang/String;` | 1.0000 |
| attachment_file | 2.7.2 | `Lm15;->v()Ljava/lang/Object;` | 2.7.5 | `Lq15;->w()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lm15;->v()Ljava/lang/Object;` | 2.7.4 | `Lv35;->v()Ljava/lang/Object;` | 0.9997 |
| attachment_file | 2.7.2 | `Ln28;->O(Lt62;Lr15;I)Ltib;` | 2.7.4 | `Ljxc;->G(Lk82;La45;I)Lbnb;` | 1.0000 |
| attachment_file | 2.7.2 | `Ln28;->O(Lt62;Lr15;I)Ltib;` | 2.7.5 | `Lda8;->H(Ly62;Lv15;I)Lajb;` | 1.0000 |
| attachment_file | 2.7.2 | `Ln28;->Q(Lr15;)Z` | 2.7.4 | `Ljxc;->I(La45;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Ln28;->Q(Lr15;)Z` | 2.7.5 | `Lda8;->J(Lv15;)Z` | 1.0000 |
| attachment_file | 2.7.2 | `Ln4;->v()Ljava/lang/Object;` | 2.7.4 | `Lm4;->v()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Ln4;->v()Ljava/lang/Object;` | 2.7.5 | `Ln4;->w()Ljava/lang/Object;` | 1.0000 |
| attachment_file | 2.7.2 | `Lnu8;->a(Lorg/json/JSONObject;)Lnu8;` | 2.7.5 | `Luu8;->a(Lorg/json/JSONObject;)Luu8;` | 1.0000 |
| attachment_file | 2.7.2 | `Lnu8;->a(Lorg/json/JSONObject;)Lnu8;` | 2.7.4 | `Lby8;->a(Lorg/json/JSONObject;)Lby8;` | 0.9990 |
| attachment_file | 2.7.2 | `Lo37;->c(Ljava/lang/String;Lr15;I)V` | 2.7.4 | `Lxz9;->b(Ljava/lang/String;La45;I)V` | 1.0000 |
| attachment_file | 2.7.2 | `Lo37;->c(Ljava/lang/String;Lr15;I)V` | 2.7.5 | `Ls37;->e(Ljava/lang/String;Lv15;I)V` | 1.0000 |

## 动态日志与证据包

日志只输出计数、类/方法标记和文件哈希，不复制原始用户内容、凭据或请求正文。

```json
{
  "dsprobe.log": {
    "bytes": 12320,
    "sha256": "77d5e701da887663001fcd1d0c20a93857411290708e3003e8638e28e7f51134",
    "line_count": 49,
    "event_counts": {
      "host_generation:2.7.2/code289-cn": 1,
      "hook_install_attempt": 10,
      "wrong_full_mode_selection": 10,
      "navigation_capture_installed": 1,
      "class_not_found": 20,
      "hook_install_failure": 10,
      "native_root_capture": 1
    },
    "top_method_markers": []
  },
  "deekseep_vision.log": {
    "bytes": 6440972,
    "sha256": "07101f54feccbd4c6f04c40ae9d99bbe345849396baba3eb8cb387dd612588ef",
    "line_count": 19746,
    "event_counts": {
      "observer_session_start": 1,
      "observer_role:transport-low-level": 1,
      "observer_installed_event": 4,
      "observer_role:transport-dispatch": 1,
      "request_class_marker": 1,
      "request_constructor_candidate": 2,
      "request_factory_candidate": 5
    },
    "top_method_markers": [
      [
        "jw3.g",
        1
      ],
      [
        "zn3.o",
        1
      ]
    ]
  }
}
```

## Hook 设计门槛

1. 先用包名、versionCode、versionName、APK SHA-256 和 DEX 指纹识别宿主；未知版本进入只读模式。
2. 优先以语义边界定位：请求模型/路由构造、Flow/Continuation 边界、SSE parser、事件分派、会话恢复。
3. 每个候选需同时满足至少三个独立证据族（调用关系、参数/返回类型、继承/接口、稳定 API 调用、协议常量、字节码结构）；字符串重复不算独立证据。
4. 解析完整 JVM 描述符并检查 ClassLoader；禁止仅按混淆类名安装。
5. 候选不唯一、描述符不符、运行时类不可见或版本未知时，fail-closed，不安装该 Hook。
6. 安装按角色幂等；单个可选 Hook 失败不能阻断其他角色，失败记录版本、角色、候选 ID 和异常类型。
7. 先只读观察，再启用请求桥接；不记录 prompt、消息正文、认证头、Cookie、API Key 或 PoW 原始材料。
8. 真机验证覆盖首个 Delta、finish、错误、心跳超时、取消、自动恢复、并发流和重复安装。

## 已知证据边界

- 2.7.2 APK 已纳入扫描；先核对 Manifest 包名、versionCode/versionName（若 APK 提供）、DEX 指纹和 APK SHA-256，再与 code289-cn 运行日志交叉验证。若版本属性缺失，只能标记为 package+hash 身份，不能宣称已确认同一构建。
- 2.7.4 输入为 APKM，组件级身份必须以本次解包结果为准。
- 2.7.1 的 APKS/split 历史分析文件属于先前材料，需与当前单文件 deepseek271.apk 的身份核对。
- 2.7.3 / 2.7.5 既有 SSE 链是静态证据；尚未证明真实设备 Hook 成功。
- 服务端 ToolOpen/ToolFind/Search 片段不等于本地工具执行器；需找到本地执行和结果回注闭环。
