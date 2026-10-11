# Issue #84 更新评论草稿(v0.8.0)

> 用途:0.8.0 的 tag 推送、工作流跑通后,作为评论发到
> https://github.com/OctoSense-org/OctoSense-App-Hub/issues/84 ,
> 并把 issue 标题改为 `Submit vibemail 0.8.0`、正文 Version 字段改为 0.8.0。
> 按 SUBMITTING.zh-CN.md:首次发布前的所有更新都发在这一个 issue 里,
> 评论需写明 tag、完整 commit SHA、工作流运行链接。
> 推送后把 <COMMIT_SHA> 与 <WORKFLOW_RUN_URL> 替换为真实值再发。

---

Update: v0.8.0 — 评审意见全部落地 + 可核验执行升级

- Tag: `v0.8.0`(附注标签,跟随本条评论前推送)
- Commit: `<COMMIT_SHA>`
- Workflow run: <WORKFLOW_RUN_URL>(publish-app.yml:publisher-prepare → Sigstore 证明 → publisher-verify / pack)
- Gate: `hub check bundle --allow-unsigned` → vibemail 0.8.0 PASSED(capabilities {files, glance, mail, model, storage},agent read-only;unsigned 警告为 GitHub 来源证明路径的固有项)

## 对 10-09 评审意见的逐条回应

1. **发送通道迁移(已落地,0.7.28 起)**:单击发送改走 `mail.review_send` —— 宿主前台弹出审阅单,亲手批准才发出;等待期显示「宿主审阅中…」;取消审阅如实标注「已取消审阅 · 未发送」、草稿保留可重发(`bundle/main.splash` `send_live()`)。Windows 限定:参考邮件服务的物理批准仅 macOS/Android,故 0.8.0 在 Windows 上提供同语义的可核验执行闭环 —— 「存为草稿」走 `mail.compose` 保存宿主侧草稿,只有 `mail.compose_status` 回执到达才点亮「宿主核验」标识;更新同一草稿带 `expected_revision` 乐观锁。该闭环在 card-host 上以声明式路线端到端跑通。
2. **digest 不符(已修复,流程层面)**:根因是早期手工 stamp 后又改动字节。现已改为 GitHub 发布工作流对 tag 对应 commit 原样字节完成 stamp/证明/打包,本地不再手工盖章后改字节;`hub publisher-verify` 对 0.7.29 已 PASSED(sealed digest 与可编辑源一致),0.8.0 沿用同一流程。本次改动内容即本评论与 Release notes。
3. **练习模式语气滑杆标注(已落地,0.7.28 起)**:练习数据下语气滑杆的固定文案标注「练习文案」,与「练习摘要」口径对齐(写信屏预览区与滑杆标题行均有标注)。

## 0.8.0 其他升级(均带来源标注与失败态)

- 「识别到安排」日程提议卡:摘要的同一次 `model.complete` 顺带 schema 校验提取(标题/日期/时间/地点范围校验不过则整卡不渲染),卡内 ±1h 修正,`files.export` 导出 .ics;宿主无文件适配时按钮置灰并说明。
- 星轨新增 漂移/时间轴/周报 三段:周报为纯本地统计 + 一次缓存模型短语,可导出文本。
- 批量 vibe 清扫:筛选激活时浮出清扫条,确认卡 → 归档 → 5 秒撤销。
- 桌面速览卡:`glance.publish` 以 template + initial 发布(不含 script),带 `card_id` / `title`。
- 只读 App Agent:`tools.json` + `AGENT.md`,仅两个 read 级宿主工具(草稿台账、速览卡列表),隐私政策已披露。
- 布局修复:时间轴时间列右内边距(右贴文字在视图边缘被裁)、详情页底距、周报条宽归一。

## 验证(Windows 10 26100,card-host 412/700/1200)

- `python -m unittest discover -s service` → 25/25 OK(状态机孪生:草稿闭环、清扫撤销、日程校验均在列)
- `python scripts/run_routes.py <port>` → 10/10 路线 59 步(新增日程卡、三段切换、练习草稿、清扫撤销四条路线)
- `python scripts/audit_overflow.py 412 700 1200` / `audit_missing.py` → 三宽全 clean / complete
- 截图与证据随 commit 更新(`bundle/screenshots/`、`evidence/`);未验证项见仓库 `validation.json` 的 `not_verified` 一节(如实列出 Windows 上未能端到端驱动的宿主链路)
