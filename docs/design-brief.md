# VibeMail 设计规范(design brief)

0.6.0 的视觉与交互基准是最新的暖纸网页参照(工作区 `UI设计-新/app`:React +
Tailwind 的 Sidebar / Chrome / InboxList / ReadingPane / ComposeView /
AgentsView / bits,亮暗双主题设计图见 `UI设计-新/vibemail-shots/`)。实现为
Splash 脚本应用(`bundle/main.splash`),在 card-host 以 1000 / 1200 / 1440 三档
宽度审计。本文摘录设计系统、实现映射与布局数学,供后续迭代对照。(0.2.x 深空主题
与 0.5.x 森林墨绿三栏规范见 git 历史。)

## 视图索引

| 网页参考 | 屏幕 | 实现函数(main.splash) |
| --- | --- | --- |
| Sidebar | 264px 全功能侧栏 | `sidebar` / `nav_row` / `folder_row` / `cluster_row` / `foot_icon_btn` |
| Chrome(TopBar) | 顶栏 | `top_bar` / `agent_pill` / `theme_toggle` / `bell_icon` |
| InboxList + ReadingPane | 智能收件箱 | `inbox_screen`(420 列表 + 阅读 Fill)/ 分诊横幅 / `mail_row` / `preview_pane` |
| ReadingPane 内联 AI 速览 | 阅读栏 | `reading_pane` / `ai_brief`(可折叠)/ `reply_strip` / `reply_row`(智能回复) |
| ComposeView | AI 写信 | `write_screen`(居中 720 卡片 + 340 栏)/ `tone_chip` / `prompt_chip` / `ctx_row` |
| AgentsView | Agent 小队 | `agents_screen` / `stat_cell` / `agent_card` / `act_row`(自动化程度表内联) |

## 布局数学(宽度即媒体查询)

Splash 无法读取窗口宽度。经 card-host 实证的原语:**FIXED 宽度向其容器钳位**
(嵌套逐层钳位),**Fill 兄弟被挤压时归零**(无子元素时安全消失)。因此:

- 侧栏 fixed 264、列表 fixed 420、阅读栏 Fill:1000 宽时阅读栏约 314,内容以
  `[Fill 留白][定宽 720][Fill 留白]` 居中(720 钳到栏宽,留白归零)——写信卡与
  Agent 内容列同法(1180)。
- 写信页右侧 AI 栏 fixed 340;Agent 页活动流 fixed 340,左列 Fill。
- Fill 必须在 fixed 之后:在前会算出负宽度,向负宽列铸子树会静默丢弃整个渲染。
- 危险模式备忘:Fill 宽标签/无子 spacer 后跟 Fit 按钮会把按钮挤出树——按钮用
  固定宽,或把「留白 + 尾部元素」换成 Fit 徽章 + Fill spacer 的稳妥序。

## 调色板(token → main.splash 变量)

名称沿用文件历史(violet:=森林绿强调、cyan:=teal、mint:=ok 绿),值取自参照
`index.css` 的 `:root`(亮)/`[data-theme="dark"]`(暗),透明度按各自底色预混。

| 用途 | 亮色 | 暗色 | 变量 |
| --- | --- | --- | --- |
| 页面底 | #f3f1e6 | #161c1a | `space` |
| 面板/侧栏 | #faf8ef | #1d2622 | `panel` |
| 顶栏玻璃 | #xf7f5ec | #x1a211e | `glass` |
| 发丝线 | #xdeddd2 / #xc0c1b8 | #x292e2c / #x454945 | `line` / `line2` |
| 主文字 | #x1f2926(次级 66/55/45/38%) | #xebe9de | `ink` / `ink66`… |
| 强调(森林绿) | #x2f5d43 | #x8fcb9b | `violet`(`accB` 为悬停/按下次色) |
| teal 数据色 | #x0f5a52 | #x5ec4b6 | `cyan` |
| ok / 琥珀 / 红 | #x2f7d4f / #xb06f1f / #xbe4b38 | #x7fcf96 / #xe0a458 / #xe0785f | `mint` / `amber` / `red` |
| CTA 上的 kbd 芯 | #x547a65(白 18% 叠加强调色) | #xa3d5ad | `accKbd` |
| 优先级色阶 | ≥85 红 / ≥65 琥珀 / ≥45 teal / 其余次级墨 | 同左 | `pri_color` |

**默认亮色**(`themeLight = true`);`apply_theme` 重绑全部 `let`,`repaint()` 重铸
侧栏/顶栏/正文三根。

