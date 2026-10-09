# VibeMail(vibemail)

「Agentic App 黑客松 2026」场景 01(邮件)参赛应用。**有情绪的邮件。** 0.7.x 按
OctoSense 设计原型参考重构为一部流式手机列应用(任意窗口宽度自适应铺满):
五种 vibe(珊瑚橙专注 / 霓虹黄愉悦 / 薄荷绿平静 / 粉色灵感 / 蓝色连接)为每封邮件
标注情绪底色,星轨收件箱把邮件化作漂浮气泡散满全窗,写信的语气滑杆在真诚随意 ↔
轻松幽默 ↔ 自然友好 ↔ 简洁专业 ↔ 正式得体五个档位间实时改写;AI 心情播报、三行
摘要与语气改写走宿主 model 服务(不可用时如实标注并降级);真实收发经平台 mail
宿主服务完成——凭据与密钥始终留在宿主侧,不经过应用、不进提交包。

| | |
| --- | --- |
| 应用 ID / 版本 | `vibemail` / **0.7.26** |
| 门禁状态 | `hub check --allow-unsigned` — **PASSED**(可编辑源码,新可移植摘要口径) |
| 提交通道 | **GitHub publisher 工作流**(`.github/workflows/publish-app.yml`,tag push 出证明 release;无需发行者私钥) |
| 申请能力 | `mail` + `model` + `storage`(共三项,按最小化原则) |
| 实测平台 | Windows 10(26100)——唯一实测平台,布局审计宽度 412 / 700 / 1200 |
| 提交物 | `bundle/`(manifest、listing、main.splash、icon、5 张真实截图) |
| 类别 / 分级 | productivity / all |

## 目录

