# 卡应用验收管线:Splash 应用的测试、审计与演示视频

VibeMail 在开发中沉淀出一套**与具体应用无关**的验收管线。OctoScript/Splash
运行时没有单元测试框架,宿主桥接(MAKEPAD_REMOTE)有一组不写进文档的怪癖;
这套管线把「验证一个卡应用」变成几条可重复的命令。任何 Splash 卡应用都可以
直接套用——工具在 `scripts/`,坑位目录在本文第四节。

## 总览

| 工具 | 一句话 | 命令 |
| --- | --- | --- |
| `scripts/run_routes.py` | 声明式点击路线:JSON 写「要发生什么」,脚本管「怎么点」 | `python scripts/run_routes.py <port>` |
| `scripts/audit_overflow.py` | 右缘溢出审计:412/700/1200 三宽度,逐屏找越界控件 | `python scripts/audit_overflow.py 412 700 1200` |
| `scripts/audit_missing.py` | 内容缺失审计:被挤压的控件直接从树上消失,溢出审计看不见 | `python scripts/audit_missing.py 412 700 1200` |
| `scripts/record-demo.py` | 桥接抓帧录演示视频:连续 `/g` 抓帧 + 驱动演示弧线 + ffmpeg 合成 | `python scripts/record-demo.py <port>` |
| `scripts/narrate-demo.py` | 中文解说与字幕:edge-tts 逐段配音,按段时间戳对齐混音烧录 | `python scripts/narrate-demo.py` |
| `service/`(可选模式) | 状态机孪生:Splash 没法单测,用 Python 镜像状态机跑单测 | `python -m unittest discover -s service` |

配套姿势:应用先跑在 card-host(`run.cmd mobile`,远程桥默认 8146)。

## 1. 声明式路线 run_routes.py

`route_test.json` 只描述意图——点按目标、期望出现的文本、必须消失的文本:

```json
{ "tap": "专注", "exact": true,
  "expect": "已按 vibe 筛选:专注", "absent": ["周末去海边"] }
```

脚本负责一切脏活:目标滚出视口就先滚回来、点击被桥接丢弃就按效果重试、
失败自动落证(`evidence/routes/<路线>/<步骤>/{fail.png,snap.json,log.txt}`)。
全套通过才退出 0——它是发布前的门禁,也是演示可行性的证明。

## 2./3. 溢出与缺失审计(为什么需要两个)

这个运行时里被水平挤压的控件**整个从控件树消失**(矩形从不越界),所以:

- `audit_overflow.py` 找「矩形越过窗口右缘」的控件;
- `audit_missing.py` 拿一张「每屏每宽度应当可见的文本表」做存在性检查,
  逐屏小步滚动采集。

两个审计都在**每屏一个全新实例**上跑(见坑位第 5 条)。期望表与应用文案
强绑定,换文案时同步更新表。

## 4./5. 演示视频:record-demo.py + narrate-demo.py

不用任何屏幕录制软件,直接从宿主桥拿帧:

1. 抓帧线程连续 `/g?raw=1`,记录每帧的真实时间戳;驱动线程按演示弧线点按
   (与路线同一套 tap/search 助手);
2. 弧线里每个段落打 `mark()`(段落名 → 距开拍秒数),落盘 `rec_marks.json`;
3. ffmpeg 以**逐帧真实时长**合成(concat demuxer + 每帧 duration)——抓帧速率
   不匀,恒定帧率会把等待拉长、把转场压缩,音画必然错位;
4. `narrate-demo.py` 按段落窗口生成 edge-tts 中文配音,`adelay` 对齐到段落
   开始 + 点按落地补偿(约 +2.6s),drawtext 烧同文字幕。

改文案只改 `LINES` 表重跑;改弧线只改 `arc()`。产物示例见 GitHub Release
v0.8.2 的 `demo-v0.8.0-narr.mp4`。

## 运行时坑位目录(都是踩出来的)

1. **`/g` 抓帧后紧跟的点击会被丢弃。** 状态改变型点按一律「点按 → 断言效果
   → 落空重试」;录像时抓帧与点按要互斥并留 0.4s 空档。
2. **点按穿透:** 一次点按到达每一个重叠的 GestureView。底部导航因此必须在
   布局流内(in-flow),不能浮在卡片上;应用侧再加一道「导航闸」时间戳,
   穿透到详情页「回复」的导航点按曾把写信静默绑错线程。
3. **宿主回复的回调里嵌套请求不会被泵送。** 所有宿主请求从 poller 队列
   (interval)或手势发出;「保存草稿 → 核验回执」这类两步链路第二步必须走
   队列。
4. **可选键用方括号访问**(`r.data.output["event"]`);点访问缺键直接抛错,
   杀掉整个回调。运行时没有 string 方法(仅 `.search`)、没有 object.keys。
5. **长生命周期审计实例不可信:** 深度滚动积累的惯性会让后续点按滑到邻卡;
   每屏起一个全新实例最稳。
6. **`hub stamp` 的 digest 不含 manifest.json 本身**(它装着 digest);但除
   `integrity` 外的清单改动仍要重新 stamp 才过 check——门禁按效果校验,不靠
   推理。

## 复用清单

1. 把 `scripts/*.py` 拷进你的仓库(纯标准库,Python 3.9+);
2. 为你的屏写一份 `route_test.json` 和审计期望表;
3. `run.cmd`(或等价物)包一层 card-host 启停;
4. 发布前:单测 → 路线 → 双审计 → `hub stamp && hub check` → 录视频。

VibeMail 的 10 条路线 59 步、三宽度审计、26 个状态机单测与发布证据全部开源
在仓库里,可直接当参照系。