## 组件语言

- **纯色头像**:`avatar(i, size, unread)`——数据集按发件人携带 `av1`/`av2` 双色对,
  取 `av1` 为圆底 + 首字 + 未读点(space 描边圈)。运行时 `draw_bg` 不支持 `g1`/`g2`
  渐变字段(静默忽略、背景透明,实测),一切强调底色一律纯色 `color:`。
- **AI 优先级条**:`priority_meter`——26×3 轨道 + 分数着色填充 + 等宽分数。
- **标签 chip**:`chip(text, tone)`——tone 五色(violet/cyan/amber/red/mint),
  列表行最多 2 枚,阅读栏展示全集。
- **字符图标**:运行时 SVG 栅格化为空白(新旧两版均实测),lucide 图标以单 CJK
  字 / 实证 dingbat 替代(✉ 队 ★ ◑ → ✎ ▤ ✕ ✦ ✓ ↻);日历 / 滑杆 / 太阳 /
  月牙 / 铃铛由 RoundedView 原生拼绘(`calendar_icon` / `sliders_icon` /
  `sun_icon` / `moon_icon` / `bell_icon`)。
- **AI 速览卡**:`ai_brief(i)`——阅读栏内联可折叠卡(头行 ✦ AI 速览 · BRIEF +
  状态词 + 「AI 生成」按钮 + ▼/▲;正文摘要要点圆点 / 待办提取复选 / 语气
  chip / 生成来源行),模型名在 `meta.model` 有值时追加显示。
- **回复状态条**:五态(pending/confirm/sending/sent/failed)内联在阅读栏,
  两步确认发送,失败保留草稿可重试;列表行以 `state_pill` 同步显示。

## 与网页参考的取舍

- 无 ⌘K / ⌘N 快捷键:写信 CTA 的「Ctrl N」徽章标注意图;顶栏的「Ctrl K」徽章与
  EN 副标题(SMART INBOX 等)在高 DPI 窄 Shell(~940 逻辑宽)下把滑块/铃铛挤出
  右缘,0.6.1 起移除,顶栏固定内容压至 ~640px(审计宽度下限随之扩至 940)。
- Agent 卡的英文名行(FOLLOW-UP SENTINEL 等)在 126px 窄卡上被挤出树,0.6.1 起移除;
  自动化程度三标签改两行(仅建议/全自动一行的两端,半自动注记居中于下);
  会议卡时间/地点改堆叠。
- **侧栏邮箱文件夹与 AI 智能分类是真实筛选**(参照为静态行):文件夹按邮件状态
  (star / later / sent / 草稿 / boxed)过滤,AI 分类按数据集 `cluster` 字段过滤,
  徽章计数全部实时计算、为零时隐藏;阅读栏工具行 ★/▤/✕ 为可撤销开关(归档视图
  里再点 ▤ 即恢复),scope 生效时列表横幅显示当前视图胶囊。
- 分诊横幅与筛选计数保持诚实数据口径(实时计算,不用参照静态值)。
- AI 速览的「AI 生成」按钮为本应用真实模型调用入口,参照中无对应物(静态
  0.8s);生成中 / 不可用 / 模型生成三态如实展示。
- **铃铛 / 日历 / 设置是真实弹出面板**(参照为静态图标):铃铛=通知中心(待审批/
  发送失败/待发送草稿/紧急未读,红点仅在有需行动项时显示,条目直达对应视图);日历
  =AI 从邮件提取的会议(点击打开原邮件);设置=主题切换 + 练习场景开关 + 练习数据
  口径说明。面板作为 body 最末层铸造,配 white7/panel2 遮罩,点空白处关闭;面板状态
  变量名为 `pop`(不能叫 `panel`——会遮蔽调色板颜色名并被当作颜色传入图标函数)。
- 搜索框为静态胶囊(提示语 + Ctrl K),不绑定输入。
- 自动化程度表以纯 View 绘制(58% 手柄),无拖拽。
- 练习数据口径披露随 Agent 视图滚动展示。

## 练习数据(与网页参照一致的人物)

林晓薇(Northstar 合同,紧急)、VibeMail 产品团队(周报)、陈立群(招聘委员会)、
Stripe(发票)、GitHub(代码评审)、妈妈(中秋)、AWS Summit(营销)、沈括(数据
平台)。全部为虚构练习数据;Agent 小队(跟进卫士/日程管家/订阅清理/周报生成)与
活动流同为练习数据。
