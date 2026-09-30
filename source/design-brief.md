# VibeMail 设计规范（design brief）

0.2.0 的视觉与交互基准是用户提供的深空主题网页应用源码（工作区
`UI设计/app`：React + Tailwind 的 inbox / compose / agents 三视图，手机与桌面
断点自适应）。实现为 Splash 脚本应用（`bundle/main.splash`），在 card-host 以
412×860（手机）与 1200×860（桌面）两种宽度实测。本文摘录设计系统、实现映射
与响应式规则，供后续迭代对照。（0.1.x 的暖米色四屏规范见 git 历史。）

## 视图索引

| 网页参考 | 屏幕 | 实现函数（main.splash） |
| --- | --- | --- |
| InboxList + ReadingPane | 智能收件箱 | `inbox_screen` / `triage_banner` / `mail_row` / `preview_pane` |
| ReadingPane + AISummaryPanel | 邮件阅读 + AI 摘要 | `read_screen`（master-detail）/ `ai_summary_card` / `smart_replies` / `meeting_card` / 内联 reply strip |
| ComposeView | AI 写信 | `write_screen`（居中 640 列）/ `tone_chip` / 提示词面板 |
| AgentsView | Agent 小队 | `agents_screen`（居中 720 列）/ `stat_cell` / `agent_card` / `act_row` |
| Chrome（MobileNav/TopBar） | 全局导航 | `top_bar` / `nav_tab`（字符块图标 + 徽章，Fill-Fit-Fill 居中） |

## 响应式规则（布局数学即媒体查询）

Splash 无法读取窗口宽度。经 card-host 实证的原语：**FIXED 宽度向其容器钳位**
（400 在 412 窗口 → 412；嵌套逐层钳位），**Fill 兄弟被挤压时归零**（无子元素时
安全消失）。因此：

- 每屏为 `[Fill 留白][定宽列][Fill 留白]`：窄窗钳到全幅，宽窗居中
  （收件箱 md=980，写信 640，Agent 720）。
- 收件箱 master-detail：`[列表 fixed 420][预览 Fill]`——宽窗显示「列表 +
  选择一封邮件占位卡」（网页桌面版行为），窄窗预览列归零。
- 阅读 master-detail：`[阅读栏 fixed 480][列表 Fill]`——**Fill 必须在 fixed
  之后**：在前会算出负宽度，向负宽列铸子树会静默丢弃整个渲染（本次踩坑）。
  宽窗「阅读栏左 + 高亮列表右」，窄窗列表归零、阅读栏钳满全屏（推送式）。
- 危险模式备忘：Fill 宽标签/无子 spacer 后跟 Fit 按钮会把按钮挤出树
  （AI 生成 / 草稿 pill / outage 开关三处踩坑）——按钮用固定宽或放 spacer 之前。

## 调色板（token → main.splash 变量）

| 用途 | 网页参考取值 | 变量 |
| --- | --- | --- |
| 页面底色 | #05070f | `space` |
| 卡片面板 | ≈#0b1120 / #0d1526（0.72/0.8 叠加） | `panel` / `panel2` |
| 导航玻璃 | ≈#080c19 | `glass` |
| 发丝线 | #141523 / #26263b | `line` / `line2` |
| 主文字 | #e9e6df（次级 55%/45%/38%/32%） | `ink` / `ink55` / `ink45` / `ink38` / `ink32` |
| Agent 紫 | #8642ff（文本 #xb7a8ff，面板 #x170f31） | `violet` / `violetT` / `violetBg` |
| 数据青 | #22d3ee（文本 #x67e8f9） | `cyan` / `cyanT` |
| 成功薄荷 | #34d399（文本 #x6ee7b7） | `mint` / `mintT` |
| 警示琥珀 | #xfbbf24（文本 #xfcd34d） | `amber` / `amberT` |
| 错误红 | #xf87171（文本 #xfca5a5） | `red` / `redT` |
| 优先级色阶 | ≥85 红 / ≥65 琥珀 / ≥45 青 / 其余 #x9a92d9 | `pri_color` |

预混色已按 #05070f 地面合成（运行时不做 alpha 叠加）。

## 组件语言

- **渐变头像**：`avatar(m, size)`——双色调 RoundedView + 首字（`init` 字段，
  无字符串切片）+ 未读紫点 Overlay。
- **AI 优先级条**：`priority_meter`——36×3 轨道 + 紫→优先级色渐变填充 + 等宽
  分数（数字须 `"" + n` 转字符串）。
- **标签 chip**：`chip(text, tone)`——tone 五色（violet/cyan/amber/red/mint），
  列表行最多 2 枚（宽度留给优先级条），阅读页展示全集。
- **字符块图标**：导航与 Agent 卡用「tinted 圆角方块 + 单字」（收/写/队、
  卫/管/清/报）。运行时 SVG 在本栈栅格化为空白（新旧两版均实测），因此不随包
  携带任何 SVG；唯一例外是 listing 的 `icon.svg`。
- **三态横幅**：`triage_banner`——分诊行（动态计数）+ 邮件服务状态行（live /
  未添加账号 / 不可用，含「添加账号」按钮）+ 筛选 chips。无 GestureView 包装
  （横幅整卡手势会吞掉下方列表行的命中区——实测踩坑）。
- **回复状态条**：五态（pending/confirm/sending/sent/failed）内联在阅读栏，
  两步确认发送，失败保留草稿可重试；列表行以 `state_pill` 同步显示。

## 与网页参考的取舍

- 阅读栏在桌面位于列表**左侧**（网页为右侧）：Fill-after-fixed 是唯一安全的
  双栏序（见上），镜像布局是语言约束下的等价实现。
- 无侧边 Rail：Rail 需要「宽屏才出现」的条件渲染，宽度不可读时无法实现；
  底部玻璃导航在两端一致并以 Fill-Fit-Fill 居中。
- 自动化程度表以纯 View 绘制（58% 手柄），无拖拽。
- 练习数据口径披露随 Agent 视图滚动展示。

## 练习数据（与网页参考一致的人物）

林晓薇（Northstar 合同，紧急）、VibeMail 产品团队（周报）、陈立群（招聘委员会）、
Stripe（发票）、GitHub（代码评审）、妈妈（中秋）、AWS Summit（营销）、
沈括（数据平台）。全部为虚构练习数据；Agent 小队（跟进卫士/日程管家/订阅清理/
周报生成）与活动流同为练习数据。
