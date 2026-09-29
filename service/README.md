# Service layer

`controller.py` 是 `bundle/main.splash` 中回复生命周期状态机
（`attach_draft / ask_send / cancel_send / do_send / finish_send / retry_send /
keep_draft / edit_draft`）的验证孪生：Splash 运行时自身没有单测框架，
转换规则以纯 Python 落在这里，由同目录的 `test_controller.py`（unittest）覆盖；
`scripts/drive-demo.py` 再把同一条路线跑到真实 card-host 窗口上留证。
三处必须同步演进：UI 新增转换时，此处与测试同步补充。

对应 examples/aircon 的 `service/controller.py` 模式（initial_state / reduce /
view_model / demo_route）；发送为本地模拟（练习数据），不触达任何真实服务。

```sh
python -m unittest discover -s service   # 8 个用例
```
