# VibeMail(vibemail)

「Agentic App 黑客松 2026」场景 01(邮件)参赛应用。**有情绪的邮件。** 0.7.0 起
VibeMail 按 OctoSense 设计原型参考完全重构为一部 412px 手机列应用(宽窗口居中、
两侧氛围光晕):五种 vibe(珊瑚橙专注 / 霓虹黄愉悦 / 薄荷绿平静 / 粉色灵感 / 蓝色
连接)为每封邮件披上情绪光环,星轨收件箱把邮件化作漂浮气泡,写信的语气滑杆让同一
封回信在真诚与正式之间实时改写;真实收发经平台 mail 宿主服务完成,AI 摘要与改写
经宿主 model 服务完成——凭据与密钥始终留在宿主侧,不经过应用、不进提交包。

| | |
| --- | --- |
| 应用 ID / 版本 | `vibemail` / **0.7.2** |
| 门禁状态 | `hub check --publisher-key` — **PASSED,零警告**(发行者已签名) |
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
  连接),卡片左上角同色情绪光环、未读点、星标、重要度;vibe 过滤 chips 为真实
  筛选(激活时摘要卡显示筛选指示);问候按实际时间变化(早上好/中午好/下午好/晚上好)、
  「你有 N 封未读邮件」(N=未读)与
  AI 心情播报行(各 vibe 实时计数)随数据变化
- **星轨收件箱**:邮件化作漂浮气泡——大小=重要度、颜色=vibe、同色柔光晕,随
  sin/cos 缓慢漂移(0.15s 步进),点按气泡直接打开邮件;空收件箱显示「这片海域
  一片平静」
- **邮件详情**:白卡右上情绪光环、vibe 标签、**AI 三行摘要**卡(✦ 形彩色要点,
  来源如实标注:练习摘要 / 模型生成 / 生成中 / 服务不可用 / 正文截取)、完整正文,
  星标 / 归档 / 回复(霓虹黄)三键;归档可在设置中一键恢复
- **写信与语气滑杆**:收件人 / 主题预填,**语气滑杆**(真诚随意 ↔ 自然友好 ↔
  正式得体)实时改写回信预览——练习数据内置每封邮件三种语气文案(Mira 线程与
  参考原型逐字一致),live 邮件走 `model.complete` 实时改写,不可用时保留原文并
  如实标注;**单击发送**(发送中… → 已随波寄出 / 失败保留草稿可重试)
- **「我的」设置屏**:外观主题(亮/暗快切胶囊 + 跟随系统 / 亮色 / 暗色三态,
  持久化并跟随 Shell 亮暗)、OctoSense 能力声明卡(mail / storage / model 与
  「刻意不声明」注记)、邮箱账号(添加账号走宿主 sheet / 刷新 / 两步断开 /
  归档恢复)、练习开关(模拟发送失败)
- **真实邮件**:经平台 mail 宿主服务走真实 IMAP/SMTP;账号在**宿主自己的登录
  面板**添加,授权码只存宿主保险库;live 邮件由关键词规则标注 vibe(重要度按
  vibe 档位),AI 摘要按需生成;无账号环境如实显示并回退已标注的练习数据
- **真实模型调用**:AI 三行摘要与语气改写为一次性 `model.complete` 调用(schema
  校验);界面显示宿主**实际使用的模型名**(`meta.model`)
- **双主题·三态**:暖纸米色 #eaeae3 亮 × 炭黑 #151413 暗,vibe 五色跨主题不变;
  可跟随 OctoSense 系统亮暗(Shell 切换 ~2 秒内跟随)或手动固定,选择持久化

## 能力声明

应用只申请实现功能所需的三项能力(未申请即未授予):

| 能力 | 支撑的功能 | 不可用时的行为 |
| --- | --- | --- |
| `mail` | 收件箱 / 阅读 / 发送全流程(`mail.accounts`、`mail.add_account`、`mail.sync`、`mail.list`、`mail.message`、`mail.mark_read`、`mail.send`、`mail.remove_account`) | 摘要卡如实显示服务状态,回退已标注的练习数据 |
| `model` | AI 三行摘要与语气滑杆实时改写 | 界面如实标注「服务不可用」,摘要回退正文截取或练习摘要,改写保留原文 |
| `storage` | 主题偏好(theme.json,4 MiB 上限内) | card-host 恒有存储沙箱,该声明供商店隐私摘要使用 |

无网络主机声明(`hosts {}`)——刻意不声明 `net` / `web` / `camera` / `location`。

## 目录结构

