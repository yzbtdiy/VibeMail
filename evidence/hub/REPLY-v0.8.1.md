# Issue #84 更新评论草稿(v0.8.1)

> 用途:v0.8.1 工作流跑通后,作为评论发到
> https://github.com/OctoSense-org/OctoSense-App-Hub/issues/84 ,
> 并把 issue 标题改为 `Submit vibemail 0.8.1`、正文 Version 字段改为 0.8.1。
> 按 SUBMITTING.zh-CN.md:首次发布前的所有更新都发在这一个 issue 里,
> 评论需写明 tag、完整 commit SHA、工作流运行链接。
> 本文件 commit SHA 在评论前已是真实值;只需确认工作流运行链接指向成功的那次 run。

---

Update: v0.8.1 — 评审意见全部落地 + 可核验执行升级

- Tag: `v0.8.1`(附注标签)
- Commit: 见本仓库 main 顶端(评论发出时以 `git rev-parse v0.8.1^{commit}` 为准)
- Workflow run: https://github.com/yzbtdiy/VibeMail/actions (publish-app.yml,取 v0.8.1 的成功 run)
- Gate: `hub check bundle --allow-unsigned` → vibemail 0.8.1 PASSED(capabilities {files, glance, mail, model, storage},agent read-only;unsigned 警告为 GitHub 来源证明路径的固有项)

> 版本说明:v0.8.0 的 run
> [38141686860](https://github.com/yzbtdiy/VibeMail/actions/runs/38141686860)
> 被 publisher-verify 拒收——工作流钉住的 App-Hub 工具(655114c4,10-07)早于
> `mail.compose_status` 的受审工具契约与 `files` 能力的引入;按「不移动已推送
> tag,修正走新版本」的规则,0.8.1 将工具钉升至 8d3853c 并包含一处发送态修正
> (无审阅适配器的平台上不再提供永远失败的重试)。v0.8.0 的 tag 保留原样。

## 对 10-09 评审意见的逐条回应

1. **发送通道迁移(已落地,0.7.28 起)**:单击发送改走 `mail.review_send` —— 宿主前台弹出审阅单,亲手批准才发出;等待期显示「宿主审阅中…」;取消审阅如实标注「已取消审阅 · 未发送」、草稿保留可重发(`bundle/main.splash` `send_live()`)。Windows 限定:参考邮件服务的物理批准仅 macOS/Android,故 0.8.x 在 Windows 上提供同语义的可核验执行闭环 —— 「存为草稿」走 `mail.compose` 保存宿主侧草稿,只有 `mail.compose_status` 回执到达才点亮「宿主核验」标识;更新同一草稿带 `expected_revision` 乐观锁。该闭环在 card-host 上以声明式路线端到端跑通。0.8.1 补充:在宿主编译期就不含审阅适配器的平台(Windows/Linux,`public_review.rs` 的 cfg 门槛),发送落入终态「本平台不可发送」,不再提供永远失败的重试,回复卡不留失败标记。
2. **digest 不符(已修复,流程层面)**:根因是早期手工 stamp 后又改动字节。现已改为 GitHub 发布工作流对 tag 对应 commit 原样字节完成 stamp/证明/打包,本地不再手工盖章后改字节;`hub publisher-verify` 对 v0.7.29 已 PASSED(sealed digest 与可编辑源一致),0.8.x 沿用同一流程。本次改动内容即本评论与 Release notes。
3. **练习模式语气滑杆标注(已落地,0.7.28 起)**:练习数据下语气滑杆的固定文案标注「练习文案」,与「练习摘要」口径对齐(写信屏预览区与滑杆标题行均有标注)。

## 0.8.x 其他升级(均带来源标注与失败态)

- 「识别到安排」日程提议卡:摘要的同一次 `model.complete` 顺带 schema 校验提取(标题/日期/时间/地点范围校验不过则整卡不渲染),卡内 ±1h 修正,`files.export` 导出 .ics;宿主无文件适配时按钮置灰并说明。
- 星轨新增 漂移/时间轴/周报 三段:周报为纯本地统计 + 一次缓存模型短语,可导出文本。
- 批量 vibe 清扫:筛选激活时浮出清扫条,确认卡 → 归档 → 5 秒撤销。
- 桌面速览卡:`glance.publish` 以 template + initial 发布(不含 script),带 `card_id` / `title`。
- 只读 App Agent:`tools.json` + `AGENT.md`,仅两个 read 级宿主工具(草稿台账、速览卡列表),隐私政策已披露。
- 布局修复:时间轴时间列右内边距(右贴文字在视图边缘被裁)、详情页底距、周报条宽归一。

## 验证(Windows 10 26100,card-host 412/700/1200)

- `python -m unittest discover -s service` → 26/26 OK(状态机孪生:草稿闭环、清扫撤销、日程校验、发送终态均在列)
- `python scripts/run_routes.py <port>` → 10/10 路线 59 步(新增日程卡、三段切换、练习草稿、清扫撤销四条路线)
- `python scripts/audit_overflow.py 412 700 1200` / `audit_missing.py` → 三宽全 clean / complete
- 截图与证据随 commit 更新(`bundle/screenshots/`、`evidence/`);未验证项见仓库 `validation.json` 的 `not_verified` 一节(如实列出 Windows 上未能端到端驱动的宿主链路)