- [功能特性](#功能特性)
- [能力声明](#能力声明)
- [目录结构](#目录结构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [复现与验证](#复现与验证)
- [在 OctoSense 桌面 Shell 中运行(最强演示)](#在-octosense-桌面-shell-中运行最强演示)
- [运行证据](#运行证据)
- [状态与剩余人工步骤](#状态与剩余人工步骤)
- [隐私](#隐私)
- [近期版本](#近期版本)

## 功能特性

- **五种 vibe 的情绪收件箱**:每封邮件标注一种 vibe(专注 / 愉悦 / 平静 / 灵感 /
  连接),未读点、星标、重要度;vibe 过滤 chips 为纯文字 + 各自 vibe 淡色底、
  等宽均分一行(激活反白,真实筛选并在摘要卡显示筛选指示);问候按实际时间变化
  (早上好/中午好/下午好/晚上好)、「你有 N 封未读邮件」(N=未读)随数据变化;
  **AI 心情播报行**由模型按列表主题与 vibe 标注动态生成(30 字内氛围句),卡片
  如实标注「模型生成 / 生成中… / 固定文案」,无模型服务时回落固定计数行
- **星轨收件箱**:邮件化作漂浮气泡——大小=重要度、颜色=vibe、高光提体积,
  星座铺满整个窗口宽度(Fill 画布,锚点与漂移全比例化),随 sin/cos 缓慢漂移
  (0.15s 步进),点按气泡直接打开邮件;空收件箱显示「收件箱一片平静」
- **邮件详情**:vibe 芯片、**AI 三行摘要**卡(✦ 形彩色要点,来源如实标注:
  练习摘要 / 模型生成 / 生成中 / 服务不可用 / 正文截取)、完整正文,
  星标 / 归档 / 回复(霓虹黄)三键;归档可在设置中一键恢复
- **写信与语气滑杆**:收件人 / 主题预填,**五档语气滑杆**(真诚随意 ↔ 轻松幽默 ↔
  自然友好 ↔ 简洁专业 ↔ 正式得体,三等分列结构对齐、任意宽度自适应)实时改写
  回信预览——练习数据内置每封邮件五档语气文案(Mira 线程与参考原型逐字一致),
  live 邮件走 `model.complete` 实时改写,不可用时保留原文并如实标注;
  **单击发送**(发送中… → 已随波寄出 / 失败保留草稿可重试)
- **「我的」设置屏**:外观主题(亮/暗快切胶囊 + 跟随系统 / 亮色 / 暗色三态,
  持久化并跟随 Shell 亮暗)、OctoSense 能力声明卡(mail / storage / model 与
  「刻意不声明」注记)、邮箱账号(添加账号走宿主 sheet / 刷新 / 两步断开 /
  归档恢复)、练习开关(模拟发送失败)
- **真实邮件**:经平台 mail 宿主服务走真实 IMAP/SMTP;账号在**宿主自己的登录
  面板**添加,授权码只存宿主保险库;live 邮件由关键词规则标注 vibe(重要度按
  vibe 档位),AI 摘要按需生成;无账号环境如实显示并回退已标注的练习数据
- **真实模型调用**:AI 三行摘要、语气改写与心情播报为一次性 `model.complete`
  调用(schema 校验);改写来源如实标注「模型改写」(宿主 model 服务的 meta
  只含 class/usage/budget 等,不含模型名——0.7.24 实测)
- **双主题·三态**:暖纸米色 #eaeae3 亮 × 炭黑 #151413 暗,vibe 五色跨主题不变;
  可跟随 OctoSense 系统亮暗(Shell 切换 ~2 秒内跟随)或手动固定,选择持久化
- **宽度自适应·悬浮导航**:根列流式 Fill——412 手机宽度即原生设计,宽窗自然
  铺满(滑杆 / 星图等固定件由 Fill 包裹居中);玻璃导航胶囊悬浮沉底,列表从其
  下方滚过,导航闸门保证胶囊压住卡片时点导航不会误开卡片

## 能力声明

应用只申请实现功能所需的三项能力(未申请即未授予):

| 能力 | 支撑的功能 | 不可用时的行为 |
| --- | --- | --- |
| `mail` | 收件箱 / 阅读 / 发送全流程(`mail.accounts`、`mail.add_account`、`mail.sync`、`mail.list`、`mail.message`、`mail.mark_read`、`mail.send`、`mail.remove_account`) | 摘要卡如实显示服务状态,回退已标注的练习数据 |
| `model` | AI 三行摘要、语气滑杆改写与心情播报 | 界面如实标注「服务不可用」;摘要回退正文截取或练习摘要,改写保留原文,心情播报回固定计数行 |
| `storage` | 主题偏好(theme.json,4 MiB 上限内) | card-host 恒有存储沙箱,该声明供商店隐私摘要使用 |

无网络主机声明(`hosts {}`)——刻意不声明 `net` / `web` / `camera` / `location`。

## 目录结构

```text
route_test.json 声明式路线测试:6 条点击路线(vibe 筛选与详情 / 星轨与三态主题 /
               语气滑杆五档改写 / 单击发送 / 故障-保留-重试 / 归档与恢复)
validation.json 机器可读状态清单:已验证项与未验证边界(诚实记录)
BRIEF.md       设计简报(OctoScript-App-Design-Flow 第 1 步;不入提交包)
docs/          design-brief.md:设计系统与实现映射(调色板、组件语言、
               布局数学、与参考原型的取舍)
service/       写信/发送 reducer(controller.py,main.splash 状态机的
               验证孪生)+ unittest(test_controller.py,8 用例)
bridge/        开发层(现为可选):IMAP/SMTP ↔ 本机 HTTP 网桥(凭据只存
               config.json,已 gitignore;5 个解析单测)——已被平台服务
               路线取代,不进提交包
dev/           开发层:网桥适配器(替换 main.splash 的 MARKER:ADAPTER 块)
scripts/       run_app.py:run.cmd 的内核(启动前生成运行副本 build/run-bundle)
               drive-demo.py:经 Makepad 远程桥驱动真实 card-host 窗口
               截取商店截图与证据流(驱动会把真实鼠标停靠到远处——OS
               光标事件会吞掉合成点击)
               drive-mail.py:驱动提交包在 card-host 中走平台 mail 服务
               (我的 → 添加账号 → 宿主登录面板 → 真实拒绝 → 取消)
               run_routes.py:执行 route_test.json 的通用路线跑器
               audit_missing / audit_overflow:宽度审计(412 / 700 / 1200;
               缺失审计每屏全新实例——长生命周期实例的采集与点击会
               相互干扰,均为实测结论)
               mailbox_probe.py:只读 IMAP 自检(列出服务器各文件夹件数)
               check_splash.py:main.splash 括号平衡静态检查
               dev_bundle.py:组装 build/dev-bundle(仅开发,不入库)
evidence/      运行证据(见下文「运行证据」)
.github/workflows/publish-app.yml
               tag push 发布工作流(tools/octo publish-github 生成;
               publisher-prepare → GitHub Sigstore 证明 → verify/pack)
bundle/        THE SUBMISSION —— 可编辑提交源码(最终证明字节由工作流生成)
  manifest.json    id、版本、能力、完整性哈希(hub stamp 写入;未签名——
                   GitHub provenance 路线,无需发行者私钥)
  listing.json     商店展示信息(副标题、描述、截图、发布者)
  main.splash      应用本体(Splash 脚本,无编译步骤)
  assets/icon.svg  图标(暖纸方板 + 轨道环五色点 + 墨色信封)
  screenshots/     01..05 真实截取(inbox / orbit / compose / detail / dark)
```

## 环境要求

- Windows 10(26100)——唯一实测平台;其余平台未验证
- Rust stable(rustup)——用于构建带 mail 服务的 card-host
- Python 3.9+,无第三方依赖(像素探针另需 Pillow)
- 同级目录下的 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
  检出(开发接线:`crates/mail-service/` 为 OctoSense 仓库参考 mail 服务的
  本地拷贝,`crates/card-host/src/host.rs` 在 mount 时
  `octosense_mail_service::register()`——两项均为本机开发环境改动,不入上游)
- 桌面 Shell 演示另需:本地 [OctoSense](https://github.com/OctoSense-org/OctoSense)
  检出与本地签名 hub 目录(`../octosense-local-hub/`,见其 README)

## 快速开始

`run.cmd` 是一键入口(内核为 `scripts/run_app.py`):

| 命令 | 作用 |
| --- | --- |
| `run.cmd` | 以桌面宽度(1200×860)在 card-host 中启动应用(流式列铺满) |
| `run.cmd mobile` | 以手机宽度(412×860)启动——本设计的原生尺寸 |
| `run.cmd desktop` | 以桌面宽度(1200×860)启动(等价于不带参数) |
| `run.cmd demo` | 手机宽度 + 完整证据演示(drive-demo.py,重写截图与证据) |
| `run.cmd mail` | 商店形态邮件流程(我的 → 宿主面板 → 真实拒绝 → 取消) |
| `run.cmd shell` | 启动真实 OctoSense 桌面 Shell(本地签名 hub,真实邮箱可用) |
| `run.cmd check` | 单元测试 + hub stamp + hub 门禁检查 |
| `run.cmd stop` | 结束全部测试实例(card-host / octosense) |

## 复现与验证

先构建带 mail 服务的宿主(一次性):

```sh
cd ../OctoSense-App-Hub && cargo build --release -p octosense-card-host
# 产物在 %CARGO_TARGET_DIR%(本机为 D:\Users\yzbtdiy\Cache\CARGO_TARGET)
```

再以提交包运行(路线回归与证据流各用一个全新实例;原生宽度 412×860):

```sh
python -m unittest discover -s service      # 状态机单测(8/8)
run.cmd mobile                              # 启动(自动生成去签名运行副本)
python scripts/run_routes.py 8146           # 6/6 路线通过则退出码 0
run.cmd stop
run.cmd demo                                # 重写 bundle/screenshots 与 evidence/
python scripts/drive-mail.py 8146           # 商店形态邮件:面板/真实拒绝/取消
python scripts/audit_overflow.py 412 700 1200   # 溢出审计(全 clean)
python scripts/audit_missing.py 412 700 1200    # 缺失审计(五屏全 complete)
python build/dbg_pixels2.py 8146                # 像素级主题/配色断言
hub stamp bundle                            # 可移植摘要(app-contract 1.x 口径)
hub check bundle --allow-unsigned           # 门禁(可编辑源码未签名)
hub scan bundle --packet build/review.json  # 评审问题包(七问)
```

> 工具链注意:hub 必须从 OctoSense-App-Hub 当前 main 构建(本机产物在
> `%CARGO_TARGET_DIR%`,仓库本地 `target/` 里可能是旧货)。0.7.26 起摘要为
> 跨平台可移植口径,Windows 与 Linux 计算一致;`ci/verify.sh` 已同步。

接入自己的邮箱:运行应用,「我的 → 邮箱账号 → 添加账号」,在**宿主面板**里输入
邮箱地址和服务商授权码(QQ / 163 / Gmail 自动识别服务器)。授权码只存宿主侧,
不经过应用,也绝不进入提交包。已连接后「我的 → 刷新」拉取新邮件(宿主服务只列
INBOX 最新 20 封);live 邮件按关键词规则标注 vibe,AI 三行摘要打开时按需生成。

核心演示任务(对应评分「任务完成 / 可靠运行 / 人机协作」):**识别**(AI 心情
播报 + vibe 光环 + 星轨气泡)→ **阅读**(AI 三行摘要先于正文)→ **提议**(语气
滑杆五档实时改写,明确收件人)→ **授权与结果核验**(单击发送 →「已随波寄出」,
收件箱出现「已回复」胶囊)→ **失败处理**(练习开关:发送失败 → 草稿保留 → 重试
成功)→ **真实宿主调用**(card-host 如实拒绝模型请求并标注;配置过 AI providers
的 Shell 中产生真实输出)。

## 在 OctoSense 桌面 Shell 中运行(最强演示)

一次性准备(完整说明见 `../octosense-local-hub/README.md`):从本地 OctoSense 检出
构建 Shell(`python tools/setup.py` 后
`cargo build --release -p octosense --no-default-features --features app-hub`),
把提交包发布到本地 hub,然后带环境变量启动:

```sh
set MAKEPAD_REMOTE=8147
set OCTOSENSE_HUB_ANCHOR=<../octosense-local-hub/README 中的 anchor 公钥>
set OCTOSENSE_APP_DATA=D:\Coding\Rust\agenticapp26\octosense-local-hub\device
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\octosense.exe --test-action launch-hub:vibemail
```

Shell 经签名验证的目录准入提交包(同 id、同字节),将其作为窗口管理器客户端启动,
并由**自带的 Mail 服务**处理 `mail.*`:「我的 → 添加账号」唤起官方「OctoSense ·
Add a mail account」面板(地址 / 密码 / IMAP-POP3 / 服务器端口),错误凭据被真实
服务器拒绝;连接成功后「刷新」经 `mail.sync` 拉取真实收件箱。该 Shell 同时注册
`model` 服务——配置过 providers 的话,AI 三行摘要、语气改写与心情播报在其中
走真实一次性模型调用(0.7.8 起首开即取正文与摘要并自动上屏)。三态主题跟随 Shell 亮暗(0.6.15 起的方向语义,实测双向 ~1-2 秒跟随)。

## 运行证据

`evidence/` 下全部为真实运行截取 / 记录(0.7.x 界面;ev-01..10、商店截图与
ev-13..16 均为 2026-10-09 在当前 card-host 重建版上重截):

| 证据 | 内容 |
| --- | --- |
| `ev-01..07.png` | 启动收件箱(时间问候 + 心情播报)/ vibe 筛选激活指示 / Mira 详情 AI 三行摘要 / 语气滑杆真诚档 / 正式档 / 单击发送已随波寄出 / 收件箱「已回复」胶囊 |
| `ev-08/09.png` | 练习开关模拟发送失败(失败重试按钮)/ 关闭开关后重发成功 |
| `ev-10.png` | 炭黑暗色主题(设置屏切换) |
| `ev-13..16.png` | 商店形态邮件流程:未添加账号态 / 宿主登录面板 / 错误凭据真实拒绝 / 取消回未添加态 |
| `ev-20/21.png` | 桌面 Shell 真实邮件首开实证(0.7.24):京东验证码邮件首开即出模型生成三行摘要(验证码/时效/保管要点)+ 完整正文;网易营销邮件摘要如实说明正文无可读文案 |
| `ev-mail-log.txt` | card-host 邮件流程服务侧留痕(含服务器原文拒绝) |
| `hub/` | 评审包:`review.json`(hub scan 问题包,0.7.26 字节生成)+ `SUBMISSION.md`(七问书面回答,已按 0.7.26 更新);`ISSUE.md` 为 submit-app.yml 表单各字段的答案底稿 |

练习数据边界(按黑客松 FAQ):八封练习邮件(Mira 海边小屋 / 云服务账单 / Aurora
周报 / GitHub / 读书会 / 外婆桂花 / 设计双周报 / HR 黑客松)与发送失败模拟为本地
练习数据;邮件路径是**真实的**(平台 mail 宿主服务,凭据在宿主面板收集、宿主侧
保存);模型调用是**真实的宿主请求**(一次性、schema 校验)。

## 状态与剩余人工步骤

- **提交通道已迁移到 GitHub publisher 工作流**(0.7.26 起;App-Hub RC1 文档
  `docs/SUBMITTING.md` 的新默认路线,新应用无需发行者私钥):

  ```sh
  hub stamp bundle                              # 可移植摘要(app-contract 1.x)
  hub check bundle --allow-unsigned             # 可编辑源码门禁 → PASSED
  # .github/workflows/publish-app.yml 已装(tools/octo publish-github)
  git tag -a v0.7.26 -m "…" && git push origin main v0.7.26
  # → tag 工作流:publisher-prepare → GitHub Sigstore 证明 → publisher-verify/pack
  #   → release 资产 app.bundle.pack.json + release-receipt.json
  hub publisher-unpack app.bundle.pack.json --out review-bundle
  hub publisher-verify review-bundle            # 下载包本地核验
  ```

  旧版 0.7.25 曾按 legacy Ed25519 路线完成发行者签名(门禁零警告,tag 已推送),
  因上游摘要口径改版(平台原生分隔符 → 可移植路径)该 tag 的清单摘要已不被
  当前门禁接受,按官方规则「已推送 tag 不可移动」升版重制;发行者密钥
  `yzbtdiy` 保留在仓库外备用。

- 本地演示 hub:`../octosense-local-hub/` 收录 0.7.25(legacy 目录;`run.cmd shell`
  演示用;后续按「hub 拒绝重发同版本」规则升版)
- 机器可读的状态清单(已验证项 / 未验证边界)见 [validation.json](validation.json)
- 剩余人工步骤(发布者本人):
  1. 在
     [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/new?template=submit-app.yml)
     按 **Submit an app 表单**开 `Submit vibemail 0.7.26` issue(各字段答案见
     `evidence/hub/ISSUE.md`,工作流运行 URL / release 链接开 issue 时回填)

## 隐私

见 [PRIVACY.md](PRIVACY.md);商店 listing 中的隐私政策 URL 指向本仓库同一文件。

## 近期版本

- **0.7.26** —— **提交通道迁移 GitHub publisher 工作流 + 新摘要口径重制**。
  上游 App-Hub 在 10-06~10-08 连续演进:bundle 摘要改为跨平台可移植口径
  (相对路径以正斜杠入哈希,Windows/Linux 一致——旧口径把平台分隔符计入,
  已 tag 的 0.7.25 签名清单在新门禁下 REFUSED,按「已推送 tag 不可动」规则
  升版本);提交通道改版为 GitHub publisher 路线(新默认:`.github/workflows/
  publish-app.yml` 在 tag push 时构建 pin 修订的 hub、publisher-prepare、
  GitHub Sigstore 证明、publisher-verify/pack,产出 release 资产;新应用不再
  需要发行者私钥;issue 改用 submit-app.yml 表单)。应用代码零改动——0.7.26
  与 0.7.25 的 main.splash 字节相同,仅 manifest 升版、剥签名、新口径 stamp。
  同轮开发环境跟进:card-host 按当前源码重建(上游 10-06 的整词换行修复 +
  makepad re-pin 32d6415f script-compute-VM),参考 mail 服务重新接回本地
  App-Hub 检出(上游已把 mail-service 移出该仓库,本地 vendor 到
  crates/mail-service 并在 card-host 注册——两项均为本机开发改动);在新
  运行时上全量复核:8/8 单测、6/6 路线、412/700/1200 双审计全绿、截图与
  ev-01..10 重截、商店形态邮件流(真实服务器拒绝)ev-13..16 重截;ci/verify.sh
  摘要复验同步改为可移植口径。
- **0.7.25** —— **「都成了正文截取」= 模型日预算打满**(用户实测:所有 AI 三行摘要
  降级为正文截取、心情播报降级为固定文案)。宿主 model 服务对每个应用有**预算台账**
  (`device/.host/model/ledger.json`,默认 6 次/分、100 次/天、10 万 tokens/天,UTC 日
  重置),打满后所有调用被拒。两层修复:(1) **应用侧根治**——0.7.24 前的「3.2 秒
  重发循环」在模型还在思考时连发最多 4 次、每次计费,一次浏览就能烧穿全天配额;
  循环已删,改为**单次请求 + 30 秒耐心**(超时如实标「服务不可用」),限速/额度
  拒绝按宿主文案分类为「限速·重开重试」「今日额度用完」,限速与瞬时失败在**下次
  打开邮件时自然重试**(一次一调用,额度用尽不重试);失败回退统一显示列表摘句
  并由状态词说明原因。(2) **本地开发环境取消限额**——台账 `limits` 支持按应用
  覆盖且会被服务持久保留,本地 hub 已给 vibemail 设
  `per_minute 120 / calls_per_day 100000 / tokens_per_day 50000000` 并清零当日
  计数(改台账必须先停 Shell:内存台账会回写覆盖)。Shell 实证:摘要/播报恢复
  「模型生成」(3-6 秒),整轮验证仅消耗 5 次调用;6/6 路线、三档审计、8/8 单测、
  门禁 PASSED
- **0.7.24** —— **首开摘要秒回 + 「邮件正文为空」修复**(用户实测:三行摘要
  必须二次打开邮件才有、且 AI 称有正文的邮件「正文为空」)。带日志复现定位
  三个根因:(1) gen_summary/gen_tone 回调读 `r.data.meta.model`——Shell 的
  model 服务 meta 只含 class/requested/attempts/usage/budget,**没有 model 字段**,
  属性读取当场抛 not found,回调死在 `soft_repaint()` 之前——摘要其实已生成并
  写入状态,只是永远无人重绘,直到第二次打开的手势重绘才现身;删除该读取
  (改写标注固定为「模型改写」)。(2) 详情页读 `m.preview`——live 邮件的列表
  摘句存在 `snippet` 字段,`preview` 属性不存在,首开正文未到时整次渲染被
  Shell 丢弃(`on_render closure failed`),改读 `m.snippet`。(3) 摘要请求与
  正文拉取同拍发出,body 恒为空串,模型如实回答「邮件正文为空」——改为
  poll_step 等正文落地后再发(取件失败则如实标「服务不可用」)。顺带:模型
  失败回退不再用 `.split`(Shell 无字符串方法,会抛),改用列表 snippet 单条
  回退;设置页移除临时 dbg 行。Shell 实证:京东验证码邮件首开 2 秒内出真摘要
  (验证码/时效/保管提示),网易营销邮件如实总结「正文为 CSS 无可读文案」,
  语气滑杆「正式」档闲置 2 秒出「模型改写」,日志零错误;6/6 路线、三档审计、
  8/8 单测、门禁 PASSED
- **0.7.23** —— **live 星轨配色真修复**(用户实测:真实邮件星轨全是绿色):两段式根因——(1) `mod.std.index_of` 在 Shell 的 makepad 运行时不可达(0.7.14 引入),live 列表回调死亡,真实邮件加载不出来;(2) 修回 `s.search` 后仍有 `address.len()` 散列(0.7.16)——makepad VM 无字符串 len,继续杀死回调。最终:分类器保持 `s.search` 词表(真实世界词表 + 散列配色保留,散列改用 search 位置和,替代 len),live_mail 恢复直接字段访问;Shell 实测 9 封真实邮件全部加载且颜色多样(安全/订单→focus 橙、AI 工具通知→calm 绿、未知发件→joy/link/spark 散列);6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.16** —— **Shell live 列表“消失”的真根因修复**(用户实测:账号已连接、同步成功,列表却永远停在练习数据):0.7.12 给 classify_vibe 加的「自己发的邮件归 focus」规则引用了文件后部声明的全局 account_addr——Shell 运行时里,**回调内嵌套函数读取这种后声明全局直接抛 not found in scope**(card-host 不报错,因为 card-host 根本没有 live 邮件可触发该路径),mail_list 回调当场死亡,live 邮件永远写不进去。删除该引用(自我邮件按主题正常分类);6/6 路线、三档审计、8/8 单测、门禁 PASSED
- **0.7.20** —— 同步等待期**诚实提示**:live 账号的 IMAP 同步 + 回复泵送需要约一分钟(平台限制),期间收件箱心情卡下方显示「真实邮件正在同步,稍候片刻…」,不再让等待看起来像失败
- **0.7.18** —— **真实邮件“消失”的真根因修复**(用户实测:账号显示已连接,列表却停在练习数据):`mail_check` 的账号回调在**回调上下文里直接发 `mail.sync`**——Shell 把这类回调上下文发出的请求回复一并丢掉(与列表重发是同一类问题,0.7.9 只修了正文/摘要这一半),于是已连接 ✓、同步 ✗、练习数据永远驻留。修复:账号回调只置 `want_sync` 标志,`mail_load` 改由 poll_step 顶层节拍代发——poller 通道的回复送达长期可靠;至此手势/回调上下文的宿主请求**全部**走 poller 队列(accounts 除外,其回复从未丢失);6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.17** —— **live 星轨配色真修复**:0.7.12~0.7.16 的 classify 用了 `mod.std.index_of`(card-host 的 octoscript 才有;Shell 的 makepad 运行时 没有——live 列表回调死在上面,真实邮件永远加载不出来,星轨只剩练习数据),全部改回双运行时都证实的 `s.search()` 探测(词表扩充与散列配色保留);**live 邮件首开零往返**:详情页先显示列表自带 preview 摘句(Shell 回复只在输入事件被泵送,等待靠 preview 而非轮询),正文/摘要异步到达后自动升级;6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.16** —— **live vibe 关键词词表重写 + 散列配色 + 首开 preview**(用户实测:真实邮件星轨全绿——词表只覆盖练习数据语境):focus 扩订单/验证/安全/物流/支付等行动词,服务通知类归 calm,社群/长文词表扩充;仍无法识别的按发件人确定性散列分散到 joy/link/spark/calm(同一发件人稳定同色),星轨从此多彩;live 邮件首开零往返显示列表自带 preview 摘句(Shell 回复只在输入事件被泵送,等待靠 preview 而非轮询),正文/摘要异步到达后自动升级;气泡短名:纯邮箱地址取 @ 前段、超 8 字截断(受限于 Shell 运行时无 index_of/slice,实现退回全名——见 0.7.13);6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.14** —— **live vibe 分类交给模型 + Shell 方法调用修复**(0.7.13 实测 Shell 里 live 列表回调仍死——`mod.std.text.*` 路径不存在,text 方法直接装在 std 模块上):live 路径全部字符串操作改写为 `mod.std.index_of/slice/len/replace_all/split/trim` 限定调用;0.7.12 的关键词重写 + 散列配色保留;6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.12** —— **live 邮件 vibe 分类交给模型**(用户实测:真实邮件星轨全是
  绿色——关键词词表只覆盖练习数据语境,真实邮件几乎全部落入 calm 兜底):
  0.7.12 把心情播报与 vibe 分类合并为**一次 model.complete**——列表可见信息
  (主题 + 发件人 + 当前规则标注,≤12 封,不含正文与地址)进模型,返回每封的
  vibe(focus/joy/calm/spark/link 五选一)+ 30 字心情句;关键词规则保留为
  card-host 无模型时的即时兜底与降级(界面无变化);气泡短名同步优化:纯
  邮箱地址取 @ 前段、超 8 字截断;6/6 路线、三档审计、8/8 单测、门禁
  PASSED,截图证据重截,Shell 实测多色星轨
- **0.7.11** —— **首开即有内容 + 冻结修复**(用户实测:0.7.10 详情页长时间
  无响应、正文空白):①live 邮件首开**零往返显示列表自带 preview 摘句**
  (正文/摘要的异步回复到达后再升级显示——Shell 里回复只在输入事件时被
  泵送,等待无法靠轮询消除);②clean_html 死循环修复:`s.search()` 与
  `s.index_of()` 大小写语义不一致导致 cut_blocks 永不收缩(UI 线程冻结、
  点击全部无响应),统一 index_of 查找并加迭代上限(style/script/注释 40 次、
  剥标签 600 次);6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.10** —— **营销邮件正文解析修复**(用户反馈「部分邮件解析异常」:网易
  营销邮件把整份 HTML 文档当正文——@media 规则、标签全部裸奔在详情页):
  正文落地经 clean_html 清洗(按分隔符摘除 style/script/注释块,index_of +
  slice 循环剥其余标签,br/p/div/h/li 转行,解码常见实体);摘要生成中先以
  正文前几行灰字占位(0.7.9 正文通道修好后摘要有料可占),重试耗尽(4 次)
  如实转「服务不可用」+ 正文摘录兜底;6/6 路线、三档审计、8/8 单测、门禁
  PASSED,截图证据重截
- **0.7.9** —— **Shell 首开数据不到达的真修复**:0.7.7/0.7.8 两轮都只治了
  标症——实测(静置探针 33s)真正的问题是 Shell 里**从手势处理器发出的宿主
  请求,其回复要等下一次输入事件才被泵送**(首开邮件:正文与摘要的回复全部
  积压,重开的点击恰好泵送了它们,所以"重开就有")。修复:open_mail / do_send
  / 归档恢复的心请播报重问改为**置队列标志**,poll_step 在顶层节拍代发正文
  (mail.message)、摘要(model.complete)、已读标记、live 发送与心情播报
  ——poller 通道的送达自 0.7.0 列表加载起长期可靠;另加**节拍重试**(正文
  ≤5 次 / 摘要 ≤4 次)、正文获取失败如实显示原因、详情页等待提示「宿主响应
  等待中 · 轻点任意处立即获取」
- **0.7.8** —— **Shell 首开数据不到达的真修复**(0.7.7 的 soft_repaint 只解决
  了「回调 repaint 到不了屏幕」,实测用户仍见首开无正文无摘要数十秒——真正的
  问题是 Shell 里**从手势处理器发出的宿主请求,其回复要等下一次手势才被泵送**;
  0.7.0 的列表「poller 重发」就是这个问题的第一种解法):open_mail / do_send /
  归档恢复的心请播报重问全部改为**置队列标志**,poll_step 在顶层节拍代发
  正文(mail.message)、摘要(model.complete)、已读标记、live 发送与心情播报
  ——poller 通道的回复送达已被 0.7.0 列表加载长期证实;**连带修复 0.7.7 的
  软化脚本误伤**:poll_step 冲刷与主题翻转被一并软化成 soft_repaint(死循环
  置脏、从不真正渲染),改回 repaint();并修复 toggle_outage 一处早前损坏的
  语句;6/6 路线、三档审计、8/8 单测、门禁 PASSED,截图证据重截
- **0.7.7** —— **Shell 首次查看邮件 AI 摘要不显示的修复**(用户实测:摘要数据
  第一次打开就已取回,但界面不画,第二次打开才出现——Shell 隔离运行时里,
  宿主回调内的 `repaint()` 到不了屏幕,而顶层 poller 的可以,主题跟随早已
  证明后者有效):新增 `soft_repaint()` 置脏标记,16 处回调/定时器内的重绘
  全部改走它,poller 每 0.4s 冲刷;手势入口的立即 repaint 不变。附带修复
  Shell 侧同类隐患(邮件列表到达、正文取回、发送结果、心情播报返回的刷新)
- **0.7.6** —— **心情播报改模型动态生成**(用户反馈:固定文案不像 AI):
  一次性 model.complete 以列表可见信息(主题 + vibe 标注,≤12 封,不含正文
  与地址)生成 30 字内氛围句;卡片如实标注「模型生成 / 生成中… / 固定文案」,
  无模型服务或请求失败回落固定计数行;boot、live 列表加载、归档/恢复后重新
  生成。**语气滑杆扩为五档**(用户反馈三档偏少):新增 轻松幽默 / 简洁专业,
  练习数据 8 封 × 2 档新文案,默认档 自然友好
- **0.7.5** —— **宽度自适应 + 悬浮导航**:根列改流式 Fill(probed:固定 660
  居中在 412 窗口不会钳位而是溢出裁边,0.6.x「固定宽钳位」结论作废;脚本无
  窗口尺寸 API——仅 math/json/text/array/object + host 服务),412 即手机
  设计、宽窗自然铺满;语气滑杆/星图由 Fill 包裹居中;**滑杆重设计**为三等
  分列(点/滑块/点击区同列结构性对齐——修复自 0.7.0 起真诚/正式档滑块不压
  点的老毛病);**星轨画布 Fill 宽**:锚点全比例化(漂移同步),星座随窗口
  散开,不再留固定 380 的窄条死边;**悬浮导航胶囊回归**(玻璃胶囊沉底悬浮,
  列表从其下方滚过)+ **导航闸门**:go() 盖 anim_t 时间戳,0.25s 内的内容
  处理器一律忽略(实测穿透:胶囊压卡时点导航会同时打开卡片),五屏底部
  留白 36→92
- **0.7.4** —— 筛选芯片改**等宽 Fill 均分**(0.7.3 在桌面 Shell 实测:Shell
  运行时的 CJK 字形度量比 card-host 宽,固定宽芯片仍会裁掉「连接」——等宽
  自适应任何字体度量);0.7.3 为本地 hub 发布版本号(hub 拒绝重发同版本,
  修复须升版);发布流程:hub stamp + 发行者签名 + 门禁 → 复制至
  octosense-local-hub/bundle → working.key 重签 → hub publish(sequence 35)
  → verify → device 根同步,Shell 实测六芯片完整、时间问候(早上好)、
  真实邮箱(yeah.net 6 封)在线
- **0.7.2** —— 图标全量按设计稿的 lucide 几何重画(从展示页 bundle 提取原始
  path 数据换算到 16 网格:inbox 收件托盘、orbit 双弧+行星环+双卫星、
  pen-line 双缘笔+下划线、settings-2 双横线+圆环旋钮、五角星、archive、
  sparkles 大✦+加号+圆点、arrow-left、send 纸飞机、check;填充星形与圆环
  用叠圆近似,笔画 1.5u);背景四枚大氛围圆**移除**——设计稿的光晕只在每张
  邮件卡上(以及展示页手机背后),手机列改不透明纸底,宽窗口两侧留纯纸底;
  新增两条运行时结论:**(1) View 字面量内调用的铸件辅助函数只保留首尾根**
  (idiag 九格只剩两端,七格探针证明加法/let/乘积参数形式全部正常,改为
  每格内联字面量分数);**(2) 收件箱按帧重绘会打断滚动拖拽**(0.7.1 已证,
  星轨不受影响);dbg_pixels2 亮色收件箱的霓虹断言改 #c9b300 换色点(与
  参考的亮底对比度处理一致);5 张商店截图与 ev-01..10 重截;星形/纸飞机
  加密节点链消虚感,vibe 筛选芯片收紧(内边距 11/间距 4)使六枚全部落位,
  消除右缘被裁芯片的"悬浮圆"观感;**光环全量收敛**(实测反馈:离散圆盘
  近似模糊光晕时,只有连接蓝显形为"多几个圆")——星轨气泡光晕与邮件卡/
  详情卡光环全部移除,vibe 色由未读点/芯片/气泡本体承担,aura 族仅保留
  品牌小光斑、空态与设置头像三处环境光;星标图标按 lucide 五角星轮廓
  密铺重画(沿真实路径顶点布置圆盘 + 五边形核心,11px 也读作五角星);
  **情绪芯片改纯文字 + 各自 vibe 色**(用户反馈小尺寸图形发虚):筛选芯片
  去字形、按 vibe 上淡色底(激活反白),"全部"保持中性;卡片情绪芯片去字形
  加大字号;vibe_glyph/flame/bubble/sun_small 图形族退役(leaf 保留于空态);
  **时间自适应问候**:std.local_time() 在 card-host 报 UTC(宿主未设偏移),
  应用内 +8 校正,5-12 早上好 / 12-14 中午好 / 14-18 下午好 / 其余晚上好,
  poller 检测词变化仅收件箱重绘;**文案去海味**:「海面有 N 朵浪」→
  「你有 N 封未读邮件」、「今天的海面:…」→「今天有 …」(心情播报保留)、
  「这片海域一片平静」→「收件箱一片平静」、slogan「邮件有情绪」→
  「有情绪的邮件」(settings/listing/README 同步);启动探针与全部路线
  expect 由「海面有」改「未读邮件」;筛选芯片行去滚动化——芯片侧边距
  12→10 后六枚全部落位,整行改普通流式布局,ScrollXView 的悬浮横向
  滚动条不再出现,连接芯片也不会被右缘裁断
- **0.7.1** —— 对齐设计原型的第二轮美化(无状态栏——宿主窗框自带,与 0.7.0
  一致):字号阶梯整体上调至参考值(问候/屏标 22,卡发件人 13、主题 12.5、
  摘录 11.5,详情主题 17、正文 13,摘要行 11,摘要要点 12,底栏 9/16 图标),
  面板圆角统一 16(摘要卡/回信预览/AI 摘要盒);详情星标/归档胶囊改 paper2
  凹陷底(参考 --paper-2);写信输入框改透明底 + 12.5px(参考 bg-transparent,
  状态色全覆写);主题快切胶囊 68×36/旋钮 28(参考 h-9 w-[68px]);星轨气泡
  改参考短名(`sender.slice(0,6)` 语义,新增 `bname` 字段)+ 9px 标签 +
  双层高光(宽柔光 + 紧核,radial-gradient 手感)+ 光晕增浓(α 30/18 对齐
  参考阴影 55);修复光晕方角(环大于画布被裁成方形——0.7.1 实测,气泡包裹
  画布扩至 1.66× 并重推导锚点保持圆心);空态加绘制叶片字形;运行时结论:
  收件箱按帧重绘会打断滚动拖拽(路线 5/6 无法滚到列表底部,实测回退——问候
  光环保持静态,与参考的漂移光环取舍);run_routes 寻达加强(+420 步进),
  run.cmd demo 修正为手机宽度(商店截图几何 412×860,旧代码 1200 与产物
  矛盾);dbg_pixels2 采样框对齐 0.7.1 几何(写屏全高,收件箱以薄荷 chip
  混色替代下方折叠的连接蓝);5 张商店截图与 ev-01..10 全部重截
- **0.7.0** —— 按 OctoSense 设计原型参考**完全重构**:应用从桌面三栏改为 412px
  手机列布局(宽窗口居中,两侧静态氛围光晕;单一 on_render 根整窗重铸;无状态栏
  ——宿主窗口自带窗框,内容直接开始)。新 vibe
  系统:五种情绪(coral 专注 / neon 愉悦 / mint 平静 / pink 灵感 / blue 连接,
  双主题不变色;neon 点/要点在亮色换 #c9b300 保对比),邮件卡带情绪光环与 vibe
  筛选 chips(激活显示筛选指示);新星轨屏:气泡大小=重要度(52+imp×0.62)、
  颜色=vibe、双层柔光晕、sin/cos 漂移(0.15s 定时器仅星轨屏重绘)、点按直达;
  新详情屏:AI 三行摘要卡(✦ 彩色要点 + 五态来源标注)+ 星标/归档/回复;新写信
  屏:语气滑杆三档(标签可点)+ 单击发送状态机(发送中/已随波寄出/失败重试,
  取代 0.6.x 两步确认;controller.py 孪生与 8 单测同步重写);新「我的」屏:主题
  三态 + 能力声明 + 账号管理 + 练习开关。新配色:暖纸 #eaeae3 × 炭黑 #151413,
  参考透明度按各自底色预混。数据集更换为参考原型八封练习邮件(每封含三种语气
  回信文案,Mira 三条与参考逐字一致);manifest 增列 storage 能力(4 MiB)。
  运行时结论:底栏导航改**流内停靠**(点击会穿透所有重叠 GestureView——实测);
  图标族新增火焰/叶片/气泡/托盘/行星环/斜笔/左折返/纸飞机(沿用 0.6.17
  拼绘语法,无字体 dingbat)。run_app.py 启动前自动生成去签名运行副本(card-host
  --allow-unsigned 拒绝带签名 manifest);启动探针改「海面有」;路线测试重写为
  6 条(vibe 筛选/星轨与主题/语气滑杆/单击发送/故障重试/归档恢复,6/6 通过);
  宽度审计改为 412/700/1200 三档(缺失审计每屏全新实例——长实例采集与点击相互
  干扰,导航点击必须精确匹配:摘要行「在「我的」里添加」会吃掉子串点击);
  5 张商店截图与 ev-01..10 证据全部重新截取;BRIEF.md 按设计流程第 1 步补写
- **0.6.17** —— 图标全量重设计:整套界面图标由 RoundedView 原生拼绘的统一图标族
  取代字体 dingbat(23 个图标共享同一语法,光学归一化,放大检视无歧义读法);
  品牌标志 VibeMark 重绘;商店图标重绘(详见 git 历史)
- **0.6.16** —— Agent 小队导航图标(机器人徽章);**0.6.15** —— 修正三态主题方向
  颠倒;**0.6.11** —— 三态主题(跟随系统/亮色/暗色,持久化);**0.6.10** —— 真实
  邮箱在桌面 Shell 内完整闭环(sync 先行/常驻轮询/正文按需拉取,实测 yeah.net
  5 封落列表);**0.6.0** —— 按网页参照重构为暖纸×森林墨绿桌面三栏;**0.5.0** ——
  森林墨绿双主题;**0.4.0** —— 亮暗双主题;**0.3.x** —— 桌面横向卡片布局
  (0.6.x 桌面三栏与 Agent 小队详见 git 历史)
