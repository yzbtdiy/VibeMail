# Agentic Mail（agentic-mail）

[English](README.md) | 简体中文

参赛「Agentic App 黑客松 2026」（场景 01 邮件）的概念应用。五个屏幕——智能收件箱、
邮件阅读（AI 摘要）、AI 写信起草、跟进待办、我的——按 `source/` 四张参考设计图
实现为 Splash 脚本应用（`bundle/main.splash`），在 App Hub 的 `card-host` 中实跑、
真实交互、真实截屏。目录结构参照
[OctoScript-App-Design-Flow/examples](../OctoScript-App-Design-Flow/examples/README.zh-CN.md)
的约定（source / artwork / service / scripts / evidence）。

**能力与数据口径**：应用申请 `model` 与 `mail` 两项权限。
`mail`：真实收发走平台 mail 宿主服务（账号由宿主登录面板添加、凭据存系统密钥库，
不经过应用）；无该服务的环境（card-host）如实显示不可用并回退练习数据。
`model`：AI 摘要与起草通过一次性模型服务（schema 校验、日预算）调用设备配置的
模型，密钥不经过应用；不可用回退本地模板并标注。待办为练习数据（no-facts 原则）。

## 目录结构

```text
source/                 设计源：4 张参考设计图（design-01..04.png）+ design-brief.md
                        （调色板、逐屏要点、素材映射、与设计图的已知偏差）
artwork/                素材工作副本（SVG 头像/图标）；随包副本在 bundle/assets/
service/                回复生命周期 reducer（controller.py，main.splash 状态机的
                        验证孪生）+ unittest（test_controller.py，8 用例）
bridge/                 开发层：IMAP/SMTP ↔ 本机 HTTP 网桥（凭据只存 config.json，
                        已 gitignore；5 个解析单测）——不进提交包
dev/                    开发层：网桥适配器（替换 main.splash 的 MARKER:ADAPTER 块）
scripts/                drive-demo.py：经 Makepad 远程桥驱动真实 card-host 窗口
                        跑完整演示任务并截取全部证据
evidence/               运行证据
  ev-01..08.png         回复生命周期证据（草稿/确认/已发送/收件箱胶囊同步/
                        失败/保留/重试成功/待办分段 tab）
  final-snap.json       演示结束时的完整组件树
  final-log.txt         card-host 日志
  hub/                  hub 流程工件：review.json（scan 问题包）、SUBMISSION.md
                        （七问书面回答 + 复现说明 + 剩余人工步骤）
  l0-design/            早期 L0 摘要卡片形态的设计产物（image-to-card 流程，已退役）
  legacy/               重设计前的旧版截图（va/vb，仅供历史对照）
bundle/                 THE SUBMISSION（唯一提交部分；hub check PASSED，待签名）
  main.splash           五屏脚本应用（回复生命周期状态机在邮件对象上）
  assets/  listing.json  manifest.json  screenshots/01..05
```

## 核心演示任务（对应评分「任务完成 / 可靠运行 / 人机协作」）

从「【紧急】产品发布会流程确认」出发：**识别**（AI 分诊 + AI 摘要 + 附件）→
**提议**（AI 起草可编辑草稿，明确回复对象与语气；快速回复胶囊）→ **授权**
（两步确认发送）→ **结果核验**（阅读页「已回复」状态条与收件箱胶囊同步）→
**失败处理**（练习场景开关：发送失败 → 草稿保留 → 重试成功）；
**真实模型调用**（`ev-09/ev-10`：card-host 中宿主如实拒绝 `no service answers "model"`，
界面明示并回退——在 2026-09-28 后的 OctoSense 桌面 Shell 中同一按钮即产生真实模型输出）。

## 复现（Windows 10 26100，唯一实测平台）

```sh
python -m unittest discover -s service      # 状态机单测
../OctoSense-App-Hub/target/release/card-host.exe --bundle bundle \
    --app-data .local-state --allow-unsigned --stamp &   # 可见窗口；
# MAKEPAD_REMOTE=<port> 可开远程桥；无头加 MAKEPAD_HIDE_WINDOWS=1
python scripts/drive-demo.py <port>         # 驱动完整任务并刷新全部证据
../OctoSense-App-Hub/target/release/hub.exe check bundle --allow-unsigned
```

## 状态

- `hub check`：`agentic-mail 0.1.0 — PASSED`（仅未签名警告；grants 含 `mail`,`model`）。
- 真实模型演示环境：从 OctoSense main（≥2026-09-28）构建桌面 Shell 并配置 AI providers
  （`PUBLISHING §4` 排练路径）；card-host 永远展示不可用态。
- 截图为 card-host 真实截取并逐张人工核验；见 `evidence/`。
- 剩余人工步骤（发布者本人）：`hub keygen` → `hub sign-manifest` →
  `hub check --publisher-key` → 打 tag 并在 OctoSense-App-Hub 开
  `Submit agentic-mail 0.1.0` issue（附 `evidence/hub/SUBMISSION.md`）。
