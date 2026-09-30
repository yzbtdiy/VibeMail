# VibeMail（vibemail）

[English](README.md) | 简体中文

参赛「Agentic App 黑客松 2026」（场景 01 邮件）的概念应用。0.5.1 在 0.5.0 按最新 UI 设计**完全重构**的基础上，把三栏（列表｜阅读｜Copilot）改为**各自独立滚动**（与网页版一致），并修掉滚动露黑底；0.5.0（`bundle/main.splash`）：森林墨绿 × 暖沙纸感双主题（默认深林暗色、暖沙亮色，顶栏胶囊一键切换）；侧栏导航（写信·AI 起草 / 收件箱 / Agent 小队 + 邮箱文件夹 + AI 智能分类 + AGENT ACTIVE 迷你卡）；顶栏（问 Vibe Agent 搜索、运行中胶囊、主题切换）；三栏收件箱（邮件列表 | 原地阅读 | AI Copilot：摘要 / 待办提取 / 语气洞察 / 智能回复）；写信卡片 + COMPOSE WITH AI 栏；Agent 任务面板（统计 / 开关 / 自动化程度 / 实时活动流）。点击卡片即在阅读栏原地展开，无页面跳转。审计宽度 1200 与 1440（run.cmd 默认 1200x860）。AI 摘要与起草已在 OctoSense Shell 里对接真实配置的模型服务（MiniMax）实测通过——见 ev-22/ev-23。

**能力与数据口径**：应用申请 `model` 与 `mail` 两项权限。
`mail`：真实收发走平台 mail 宿主服务——账号由**宿主自己的登录面板**添加，
授权码只存宿主侧，不经过应用、不进提交包。已在**两个宿主**实测：
(1) **OctoSense 桌面 Shell 本体**（最强证据，ev-17..19）——提交包以同一
id、同一字节经本地签名 hub 目录准入（`../octosense-local-hub/`：
keygen→certify→publish，`OCTOSENSE_HUB_ANCHOR`/`OCTOSENSE_APP_DATA` 指向
本地），以 `--test-action launch-hub:vibemail` 作为窗口管理器客户端启动，
Shell 自带的 Mail 服务应答：官方「OctoSense · Add a mail
account」面板弹出，错误密码被真实 `imap.qq.com:993` 拒绝；(2) 本地
card-host 构建注册参考 mail 服务（`OctoSense-App-Hub/crates/mail-service`，
HOST-SERVICES.md 记载的宿主扩展路径，ev-13..16）。无该服务的环境（原版
card-host）如实显示不可用并回退练习数据。
`model`：AI 摘要与起草通过一次性模型服务（schema 校验、日预算）调用设备配置的
模型，密钥不经过应用；不可用回退本地模板并标注。Agent 小队与活动流为练习数据
（no-facts 原则）。

## 目录结构

```text
source/                 设计源：重做所参照的网页源码 + design-brief.md
                        （调色板、逐视图要点、响应式规则）
artwork/                退役 SVG 素材的工作副本（新版 UI 全原生绘制：渐变头像、
                        字符块图标、圆角面板——运行时 SVG 在本栈栅格化为空白，
                        因此不随包携带任何 SVG）
service/                回复生命周期 reducer（controller.py，main.splash 状态机的
                        验证孪生）+ unittest（test_controller.py，8 用例）
bridge/                 开发层（现为可选）：IMAP/SMTP ↔ 本机 HTTP 网桥（凭据只存
                        config.json，已 gitignore；5 个解析单测）——已被平台服务
                        路线取代，不进提交包
dev/                    开发层：网桥适配器（替换 main.splash 的 MARKER:ADAPTER 块）
scripts/                drive-demo.py：经 Makepad 远程桥驱动真实 card-host 窗口
                        跑完整演示任务并截取全部证据（驱动会把真实鼠标停靠到
                        远处——OS 光标事件会吞掉合成点击）
                        drive-mail.py：驱动提交包在 card-host 中走平台 mail 服务
                        （无账号态 → 宿主登录面板 → 真实拒绝 → 取消）
                        official_sheet_run.py：同一流程在 **OctoSense 桌面 Shell**
                        内（官方面板 + 官方服务的真实 imap.qq.com 拒绝）
evidence/               运行证据
  ev-01..08.png         回复生命周期证据（草稿/确认/已发送/收件箱胶囊同步/
                        失败/保留/重试成功/Agent 审批）
  ev-09/10.png          模型不可用态（宿主原文拒绝 + 本地回退）
  ev-13..16.png         card-host 商店形态真实邮件（无账号横幅/宿主登录面板/
                        imap.qq.com 真实拒绝/取消返回）
  ev-17..19.png         OctoSense 桌面 Shell 内（应用作为 WM 客户端运行/
                        官方 Add-a-mail-account 面板/官方服务真实 IMAP 拒绝）
  ev-20.png             桌面 1200px 宽度 master-detail（响应式布局证据）
  final-snap.json       演示结束时的完整组件树
  final-log.txt         card-host 日志
  hub/                  hub 流程工件：review.json（scan 问题包）、SUBMISSION.md
                        （七问书面回答 + 复现说明 + 剩余人工步骤）
  l0-design/            早期 L0 摘要卡片形态的设计产物（image-to-card 流程，已退役）
  legacy/               重设计前的旧版截图（va/vb，仅供历史对照）
bundle/                 THE SUBMISSION（唯一提交部分；hub check PASSED）
  main.splash           响应式三视图脚本（回复生命周期状态机在邮件对象上）
  assets/icon.svg  listing.json  manifest.json  screenshots/01..04
```

