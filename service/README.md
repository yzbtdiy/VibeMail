# Service layer

`controller.py` 是 `bundle/main.splash` 中回复生命周期状态机
（`attach_draft / do_send / finish_send / finish_review / retry_send /
keep_draft / set_outage`）的验证孪生：Splash 运行时自身没有单测框架，
转换规则以纯 Python 落在这里，由同目录的 `test_controller.py`（unittest）覆盖；
`scripts/drive-demo.py` 再把同一条路线跑到真实 card-host 窗口上留证。
三处必须同步演进：UI 新增转换时，此处与测试同步补充。

对应 examples/aircon 的 `service/controller.py` 模式（initial_state / reduce /
view_model / demo_route）；练习发送为本地模拟，不触达任何真实服务。
live 发送走宿主前台审阅通道 `mail.review_send`（0.7.28 起；`mail.send`
自 10-04 起只回 approval_required）——`finish_review` 按宿主回包分类为
sent / failed / cancelled（取消审阅未发送，草稿保留、邮件不打失败标记），
与 `send_live` 的回调分支一一对应。

```sh
python -m unittest discover -s service   # 13 个用例
```
