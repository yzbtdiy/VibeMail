# VibeMail(vibemail)

「Agentic App 黑客松 2026」场景 01(邮件)参赛应用。VibeMail 是一个桌面横向布局的
Agentic 邮件应用:左侧导航栏 + 邮件卡片列表 + 常驻阅读栏(点击卡片原地展开,无页面
跳转),内置 AI 分诊、摘要、待办提取与回信起草;真实收发经平台 mail 宿主服务完成,
AI 能力经宿主 model 服务完成——凭据与密钥始终留在宿主侧,不经过应用、不进提交包。

| | |
| --- | --- |
| 应用 ID / 版本 | `vibemail` / **0.5.5** |
| 门禁状态 | `hub check` — **PASSED**(仅余未签名警告,签名属人工步骤) |
| 申请能力 | `mail` + `model`(共两项,按最小化原则) |
| 实测平台 | Windows 10(26100)——唯一实测平台,布局审计宽度 1000 / 1200 / 1440 |
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

- **智能收件箱**:AI 分诊横幅(实时计数)、筛选胶囊、优先级条、标签;邮件以卡片列表呈现
- **三栏桌面布局**:邮件列表 | 原地阅读栏 | AI Copilot,三栏各自独立滚动(与网页版
  参照一致);1200/1440 宽度下收件箱为「列表 + 占位卡」,阅读态为 master-detail
- **阅读栏 + AI Copilot**:AI 摘要(要点 / 建议动作 / 会议识别 / 情绪标签)、待办
  提取、语气洞察、一键智能回复
- **AI 写信**:提示词起草、语气选择、可编辑 AI 草稿;模型不可用时回退本地模板并明确标注
- **回复生命周期状态机**:草稿待发送 → 两步确认 → 发送中 → 已发送 / 失败(保留草稿
  可重试),收件箱胶囊与阅读栏状态条始终一致(`service/controller.py` 为其验证孪生,
  8 个单测)
- **真实邮件**:经平台 mail 宿主服务走真实 IMAP/SMTP;账号在**宿主自己的登录面板**
  添加,授权码只存宿主保险库;无该服务的环境(原版 card-host)如实显示不可用并回退
  已标注的练习数据
- **真实模型调用**:AI 摘要与起草为一次性 `model.complete` 调用(schema 校验、日
  预算);0.5.4 起界面显示宿主**实际使用的模型名**(读取应答的 `meta.model`);0.5.5 针对高 DPI Shell 重排三栏(侧栏 240 / 列表 310 / 阅读栏自适应 / Copilot 260),1000 / 1200 / 1440 三档审计全绿
- **双主题**:森林墨绿(默认)× 暖沙亮色,顶栏胶囊一键切换,内容与布局不变
- **Agent 小队**:统计、开关、自动化程度、实时活动流与审批(练习数据,遵守
  no-facts 原则)

## 能力声明

应用只申请实现功能所需的两项能力(未申请即未授予):

| 能力 | 支撑的功能 | 不可用时的行为 |
| --- | --- | --- |
| `mail` | 收件箱 / 阅读 / 起草 / 发送全流程(`mail.accounts`、`mail.add_account`、`mail.list`、`mail.message`、`mail.mark_read`、`mail.send`) | 横幅如实显示「无服务应答」,回退已标注的练习数据 |
| `model` | 「AI 生成」摘要与「生成草稿」两个按钮 | 宿主原文拒绝显示在界面上,回退明确标注的本地模板 |

无网络主机声明(`hosts {}`)、无存储之外的额外请求。

## 目录结构