```text
route_test.json 声明式路线测试:6 条点击路线(vibe 筛选与详情 / 星轨与三态主题 /
               语气滑杆三档改写 / 单击发送 / 故障-保留-重试 / 归档与恢复)
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
scripts/       run_app.py:run.cmd 的内核(启动前自动生成去签名运行副本
               build/run-bundle——card-host 的 --allow-unsigned 拒绝带
               签名 manifest,提交包保持签名)
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
bundle/        THE SUBMISSION —— 唯一提交部分
  manifest.json    id、版本、能力、完整性哈希(hub stamp 写入)、发行者签名
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
  检出(`crates/card-host/src/host.rs` 已接好 `octosense_mail_service::register()`)
- 桌面 Shell 演示另需:本地 [OctoSense](https://github.com/OctoSense-org/OctoSense)
  检出与本地签名 hub 目录(`../octosense-local-hub/`,见其 README)

## 快速开始

`run.cmd` 是一键入口(内核为 `scripts/run_app.py`):

| 命令 | 作用 |
| --- | --- |
| `run.cmd` | 以桌面宽度(1200×860)在 card-host 中启动应用(手机列居中) |
| `run.cmd mobile` | 以手机宽度(412×860)启动——本设计的原生尺寸 |
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
../OctoSense-App-Hub/target/release/hub.exe stamp bundle
../OctoSense-App-Hub/target/release/hub.exe check bundle --publisher-key yzbtdiy=<公钥>
```

接入自己的邮箱:运行应用,「我的 → 邮箱账号 → 添加账号」,在**宿主面板**里输入
邮箱地址和服务商授权码(QQ / 163 / Gmail 自动识别服务器)。授权码只存宿主侧,
不经过应用,也绝不进入提交包。已连接后「我的 → 刷新」拉取新邮件(宿主服务只列
INBOX 最新 20 封);live 邮件按关键词规则标注 vibe,AI 三行摘要打开时按需生成。

核心演示任务(对应评分「任务完成 / 可靠运行 / 人机协作」):**识别**(AI 心情
播报 + vibe 光环 + 星轨气泡)→ **阅读**(AI 三行摘要先于正文)→ **提议**(语气
滑杆三档实时改写,明确收件人)→ **授权与结果核验**(单击发送 →「已随波寄出」,
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
`model` 服务——配置过 providers 的话,AI 三行摘要与语气改写在其中走真实一次性
模型调用。三态主题跟随 Shell 亮暗(0.6.15 起的方向语义,实测双向 ~1-2 秒跟随)。

## 运行证据

`evidence/` 下全部为真实运行截取 / 记录(0.7.0 界面):

| 证据 | 内容 |
| --- | --- |
| `ev-01..07.png` | 启动收件箱(暖纸亮色)/ vibe 筛选激活指示 / Mira 详情 AI 三行摘要 / 语气滑杆真诚档 / 正式档 / 单击发送已随波寄出 / 收件箱「已回复」胶囊 |
| `ev-08/09.png` | 练习开关模拟发送失败(失败重试按钮)/ 关闭开关后重发成功 |
| `ev-10.png` | 炭黑暗色主题(设置屏切换) |
| `ev-13..16.png` | 商店形态邮件流程:未添加账号态 / 宿主登录面板 / 错误凭据真实拒绝 / 取消回未添加态 |
| `ev-mail-log.txt` | card-host 邮件流程服务侧留痕(含服务器原文拒绝) |
| `hub/` | 评审包:`review.json`(hub scan 问题包)+ `SUBMISSION.md`(七问书面回答,待按 0.7.0 更新) |

练习数据边界(按黑客松 FAQ):八封练习邮件(Mira 海边小屋 / 云服务账单 / Aurora
周报 / GitHub / 读书会 / 外婆桂花 / 设计双周报 / HR 黑客松)与发送失败模拟为本地
练习数据;邮件路径是**真实的**(平台 mail 宿主服务,凭据在宿主面板收集、宿主侧
保存);模型调用是**真实的宿主请求**(一次性、schema 校验)。

## 状态与剩余人工步骤

- **发行者签名已完成,门禁零警告**:

  ```sh
  hub keygen <仓库外路径>/publisher-yzbtdiy.key     # 私钥保存在仓库之外
  hub stamp bundle
  hub sign-manifest bundle --key <该密钥> --key-id yzbtdiy
  hub check bundle --publisher-key yzbtdiy=1095438c3939742da32f74fbcc724ae452b3f1e22e4ebe9cd834c24b2b2b5759
  # → vibemail 0.7.0 — PASSED(无任何警告)
  ```

- 本地演示 hub:`../octosense-local-hub/` 仍收录 0.6.16(sequence 32),
  `run.cmd shell` 运行该版本;0.7.0 发布后需按本地 hub 规则重新发布收录
- 机器可读的状态清单(已验证项 / 未验证边界)见 [validation.json](validation.json)
- 剩余人工步骤(发布者本人):
  1. 打 tag(`v0.7.0`)并在
     [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues)
     开 `Submit vibemail 0.7.0` issue(附 `evidence/hub/SUBMISSION.md`,按 0.7.0
     更新后提交)

## 隐私

见 [PRIVACY.md](PRIVACY.md);商店 listing 中的隐私政策 URL 指向本仓库同一文件。

## 近期版本

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
  expect 由「海面有」改「未读邮件」
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
