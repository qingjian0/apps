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

## 组件身份核对

| 版本 | 组件 | 包名 | versionCode | versionName | split | 签名证书 SHA-256 | 身份完整度 | APK SHA-256 |
|---|---|---|---|---|---|---|
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

匹配分数由语义锚点、稳定框架/API 调用族和规范化 opcode 分布组成；候选截取前先按锚点数量、稳定 API 调用量和方法体规模排序。分数仅用于排序，必须回看源码/Smali 和调用者/被调用者证据。

| 角色 | 来源版本 | 来源方法 | 目标版本 | 候选方法 | 相似度 |
|---|---|---|---|---|---:|
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.3 | `Lch7;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Leu8;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.1 | `Lf1a;->a1(Lcm9;)Ldx4;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.2 | `Ln65;-><clinit>()V` | 0.9973 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.9947 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.9947 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.3 | `Lw24;-><clinit>()V` | 0.9450 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.2 | `Lt74;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.1 | `Lh55;-><clinit>()V` | 2.7.3 | `Ld73;-><clinit>()V` | 0.6795 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.2 | `Lfcc;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.3 | `Ldia;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.4 | `Lvgc;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.2 | `Lfia;->e()Z` | 0.6329 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.3 | `Lnw8;->b()Z` | 0.6329 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.4 | `Lima;->e()Z` | 0.6329 |
| account_capability | 2.7.1 | `Lh6c;->j()J` | 2.7.5 | `Loia;->e()Z` | 0.6329 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 0.6083 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 0.6083 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 0.6083 |
| account_capability | 2.7.1 | `Ll79;->s(Ljq1;Lbx4;)Ljava/lang/Object;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 0.6083 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 0.9707 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 0.9707 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 0.9707 |
| account_capability | 2.7.1 | `Lm36;->K(B)Ljava/lang/String;` | 2.7.3 | `Lv9a;->c0(B)Ljava/lang/String;` | 0.9617 |
| account_capability | 2.7.1 | `Lmna;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.2 | `Lqsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9072 |
| account_capability | 2.7.1 | `Lmna;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.5 | `Lzsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9072 |
| account_capability | 2.7.1 | `Lmna;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.4 | `Lwwa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9063 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.3 | `Lyw8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnda;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.1 | `Lnz6;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lhv7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9081 |
| account_capability | 2.7.1 | `Lnz6;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lav7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9074 |
| account_capability | 2.7.1 | `Lnz6;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Luw7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9074 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.2 | `Lth7;-><clinit>()V` | 1.0000 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9915 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.4 | `Lmj7;-><clinit>()V` | 0.9834 |
| account_capability | 2.7.1 | `Lud7;-><clinit>()V` | 2.7.3 | `Lw46;-><clinit>()V` | 0.9593 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.2 | `Lt74;-><clinit>()V` | 0.9985 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.9985 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.9977 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.3 | `Ld73;-><clinit>()V` | 0.9524 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.3 | `Lw24;-><clinit>()V` | 0.6908 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.2 | `Ln65;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.1 | `Lw64;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.2 | `Ld45;-><clinit>()V` | 0.9933 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9927 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.4 | `Ln65;-><clinit>()V` | 0.9881 |
| account_capability | 2.7.1 | `Lx25;-><clinit>()V` | 2.7.3 | `Ln04;-><clinit>()V` | 0.9739 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.2 | `Lj9b;->a()V` | 1.0000 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.4 | `Ltdb;->a()V` | 1.0000 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.5 | `Lr9b;->a()V` | 1.0000 |
| account_capability | 2.7.1 | `Lz3b;->a()V` | 2.7.3 | `Lbi9;->a()V` | 0.9423 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.2 | `Lfia;->e()Z` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.3 | `Lnw8;->b()Z` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.4 | `Lima;->e()Z` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.2 | `Lfcc;->j()J` | 0.6329 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.3 | `Ldia;->j()J` | 0.6329 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.4 | `Lvgc;->j()J` | 0.6329 |
| account_capability | 2.7.1 | `Lzca;->e()Z` | 2.7.5 | `Lecc;->j()J` | 0.6329 |
| account_capability | 2.7.2 | `Lav7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Luw7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.2 | `Lav7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lhv7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9991 |
| account_capability | 2.7.2 | `Ld45;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9994 |
| account_capability | 2.7.2 | `Ld45;-><clinit>()V` | 2.7.4 | `Ln65;-><clinit>()V` | 0.9946 |
| account_capability | 2.7.2 | `Ld45;-><clinit>()V` | 2.7.3 | `Ln04;-><clinit>()V` | 0.9800 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.3 | `Ldia;->j()J` | 1.0000 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.4 | `Lvgc;->j()J` | 1.0000 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.3 | `Lnw8;->b()Z` | 0.6329 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.4 | `Lima;->e()Z` | 0.6329 |
| account_capability | 2.7.2 | `Lfcc;->j()J` | 2.7.5 | `Loia;->e()Z` | 0.6329 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.3 | `Lnw8;->b()Z` | 1.0000 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.4 | `Lima;->e()Z` | 1.0000 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.3 | `Ldia;->j()J` | 0.6329 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.4 | `Lvgc;->j()J` | 0.6329 |
| account_capability | 2.7.2 | `Lfia;->e()Z` | 2.7.5 | `Lecc;->j()J` | 0.6329 |
| account_capability | 2.7.2 | `Lj9b;->a()V` | 2.7.4 | `Ltdb;->a()V` | 1.0000 |
| account_capability | 2.7.2 | `Lj9b;->a()V` | 2.7.5 | `Lr9b;->a()V` | 1.0000 |
| account_capability | 2.7.2 | `Lj9b;->a()V` | 2.7.3 | `Lbi9;->a()V` | 0.9423 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 1.0000 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 1.0000 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.2 | `Ll6a;->a1(Lar9;)Lhy4;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.9973 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.9973 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.3 | `Lw24;-><clinit>()V` | 0.9470 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.2 | `Ln65;-><clinit>()V` | 2.7.3 | `Ld73;-><clinit>()V` | 0.6799 |
| account_capability | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lo10;->T(B)Ljava/lang/String;` | 2.7.3 | `Lv9a;->c0(B)Ljava/lang/String;` | 0.9898 |
| account_capability | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 2.7.3 | `Lch7;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lox8;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lqsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.5 | `Lzsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 1.0000 |
| account_capability | 2.7.2 | `Lqsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.4 | `Lwwa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9991 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 1.0000 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.9992 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.3 | `Ld73;-><clinit>()V` | 0.9536 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.3 | `Lw24;-><clinit>()V` | 0.6908 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.2 | `Lt74;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.2 | `Lth7;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9915 |
| account_capability | 2.7.2 | `Lth7;-><clinit>()V` | 2.7.4 | `Lmj7;-><clinit>()V` | 0.9834 |
| account_capability | 2.7.2 | `Lth7;-><clinit>()V` | 2.7.3 | `Lw46;-><clinit>()V` | 0.9593 |
| account_capability | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 2.7.3 | `Lyw8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Ltia;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 0.6083 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 0.6083 |
| account_capability | 2.7.2 | `Lxa9;->R(Lcr1;Lfy4;)Ljava/lang/Object;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 0.6083 |
| account_capability | 2.7.3 | `Lbi9;->a()V` | 2.7.4 | `Ltdb;->a()V` | 0.9423 |
| account_capability | 2.7.3 | `Lbi9;->a()V` | 2.7.5 | `Lr9b;->a()V` | 0.9423 |
| account_capability | 2.7.3 | `Lch7;->f()Ljava/lang/String;` | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.3 | `Lch7;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.3 | `Ld73;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.9542 |
| account_capability | 2.7.3 | `Ld73;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.9536 |
| account_capability | 2.7.3 | `Ld73;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.6804 |
| account_capability | 2.7.3 | `Ld73;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.6804 |
| account_capability | 2.7.3 | `Ldia;->j()J` | 2.7.4 | `Lvgc;->j()J` | 1.0000 |
| account_capability | 2.7.3 | `Ldia;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.3 | `Ldia;->j()J` | 2.7.4 | `Lima;->e()Z` | 0.6329 |
| account_capability | 2.7.3 | `Ldia;->j()J` | 2.7.5 | `Loia;->e()Z` | 0.6329 |
| account_capability | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 1.0000 |
| account_capability | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.3 | `Lgl8;->Y0(Lc78;)Lsv3;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 0.6083 |
| account_capability | 2.7.3 | `Lika;->z(Lpx0;Lhv3;)Ljava/lang/Object;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 0.6083 |
| account_capability | 2.7.3 | `Ln04;-><clinit>()V` | 2.7.4 | `Ln65;-><clinit>()V` | 0.9851 |
| account_capability | 2.7.3 | `Ln04;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9806 |
| account_capability | 2.7.3 | `Lnw8;->b()Z` | 2.7.4 | `Lima;->e()Z` | 1.0000 |
| account_capability | 2.7.3 | `Lnw8;->b()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.3 | `Lnw8;->b()Z` | 2.7.4 | `Lvgc;->j()J` | 0.6329 |
| account_capability | 2.7.3 | `Lnw8;->b()Z` | 2.7.5 | `Lecc;->j()J` | 0.6329 |
| account_capability | 2.7.3 | `Lv9a;->c0(B)Ljava/lang/String;` | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 0.9898 |
| account_capability | 2.7.3 | `Lv9a;->c0(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 0.9898 |
| account_capability | 2.7.3 | `Lw24;-><clinit>()V` | 2.7.4 | `Lx85;-><clinit>()V` | 0.9490 |
| account_capability | 2.7.3 | `Lw24;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.9490 |
| account_capability | 2.7.3 | `Lw24;-><clinit>()V` | 2.7.4 | `Lt94;-><clinit>()V` | 0.6908 |
| account_capability | 2.7.3 | `Lw24;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.6908 |
| account_capability | 2.7.3 | `Lw46;-><clinit>()V` | 2.7.4 | `Lmj7;-><clinit>()V` | 0.9746 |
| account_capability | 2.7.3 | `Lw46;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9668 |
| account_capability | 2.7.3 | `Lyw8;->f()Ljava/lang/String;` | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.3 | `Lyw8;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 1.0000 |
| account_capability | 2.7.4 | `Lbrc;->C(Lts1;Ln05;)Ljava/lang/Object;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 0.6083 |
| account_capability | 2.7.4 | `Le19;->f()Ljava/lang/String;` | 2.7.5 | `Lvx8;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lima;->e()Z` | 2.7.5 | `Loia;->e()Z` | 1.0000 |
| account_capability | 2.7.4 | `Lima;->e()Z` | 2.7.5 | `Lecc;->j()J` | 0.6329 |
| account_capability | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 2.7.5 | `Lt6a;->a1(Lhr9;)Lly4;` | 1.0000 |
| account_capability | 2.7.4 | `Lkaa;->a1(Lyu9;)Lp05;` | 2.7.5 | `Leb9;->R(Ldr1;Ljy4;)Ljava/lang/Object;` | 0.6083 |
| account_capability | 2.7.4 | `Lmj7;-><clinit>()V` | 2.7.5 | `Lai7;-><clinit>()V` | 0.9915 |
| account_capability | 2.7.4 | `Ln65;-><clinit>()V` | 2.7.5 | `Lh45;-><clinit>()V` | 0.9952 |
| account_capability | 2.7.4 | `Lp51;->U(B)Ljava/lang/String;` | 2.7.5 | `Ls10;->T(B)Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lt94;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.9992 |
| account_capability | 2.7.4 | `Lt94;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 0.6854 |
| account_capability | 2.7.4 | `Ltdb;->a()V` | 2.7.5 | `Lr9b;->a()V` | 1.0000 |
| account_capability | 2.7.4 | `Luw7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lhv7;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9991 |
| account_capability | 2.7.4 | `Lvgc;->j()J` | 2.7.5 | `Lecc;->j()J` | 1.0000 |
| account_capability | 2.7.4 | `Lvgc;->j()J` | 2.7.5 | `Loia;->e()Z` | 0.6329 |
| account_capability | 2.7.4 | `Lwma;->f()Ljava/lang/String;` | 2.7.5 | `Lcja;->f()Ljava/lang/String;` | 1.0000 |
| account_capability | 2.7.4 | `Lwwa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 2.7.5 | `Lzsa;->onRecvCustomCmdMsg(Ljava/lang/String;II[B)V` | 0.9991 |
| account_capability | 2.7.4 | `Lx85;-><clinit>()V` | 2.7.5 | `Lr65;-><clinit>()V` | 1.0000 |
| account_capability | 2.7.4 | `Lx85;-><clinit>()V` | 2.7.5 | `Lx74;-><clinit>()V` | 0.6854 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.2 | `Lk5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.2 | `Ln5b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.4 | `Ly9b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.5 | `Lv5b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.2 | `Lnz0;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6190 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5600 |
| agent_planning | 2.7.1 | `La0b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5459 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.4 | `Lx9b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.2 | `Ls5b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.5209 |
| agent_planning | 2.7.1 | `Lc0b;->toString()Ljava/lang/String;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.4989 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.4 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.5 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.3 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 0.9944 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.4 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.3 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 0.9623 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.2 | `Ljkb;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lvob;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 0.8044 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8044 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8044 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.7938 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.1 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 0.5689 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.5689 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.5689 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.5640 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 0.8429 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8429 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8429 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.1 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.2 | `Ln5b;-><clinit>()V` | 0.9756 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.4 | `Ly9b;-><clinit>()V` | 0.9756 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.5 | `Lv5b;-><clinit>()V` | 0.9756 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.2 | `Lk5b;-><clinit>()V` | 0.9633 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 0.9633 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 0.9633 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.2 | `Lnz0;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6143 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5583 |
| agent_planning | 2.7.1 | `Ld0b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5444 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.4 | `Lrhc;->o(Lo19;Ly99;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.5 | `Ladc;->o(Lfy8;Lo69;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.3 | `Laja;->o(Lmh7;Lvp7;)V` | 0.9966 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.1 | `Ld7c;->o(Lou8;Lv29;)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 0.8064 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8064 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8064 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.2 | `Ljkb;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.4 | `Lvob;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.7892 |
| agent_planning | 2.7.1 | `Lec1;->B(I)Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.7892 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.4 | `Laab;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.5 | `Lx5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.2 | `Ls5b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 0.8048 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.8048 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.8048 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.5187 |
| agent_planning | 2.7.1 | `Lf0b;->toString()Ljava/lang/String;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.4929 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.2 | `Lq5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.4 | `Lbab;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.5 | `Ly5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.2 | `Lnz0;-><clinit>()V` | 0.8680 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 0.8680 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 0.8680 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.2 | `Lk5b;-><clinit>()V` | 0.8495 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 0.8495 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 0.8495 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6723 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.6215 |
| agent_planning | 2.7.1 | `Lg0b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5640 |
| agent_planning | 2.7.1 | `Lg0b;->d(Lbn3;)Ljava/lang/Object;` | 2.7.2 | `Lq5b;->d(Lrn3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;->d(Lbn3;)Ljava/lang/Object;` | 2.7.4 | `Lbab;->e(Lrp3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lg0b;->d(Lbn3;)Ljava/lang/Object;` | 2.7.5 | `Ly5b;->d(Lwn3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.2 | `Lnv4;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.3 | `Lms3;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.4 | `Lvx4;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.5 | `Lrv4;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lgu4;->run()V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.1 | `Lh1b;-><clinit>()V` | 2.7.2 | `Lq6b;-><clinit>()V` | 0.9843 |
| agent_planning | 2.7.1 | `Lh1b;-><clinit>()V` | 2.7.5 | `Lx6b;-><clinit>()V` | 0.9843 |
| agent_planning | 2.7.1 | `Lh1b;-><clinit>()V` | 2.7.4 | `Labb;-><clinit>()V` | 0.9697 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.2 | `Lyc5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.4 | `Lif5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.5 | `Lcd5;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhb5;-><clinit>()V` | 2.7.3 | `Lp84;-><clinit>()V` | 0.7970 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.2 | `Ldrb;-><clinit>()V` | 0.9948 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.5 | `Ldrb;-><clinit>()V` | 0.9933 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.4 | `Lqvb;-><clinit>()V` | 0.9912 |
| agent_planning | 2.7.1 | `Lhlb;-><clinit>()V` | 2.7.3 | `Lez9;-><clinit>()V` | 0.9680 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.2 | `Lov4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.3 | `Lns3;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.4 | `Lwx4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lhu4;->onGlobalLayout()V` | 2.7.5 | `Lsv4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.2 | `Ls5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 0.9482 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.9482 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.9482 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.4 | `Laab;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.5827 |
| agent_planning | 2.7.1 | `Li0b;->toString()Ljava/lang/String;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.5462 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.2 | `Loca;-><clinit>()V` | 0.9984 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.5 | `Lxca;-><clinit>()V` | 0.9975 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.4 | `Lqga;-><clinit>()V` | 0.9952 |
| agent_planning | 2.7.1 | `Li7a;-><clinit>()V` | 2.7.3 | `Ldr8;-><clinit>()V` | 0.9797 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.2 | `Ls6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.2 | `Lwcc;->e()Lxjc;` | 0.5900 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.3 | `Lvia;->e()Lrpa;` | 0.5900 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.4 | `Lmhc;->e()Lioc;` | 0.5900 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 0.5900 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 0.5298 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.5298 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.5298 |
| agent_planning | 2.7.1 | `Lj1b;->toString()Ljava/lang/String;` | 2.7.3 | `Lhl4;->b()Ljava/lang/String;` | 0.5036 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.3 | `Lhl4;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.4 | `Lnt5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.5 | `Lhr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.2 | `Lwcc;->e()Lxjc;` | 0.5104 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.3 | `Lvia;->e()Lrpa;` | 0.5104 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.4 | `Lmhc;->e()Lioc;` | 0.5104 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 0.5104 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.2 | `Ls6b;->toString()Ljava/lang/String;` | 0.5036 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 0.5036 |
| agent_planning | 2.7.1 | `Ljp5;->b()Ljava/lang/String;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 0.5036 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.2 | `Ls5b;->toString()Ljava/lang/String;` | 0.9482 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.9482 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.9482 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.4 | `Lx9b;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.5866 |
| agent_planning | 2.7.1 | `Ln1b;->toString()Ljava/lang/String;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.5559 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lm1a;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lux9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9853 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 0.5545 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.5545 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.5545 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Ls5b;->toString()Ljava/lang/String;` | 0.5449 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.5449 |
| agent_planning | 2.7.1 | `Lns9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.5449 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 0.9983 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.4 | `Lvpc;->b(Lorg/json/JSONObject;)Z` | 0.9983 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.5 | `Ljlc;->b(Lorg/json/JSONObject;)Z` | 0.9983 |
| agent_planning | 2.7.1 | `Lofc;->b(Lorg/json/JSONObject;)Z` | 2.7.3 | `Lhra;->b(Lorg/json/JSONObject;)Z` | 0.9894 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.2 | `Lbf9;-><clinit>()V` | 0.9970 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 0.9970 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.4 | `Lxi9;-><clinit>()V` | 0.9941 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.3 | `Lkx7;-><clinit>()V` | 0.9856 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.2 | `Ln03;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.3 | `Lr32;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.4 | `Lk23;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lpb9;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.2 | `Lyp;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.4 | `Laq;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.5 | `Lzp;->run()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lpp;->run()V` | 2.7.3 | `Lyo;->run()V` | 0.9920 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.3 | `Lhl5;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.3 | `Lhl5;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.3 | `Lhl5;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.3 | `Lhl5;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqq6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.2 | `Ll03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.3 | `Lp32;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.4 | `Li23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lqz2;-><clinit>()V` | 2.7.5 | `Lq03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.4 | `Lr19;->f(IIILo19;Lne4;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 0.9980 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.5 | `Liy8;->f(IIILfy8;Loc4;)V` | 0.9980 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.2 | `Lw6b;->toString()Ljava/lang/String;` | 0.5866 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.5866 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.5866 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.2 | `Ls5b;->toString()Ljava/lang/String;` | 0.5827 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.5827 |
| agent_planning | 2.7.1 | `Lru8;->f(IIILou8;Lib4;)V` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.5827 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.2 | `Lnz0;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.2 | `Lk5b;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.2 | `Ln5b;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.4 | `Ly9b;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.5 | `Lv5b;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6438 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5689 |
| agent_planning | 2.7.1 | `Lry0;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5538 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.2 | `Ln03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.3 | `Lr32;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.4 | `Lk23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.2 | `Lbf9;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.3 | `Lkx7;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.4 | `Lxi9;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lsz2;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.2 | `Lp21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.4 | `Le41;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.5 | `Lr21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.2 | `Ljkb;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.4 | `Lvob;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 0.5362 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 0.5362 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 0.5362 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5261 |
| agent_planning | 2.7.1 | `Lt11;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5232 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.2 | `Ljkb;-><clinit>()V` | 0.8387 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.8387 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.4 | `Lvob;-><clinit>()V` | 0.8387 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.8387 |
| agent_planning | 2.7.1 | `Lty0;->toString()Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8114 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.3 | `Lhe5;->K0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->N(Ljava/lang/String;J)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->K0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->P0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->K0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lum7;->x0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.1 | `Lux;->j(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lcx;->g(Ljava/lang/Object;)Ljava/lang/Object;` | 0.7932 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lfj9;->C(Lvd3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqf9;->C(Ldc3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxb9;->B(Lnb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lsx7;->C(Lhf2;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9939 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.2 | `Lsmc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.4 | `Ldrc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.5 | `Lrmc;->a(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.1 | `Lxgc;->a(Lorg/json/JSONObject;)Z` | 2.7.3 | `Lpsa;->a(Lorg/json/JSONObject;)Z` | 0.9878 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.2 | `Lsr0;->a(Liy8;)Lg89;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.3 | `Len0;->a(Lxh7;)Lnr7;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.4 | `Lit0;->a(Ly19;)Lxb9;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxq0;->a(Lyu8;)Lv49;` | 2.7.5 | `Ltr0;->a(Lpy8;)Ln89;` | 1.0000 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.3 | `Lsm6;->b(Lzb4;Lif2;)Ljava/lang/Object;` | 0.9887 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 0.9870 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.5 | `Lm08;->a(Ltg5;Lec3;)Ljava/lang/Object;` | 0.9870 |
| agent_planning | 2.7.1 | `Lxw7;->a(Lwe5;Lob3;)Ljava/lang/Object;` | 2.7.4 | `La28;->a(Lyi5;Lwd3;)Ljava/lang/Object;` | 0.9853 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.2 | `Lwcc;->e()Lxjc;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.3 | `Lvia;->e()Lrpa;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.4 | `Lmhc;->e()Lioc;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 1.0000 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.2 | `Ls6b;->toString()Ljava/lang/String;` | 0.5900 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 0.5900 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 0.5900 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 0.5104 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.3 | `Lhl4;->b()Ljava/lang/String;` | 0.5104 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.4 | `Lnt5;->b()Ljava/lang/String;` | 0.5104 |
| agent_planning | 2.7.1 | `Ly6c;->e()Laec;` | 2.7.5 | `Lhr5;->b()Ljava/lang/String;` | 0.5104 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.3 | `Ltr8;->j(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.4 | `Lgha;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Ly7a;->h(Ljava/lang/Object;)V` | 2.7.5 | `Lnda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.2 | `Ljkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.4 | `Lvob;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 0.8387 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8387 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8387 |
| agent_planning | 2.7.1 | `Lyeb;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8114 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.2 | `Lwjc;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.3 | `Lqpa;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.4 | `Lhoc;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzdc;->b(Ljava/util/LinkedList;)I` | 2.7.5 | `Lvjc;->b(Ljava/util/LinkedList;)I` | 0.9930 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.2 | `Lxt9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.4 | `Lwx9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.5 | `Leu9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.1 | `Lzo9;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 2.7.3 | `Lz98;->a(Ljava/lang/Class;)Ljava/lang/Object;` | 0.6100 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.2 | `Ldx6;-><clinit>()V` | 0.9971 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.4 | `Lc07;-><clinit>()V` | 0.9971 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.5 | `Ljx6;-><clinit>()V` | 0.9971 |
| agent_planning | 2.7.1 | `Lzu6;-><clinit>()V` | 2.7.3 | `Ldp5;-><clinit>()V` | 0.9525 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.4 | `Lrhc;->o(Lo19;Ly99;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.5 | `Ladc;->o(Lfy8;Lo69;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.3 | `Laja;->o(Lmh7;Lvp7;)V` | 0.9966 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.4866 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.2 | `Lbdc;->o(Lyx8;Lh69;)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.4860 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.4 | `Lxi9;-><clinit>()V` | 0.9970 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.3 | `Lkx7;-><clinit>()V` | 0.9884 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.3 | `Lr32;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.4 | `Lk23;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.2 | `Lbf9;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.5 | `Liy8;->f(IIILfy8;Loc4;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.9980 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.4 | `Lr19;->f(IIILo19;Lne4;)V` | 0.9980 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.5863 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.5863 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.5825 |
| agent_planning | 2.7.2 | `Lby8;->f(IIILyx8;Lkc4;)V` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.5825 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.4 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.5 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 2.7.3 | `Lcn/fly/verify/dz;->a(Landroid/net/Network;Ljava/lang/String;)Ljava/net/HttpURLConnection;` | 0.9944 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.4 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.5 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 2.7.3 | `Lcn/fly/verify/dz;->b(Landroid/content/Context;)Ljava/lang/String;` | 0.9623 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.5747 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 0.6111 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.5747 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onTrace(Landroid/support/v4/app/Fragment;Ljava/lang/String;Ljava/lang/String;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onHiddenChanged(Landroid/support/v4/app/Fragment;Z)V` | 0.8127 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->setUserVisibleHint(Landroid/support/v4/app/Fragment;Z)V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->onResumeShow(Landroid/support/v4/app/Fragment;Ljava/lang/String;)V` | 0.6111 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lvob;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.8576 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8200 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8167 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8044 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8044 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.7938 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.7060 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.2 | `Lcom/bytedance/apm/insight/a;->onRefresh(Lorg/json/JSONObject;Z)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.7002 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.3 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lcom/bytedance/apm/insight/a;->onReady()V` | 0.5829 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.5689 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.5689 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->collectService(Ljava/util/Map;)V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.5640 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8240 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8429 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8429 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8240 |
| agent_planning | 2.7.2 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8200 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.3 | `Lhl4;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.4 | `Lnt5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.5 | `Lhr5;->b()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.3 | `Lvia;->e()Lrpa;` | 0.5104 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.4 | `Lmhc;->e()Lioc;` | 0.5104 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.5 | `Lvcc;->e()Lwjc;` | 0.5104 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.4 | `Lcbb;->toString()Ljava/lang/String;` | 0.5036 |
| agent_planning | 2.7.2 | `Lcr5;->b()Ljava/lang/String;` | 2.7.5 | `Lz6b;->toString()Ljava/lang/String;` | 0.5036 |
| agent_planning | 2.7.2 | `Ldrb;-><clinit>()V` | 2.7.5 | `Ldrb;-><clinit>()V` | 0.9985 |
| agent_planning | 2.7.2 | `Ldrb;-><clinit>()V` | 2.7.4 | `Lqvb;-><clinit>()V` | 0.9963 |
| agent_planning | 2.7.2 | `Ldrb;-><clinit>()V` | 2.7.3 | `Lez9;-><clinit>()V` | 0.9725 |
| agent_planning | 2.7.2 | `Ldx6;-><clinit>()V` | 2.7.4 | `Lc07;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ldx6;-><clinit>()V` | 2.7.5 | `Ljx6;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ldx6;-><clinit>()V` | 2.7.3 | `Ldp5;-><clinit>()V` | 0.9548 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.9890 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->K0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.2 | `Le27;->E0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->K0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 0.7982 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.2 | `Le27;->M0(Ljava/lang/String;)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.7912 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.3 | `Lhe5;->L(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.4 | `Lsm8;->J(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.5 | `Lf27;->M(Ljava/lang/String;J)V` | 1.0000 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.3 | `Lhe5;->v0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.4 | `Lsm8;->o0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.5 | `Lf27;->z0(Ljava/lang/String;)V` | 0.9890 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.3 | `Lhe5;->K0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.4 | `Lsm8;->w0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.2 | `Le27;->V(Ljava/lang/String;J)V` | 2.7.5 | `Lf27;->M0(Ljava/lang/String;)V` | 0.7982 |
| agent_planning | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 2.7.3 | `Ltr8;->j(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 2.7.4 | `Lgha;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Leda;->h(Ljava/lang/Object;)V` | 2.7.5 | `Lnda;->h(Ljava/lang/Object;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 2.7.5 | `Lm08;->a(Ltg5;Lec3;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 2.7.3 | `Lsm6;->b(Lzb4;Lif2;)Ljava/lang/Object;` | 0.9982 |
| agent_planning | 2.7.2 | `Lf08;->a(Log5;Lzb3;)Ljava/lang/Object;` | 2.7.4 | `La28;->a(Lyi5;Lwd3;)Ljava/lang/Object;` | 0.9982 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lhj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lgj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 0.5590 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 0.5590 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.5386 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.5386 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5376 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.5369 |
| agent_planning | 2.7.2 | `Lfj;->p(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.5293 |
| agent_planning | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lfj9;->C(Lvd3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lqf9;->C(Ldc3;Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Ljf9;->C(Lyb3;Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lsx7;->C(Lhf2;Ljava/lang/Object;)Ljava/lang/Object;` | 0.9939 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.4 | `Lvob;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.4 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.5 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.8576 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8387 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8387 |
| agent_planning | 2.7.2 | `Ljkb;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.8114 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.4 | `Ly9b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.5 | `Lv5b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6190 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5600 |
| agent_planning | 2.7.2 | `Lk5b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5459 |
| agent_planning | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 2.7.4 | `Lvpc;->b(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 2.7.5 | `Ljlc;->b(Lorg/json/JSONObject;)Z` | 1.0000 |
| agent_planning | 2.7.2 | `Lklc;->b(Lorg/json/JSONObject;)Z` | 2.7.3 | `Lhra;->b(Lorg/json/JSONObject;)Z` | 0.9910 |
| agent_planning | 2.7.2 | `Ll03;-><clinit>()V` | 2.7.3 | `Lp32;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ll03;-><clinit>()V` | 2.7.4 | `Li23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ll03;-><clinit>()V` | 2.7.5 | `Lq03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.4 | `Lx9b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.5 | `Lu5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.8226 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.5209 |
| agent_planning | 2.7.2 | `Lm5b;->toString()Ljava/lang/String;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.4989 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.3 | `Lr32;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.4 | `Lk23;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.5 | `Ls03;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.3 | `Lkx7;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.4 | `Lxi9;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.2 | `Ln03;-><clinit>()V` | 2.7.5 | `Lif9;-><clinit>()V` | 0.5124 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.4 | `Ly9b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.5 | `Lv5b;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 0.9871 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6143 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5583 |
| agent_planning | 2.7.2 | `Ln5b;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5444 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.3 | `Lms3;->run()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.4 | `Lvx4;->run()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.5 | `Lrv4;->run()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.3 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.4 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$200(ZLjava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.2 | `Lnv4;->run()V` | 2.7.5 | `Lcom/bytedance/apm/agent/v2/instrumentation/FragmentTimeAgent;->access$800(Ljava/lang/String;Ljava/lang/String;JJ)V` | 0.4955 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lm1a;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Lux9;->z(Ljava/lang/Object;)Ljava/lang/Object;` | 1.0000 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.9853 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.5545 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.5545 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.5449 |
| agent_planning | 2.7.2 | `Lnx9;->y(Ljava/lang/Object;)Ljava/lang/Object;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.5449 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.4 | `Lc11;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.5 | `Loz0;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.4 | `Lv9b;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.5 | `Ls5b;-><clinit>()V` | 0.9450 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.4 | `Ly9b;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.5 | `Lv5b;-><clinit>()V` | 0.9353 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.6438 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5689 |
| agent_planning | 2.7.2 | `Lnz0;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5538 |
| agent_planning | 2.7.2 | `Loca;-><clinit>()V` | 2.7.5 | `Lxca;-><clinit>()V` | 0.9992 |
| agent_planning | 2.7.2 | `Loca;-><clinit>()V` | 2.7.4 | `Lqga;-><clinit>()V` | 0.9968 |
| agent_planning | 2.7.2 | `Loca;-><clinit>()V` | 2.7.3 | `Ldr8;-><clinit>()V` | 0.9812 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.3 | `Lhl5;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.3 | `Lhl5;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.2 | `Los6;->f(Ljava/util/LinkedHashSet;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 0.6832 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.3 | `Lhl5;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.4 | `Lov6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->g(Ljava/util/ArrayList;)V` | 1.0000 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.3 | `Lhl5;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.4 | `Lov6;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.2 | `Los6;->g(Ljava/util/ArrayList;)V` | 2.7.5 | `Lus6;->f(Ljava/util/LinkedHashSet;)V` | 0.6832 |
| agent_planning | 2.7.2 | `Lov4;->onGlobalLayout()V` | 2.7.3 | `Lns3;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lov4;->onGlobalLayout()V` | 2.7.4 | `Lwx4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lov4;->onGlobalLayout()V` | 2.7.5 | `Lsv4;->onGlobalLayout()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.4 | `Le41;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.5 | `Lr21;-><clinit>()V` | 1.0000 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.4 | `Lvob;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.5373 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 0.5362 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 0.5362 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/apm/insight/FlutterAgent;->registerConfigListener(Lcom/bytedance/apm/insight/FlutterAgent$IFlutterConfigListener;)V` | 0.5261 |
| agent_planning | 2.7.2 | `Lp21;-><clinit>()V` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.5232 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.4 | `Laab;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.5 | `Lx5b;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.4 | `Ldab;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.5 | `La6b;->toString()Ljava/lang/String;` | 0.8397 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.4 | `Lgbb;->toString()Ljava/lang/String;` | 0.8048 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.5 | `Ld7b;->toString()Ljava/lang/String;` | 0.8048 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.3 | `Lph7;->f(IIILmh7;Llb3;)V` | 0.5187 |
| agent_planning | 2.7.2 | `Lp5b;->toString()Ljava/lang/String;` | 2.7.3 | `Lxc8;->A(Ljava/lang/Object;)Ljava/lang/Object;` | 0.4929 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.4 | `Ltz0;->q(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.5 | `Lqy0;->p(I)Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 0.8064 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 0.8064 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.4 | `Lvob;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.5 | `Lqkb;-><clinit>()V` | 0.7933 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Lcom/bytedance/services/apm/api/IApmAgent;` | 0.7892 |
| agent_planning | 2.7.2 | `Lpy0;->p(I)Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.7892 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.4 | `Le11;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.5 | `Lqz0;->toString()Ljava/lang/String;` | 1.0000 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.3 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.4 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.5 | `Lcom/bytedance/services/apm/api/IApmAgent__ServiceProxy;->newInstance()Ljava/lang/Object;` | 0.8429 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.3 | `Lhs9;-><clinit>()V` | 0.8387 |
| agent_planning | 2.7.2 | `Lpz0;->toString()Ljava/lang/String;` | 2.7.4 | `Lvob;-><clinit>()V` | 0.8387 |

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