```text
route_test.json 声明式路线测试:4 条点击路线(原地阅读与模型不可用态 /
               两步确认发送 / 故障-保留-重试 / Agent 审批与主题切换)
validation.json 机器可读状态清单:已验证项与未验证边界(诚实记录)
source/        设计源:重做所参照的网页源码 + design-brief.md
               (调色板、逐视图要点、响应式规则)
service/       回复生命周期 reducer(controller.py,main.splash 状态机的
               验证孪生)+ unittest(test_controller.py,8 用例)
bridge/        开发层(现为可选):IMAP/SMTP ↔ 本机 HTTP 网桥(凭据只存
               config.json,已 gitignore;5 个解析单测)——已被平台服务
               路线取代,不进提交包
dev/           开发层:网桥适配器(替换 main.splash 的 MARKER:ADAPTER 块)
scripts/       run_app.py:run.cmd 的内核(launch / demo / mail / shell /
               check / stop 各子命令)
               drive-demo.py:经 Makepad 远程桥驱动真实 card-host 窗口
               跑完整演示任务并截取全部证据(驱动会把真实鼠标停靠到
               远处——OS 光标事件会吞掉合成点击)
               drive-mail.py:驱动提交包在 card-host 中走平台 mail 服务
               (无账号态 → 宿主登录面板 → 真实拒绝 → 取消;截图可再生)
               official_sheet_run.py:同一流程在 OctoSense 桌面 Shell 内
               (官方面板 + 官方服务的真实 imap.qq.com 拒绝)
               ai_test.py:Shell 内 AI 摘要 / 起草驱动(ev-22..24)
               audit_missing / audit_overflow:宽度审计
               dev_bundle.py:组装 build/dev-bundle(仅开发,不入库)
               run_routes.py:执行 route_test.json 的通用路线跑器
               (失败时把截图 / 组件树 / 日志落到 evidence/routes/)
evidence/      运行证据(见下文「运行证据」)
bundle/        THE SUBMISSION —— 唯一提交部分
  manifest.json    id、版本、能力、完整性哈希(hub stamp 写入)
  listing.json     商店展示信息(副标题、描述、截图、发布者)
  main.splash      应用本体(Splash 脚本,无编译步骤)
  assets/icon.svg  图标(listing 所指)
  screenshots/     01..05 真实截取(inbox / read / write / agents / light)
```

## 环境要求

- Windows 10(26100)——唯一实测平台;其余平台未验证
- Rust stable(rustup)——用于构建带 mail 服务的 card-host
- Python 3.9+,无第三方依赖
- 同级目录下的 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)
  检出(`crates/card-host/src/host.rs` 已接好 `octosense_mail_service::register()`)