## 核心演示任务（对应评分「任务完成 / 可靠运行 / 人机协作」）

从「Re: Q4 联名方案」出发：**识别**（AI 分诊横幅 + 优先级条 + 摘要卡：要点 /
建议动作 / 会议识别 / 情绪标签）→ **提议**（AI 起草可编辑草稿，明确回复对象与
语气；一键智能回复胶囊）→ **授权**（两步确认发送）→ **结果核验**（阅读页
「已回复」状态条与收件箱胶囊同步）→ **失败处理**（练习场景开关：发送失败 →
草稿保留 → 重试成功）；
**真实模型调用**（`ev-09/ev-10`：card-host 中宿主如实拒绝 `no service answers "model"`，
界面明示并回退——在 2026-09-28 后的 OctoSense 桌面 Shell 中同一按钮即产生真实模型输出）。

## 复现（Windows 10 26100，唯一实测平台）

先构建带 mail 服务的宿主（本地 hub 检出；`crates/card-host/src/host.rs`
已接好 `octosense_mail_service::register()`）：

```sh
cd ../OctoSense-App-Hub && cargo build --release -p octosense-card-host
# 产物在 %CARGO_TARGET_DIR%（D:\Users\yzbtdiy\Cache\CARGO_TARGET）
```

再以提交包运行（两种宽度分别验证响应式布局）：

```sh
python -m unittest discover -s service      # 状态机单测
set MAKEPAD_REMOTE=8146
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\card-host.exe --bundle bundle ^
    --app-data .local-state --allow-unsigned --stamp --size 412x860
python scripts/drive-demo.py 8146           # 完整生命周期 + 模型不可用态
python scripts/drive-mail.py 8146           # 商店形态邮件：面板/真实拒绝/取消
rem 桌面宽度：以 --size 1200x860 重启并点开任一邮件——
rem 收件箱变「列表+占位卡」、阅读态变 master-detail（ev-20）
../OctoSense-App-Hub/target/release/hub.exe stamp bundle
../OctoSense-App-Hub/target/release/hub.exe check bundle --allow-unsigned
```

接入自己的邮箱：运行 card-host，点「添加账号」，在**宿主面板**里输入邮箱地址
和服务商授权码（QQ/163/Gmail 自动识别服务器）。授权码只存宿主侧
（`.local-state/.host/mail/`），不经过应用，也绝不进入提交包。

### 在 OctoSense 桌面 Shell 本体中运行（最强演示路径）

一次性准备（完整说明见 `../octosense-local-hub/README.md`）：从本地 OctoSense
检出构建 Shell（`python tools/setup.py` 后
`cargo build --release -p octosense --no-default-features --features app-hub`），
把提交包发布到本地 hub，然后带环境变量启动：

```sh
set MAKEPAD_REMOTE=8147
set OCTOSENSE_HUB_ANCHOR=<../octosense-local-hub/README 中的 anchor 公钥>
set OCTOSENSE_APP_DATA=D:\Coding\Rust\agenticapp26\octosense-local-hub\device
start "" D:\Users\yzbtdiy\Cache\CARGO_TARGET\release\octosense.exe --test-action launch-hub:vibemail
python scripts/official_sheet_run.py 8147
```

Shell 经签名验证的目录准入提交包，将其作为窗口管理器客户端启动，并由
**自带的 Mail 服务**处理 `mail.*`：「添加账号」唤起官方「OctoSense · Add a
mail account」面板（地址/密码/IMAP-POP3/服务器端口），错误凭据被真实邮件
服务器拒绝（ev-19）。该 Shell 同时注册了 `model` 服务——配置过 providers 的
话，应用的 AI 按钮在此环境中走真实一次性模型调用。

## 状态

- `hub check`：`vibemail 0.5.1 — PASSED`（本地 hub 工作密钥已签名；
  目录 sequence 2，见 `../octosense-local-hub/`）。
- 真实邮件：本地 card-host 构建已注册 mail 服务，提交包即真收发（ev-13..16）；
  原版 card-host / 未登录时如实显示对应状态。
- 真实模型演示环境：从 OctoSense main（≥2026-09-28）构建桌面 Shell 并配置 AI
  providers（`PUBLISHING §4` 排练路径）；card-host 永远展示不可用态。
- 截图为 card-host 真实截取并逐张人工核验；见 `evidence/`。
- 剩余人工步骤（发布者本人）：`hub keygen` → `hub sign-manifest` →
  `hub check --publisher-key` → 打 tag 并在 OctoSense-App-Hub 开
  `Submit vibemail 0.5.1` issue（附 `evidence/hub/SUBMISSION.md`）。