- 桌面 Shell 演示另需:本地 [OctoSense](https://github.com/OctoSense-org/OctoSense)
  检出与本地签名 hub 目录(`../octosense-local-hub/`,见其 README)

## 快速开始

`run.cmd` 是一键入口(内核为 `scripts/run_app.py`):

| 命令 | 作用 |
| --- | --- |
| `run.cmd` | 以桌面宽度(1200×860)在 card-host 中启动应用 |
| `run.cmd mobile` | 以手机宽度(412×860)启动(不支持的布局,仅供对照) |
| `run.cmd demo` | 桌面宽度 + 完整证据演示(drive-demo.py) |
| `run.cmd mail` | 商店形态邮件流程(宿主面板 → 真实拒绝 → 取消) |
| `run.cmd shell` | 启动真实 OctoSense 桌面 Shell(本地签名 hub) |
| `run.cmd shell-drive` | Shell + official_sheet_run.py(ev-17..19 流程) |
| `run.cmd check` | 单元测试 + hub stamp + hub 门禁检查 |
| `run.cmd stop` | 结束全部测试实例(card-host / octosense) |

## 复现与验证

先构建带 mail 服务的宿主(一次性):

```sh
cd ../OctoSense-App-Hub && cargo build --release -p octosense-card-host
# 产物在 %CARGO_TARGET_DIR%(本机为 D:\Users\yzbtdiy\Cache\CARGO_TARGET)
```

再以提交包运行(路线回归与证据流各用一个全新实例;宽度 1200×860,
手机宽度 412×860 为不支持的布局,仅供对照):

```sh
python -m unittest discover -s service      # 状态机单测
set MAKEPAD_REMOTE=8146
rem 路线回归:route_test.json 的 4 条路线,真实点击 + 逐步断言
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe --bundle bundle ^
    --app-data .local-state --allow-unsigned --stamp --size 1200x860
python scripts/run_routes.py 8146           # 4/4 路线通过则退出码 0
curl -s 127.0.0.1:8146/quit
rem 证据流:重起一个新实例,重写 bundle/screenshots 与 evidence/
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe --bundle bundle ^
    --app-data .local-state --allow-unsigned --stamp --size 1200x860
python scripts/drive-demo.py 8146           # 完整生命周期 + 模型不可用态
python scripts/drive-mail.py 8146           # 商店形态邮件:面板/真实拒绝/取消
../OctoSense-App-Hub/target/release/hub.exe stamp bundle
../OctoSense-App-Hub/target/release/hub.exe check bundle --allow-unsigned
```

接入自己的邮箱:运行 card-host,点「添加账号」,在**宿主面板**里输入邮箱地址和服务商
授权码(QQ / 163 / Gmail 自动识别服务器)。授权码只存宿主侧
(`.local-state/.host/mail/`),不经过应用,也绝不进入提交包。

核心演示任务(对应评分「任务完成 / 可靠运行 / 人机协作」):**识别**(AI 分诊横幅 +
优先级条 + 摘要卡)→ **提议**(可编辑 AI 草稿、明确收件人、语气、一键智能回复)→
**授权**(两步确认发送)→ **结果核验**(阅读页「已回复」状态条与收件箱胶囊同步)→
**失败处理**(练习场景开关:发送失败 → 草稿保留 → 重试成功)→ **真实模型调用**
(ev-09/ev-10:card-host 如实拒绝并显示在界面上;同一按钮在配置过 AI providers 的
OctoSense 桌面 Shell 中产生真实模型输出)。

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
python scripts/official_sheet_run.py 8147
```

Shell 经签名验证的目录准入提交包(同 id、同字节),将其作为窗口管理器客户端启动,
并由**自带的 Mail 服务**处理 `mail.*`:「添加账号」唤起官方「OctoSense · Add a
mail account」面板(地址 / 密码 / IMAP-POP3 / 服务器端口),错误凭据被真实
`imap.qq.com:993` 拒绝(ev-19)。该 Shell 同时注册 `model` 服务——配置过 providers
的话,应用的 AI 按钮在此环境中走真实一次性模型调用(AI 摘要与起草已在 Shell 中对
接真实配置的 MiniMax 实测通过,见 ev-22/ev-23)。

## 运行证据

`evidence/` 下全部为真实运行截取 / 记录(截图逐张人工核验):

| 证据 | 内容 |
| --- | --- |
| `ev-01..08.png` | 回复生命周期:草稿待发送 / 确认 / 已发送 / 收件箱胶囊同步 / 失败 / 草稿保留 / 重试成功 / Agent 审批 |
| `ev-09/10.png` | 模型不可用态(宿主原文拒绝 + 本地回退标注) |
| `ev-17..19.png` | OctoSense 桌面 Shell 内:应用作为 WM 客户端运行 / 官方 Add-a-mail-account 面板 / 官方服务真实 IMAP 拒绝 |
| `ev-21..24.png` | 亮色主题 / Shell 内真实 AI 摘要与起草(MiniMax)/ 模型名胶囊 |
| `ev-mail-log.txt` | card-host 邮件流程服务侧留痕(`add_account / sheet.submit / sign-in failed / sheet.retry / sheet.cancel`,含 imap.qq.com 原文拒绝) |
| `ev-octosense-log.txt`、`ev-ai-test-log.txt` | Shell 运行与 AI 测试日志 |
| `final-snap.json`、`final-log.txt` | 演示结束时的完整组件树与 card-host 日志 |
| `hub/` | 评审包:`review.json`(hub scan 问题包)+ `SUBMISSION.md`(七问书面回答 + 复现说明) |

练习数据边界(按黑客松 FAQ):Agent 小队、活动流与发送失败模拟为本地练习数据;邮件
路径是**真实的**(平台 mail 宿主服务,凭据在宿主面板收集、宿主侧保存);模型调用是
**真实的宿主请求**(一次性、schema 校验)。

## 状态与剩余人工步骤

- `hub check`:`vibemail 0.5.5 — PASSED`(本地 hub 工作密钥已签名;目录 sequence 2,
  见 `../octosense-local-hub/`)
- 机器可读的状态清单(已验证项 / 未验证边界)见 [validation.json](validation.json)
- 剩余人工步骤(发布者本人):
  1. `hub keygen`(密钥保存在仓库之外)
  2. `hub sign-manifest bundle --key … --key-id <publisher-id>`
  3. `hub check bundle --publisher-key <id>=<hex>` → 无警告 PASSED
  4. 打 tag 并在 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues)
     开 `Submit vibemail 0.5.5` issue(附 `evidence/hub/SUBMISSION.md`)

## 隐私

见 [PRIVACY.md](PRIVACY.md);商店 listing 中的隐私政策 URL 指向本仓库同一文件。

## 近期版本

- **0.5.5** —— 高 DPI Shell 宽度适配:侧栏 240 / 列表 310 / 阅读栏自适应 / Copilot 260,优先级计分器紧凑化,写信工具栏精简
- **0.5.4** —— 模型胶囊与摘要胶囊显示宿主实际使用的模型名(`meta.model`),替换
  GPT-Vibe 4 占位名
- **0.5.3** —— 去掉写信页输入框的多余嵌套(提示词与 AI 草稿各一层边框,文字直接
  落在卡片上)
- **0.5.2** —— 主题胶囊与侧栏底部按钮改为原生控件图形图标(太阳 / 月牙 / 日历 /
  滑杆)
- **0.5.1** —— 三栏各自独立滚动,固定视口,修掉短栏下方露黑底;AI 服务商(MiniMax)
  在 Shell 中实测通过
- **0.5.0** —— 按最新设计完全重构:森林墨绿 × 暖沙双主题、侧栏导航、三栏收件箱、
  COMPOSE WITH AI 栏、Agent 任务面板
