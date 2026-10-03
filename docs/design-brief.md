# VibeMail 设计规范(design brief)

0.7.0 的视觉与交互基准是 OctoSense 设计原型参考(展示页提取的完整规格:五种
vibe、星轨收件箱、语气滑杆、暖纸/炭黑双主题)。0.7.1 为对齐参考的第二轮校准:
字号阶梯升至参考值(22/17/13/12.5/12/11),面板圆角统一 16,写信输入框透明底,
详情中性胶囊改 paper2 凹陷底,主题快切 68×36,星轨气泡用参考短名(数据层
`bname`,≤6 字)+ 双层高光与增浓光晕;运行时取舍新增两条——收件箱按帧重绘会
打断滚动拖拽(问候光环保持静态),光晕环必须容于画布(环大于画布被裁成方形,
气泡画布扩至 1.66× 并重推导锚点)。0.7.2 按展示页 bundle 内的 lucide 原始
path 数据重画整套图标(inbox/orbit/pen-line/settings-2/star/archive/
sparkles/arrow-left/send/check,笔画 1.5u),并移除根部四枚大氛围圆——
设计稿光晕只在每张邮件卡上,手机列改不透明纸底;新增最重要的运行时结论:
**View 字面量内调用的铸件辅助函数只保留首尾根**(七格探针证明参数形式无涉,
对角线一律内联字面量分数)。实现为 Splash 脚本应用
(`bundle/main.splash`),以 412px 手机列布局在 card-host 运行(412×860 手机档
与 1200×860 桌面档,后者居中列 + 两侧氛围光环)。本文摘录设计系统、实现映射
与运行时取舍,供后续迭代对照。(0.6.x 暖纸×森林墨绿桌面三栏与 0.2.x 深空主题
见 git 历史。)

## 视图索引

| 参考屏幕 | 实现(main.splash) |
| --- | --- |
| PhoneApp 收件箱 | `inbox_screen` / `mail_card` / `filter_chip` / `inbox_empty` |
| PhoneApp 星轨 | `orbit_screen` / `bubble` / `orbit_x` / `orbit_y` / `bubble_glow` |
| PhoneApp 邮件详情 | `detail_screen` / `summary_row` / `action_capsule` |
| PhoneApp 写信 | `write_screen` / `tone_slider` / `send_button` / `preview_text` |
| PhoneApp 我的 | `set_screen` / `capability_row` / `theme_mode_chip` |
| PhoneFrame / 窗口层 | 根部 `appc` on_render(无状态栏——宿主窗口自带窗框) |

## 布局数学

- **单一 on_render 根**:窗口的全部内容(纸底、侧光环、手机列、导航)在
  `appc` 的一次 mint 内按序铸造——0.6.x 实测分层的 on_render 根会以"晚合成"
  穿透到静态 UI 之上,故不做多层 on_render。
- **导航在流内,不悬浮**:本运行时的点击会命中**所有**重叠的 GestureView
  (0.7.0 实测:悬浮导航与列表卡同时触发),因此底栏胶囊在 Down 流中排在屏幕
  区之后,列表底部留白 36 即可。
- **手机列 412 定宽居中**:`View{Fill Fill align: center}` 包 412 列;412 窗口
  时恰好铺满。固定宽度向容器钳位(0.6.x 实测原语)。
- **星轨锚点**:八个预设百分比位 × (380×560) 画布;气泡尺寸 `52 + imp*62/100`;
  漂移 `dx = cos(anim_t·(0.6+i·0.07))·4`、`dy = sin(anim_t·(0.8+i·0.09))·5`,
  anim 定时器 0.15s,仅在星轨屏重铸。

## 调色板(token → 变量,亮/暗)

| 用途 | 亮色 | 暗色 | 变量 |
| --- | --- | --- | --- |
| 页面底(暖纸/炭黑) | #eaeae3 | #151413 | `paper` |
| 内嵌面板 | #f6f5ee | #1e1d1b | `paper2` |
| 卡片 | #ffffff | #262524 | `paper3` |
| 主文字 | #2a2a2a | #xf2f0e9 | `ink` / `inkSoft` / `inkDim` |
| 发丝线(14%/13% 预混) | #cfcfc9 | #x32312e | `line` / `line2` |
| 导航胶囊底(72% 玻璃预混) | #xf3f2eb | #x1b1a19 | `glass` |
| vibe 五色(双主题不变) | coral #ff6a3d / neon #f6ff91 / mint #x7de888 / pink #xff90ff / blue #x2a7dfa | 同左 | `coralC`… |
| vibe chip 底(25%/18% α) | 如 #xff6a3d40 | 如 #xff6a3d2e | `chipBgFocus`… |
| neon 点/要点(亮色换深) | #xc9b300 | #xf6ff91 | `dotJoy` |
| 星标琥珀 / 失败红 | #xffb03d / #xb33626 | 同左 / #xf08a75 | `amberC` / `failT` |

**默认亮色**;`apply_theme(l)` 重绑全部 `let`,`repaint()`(= `ui.appc.render()`)
重铸整窗;三态主题(跟随系统采样宿主调色板/亮/暗)持久化 theme.json,0.4s
轮询器跟随 Shell 亮暗。

## 组件语言

- **氛围光环 aura**(`aura_focus`…`aura_brand`):参考的 SVG 高斯模糊光球在本
  运行时无 blur,以三枚 vibe 色系半透明圆错位叠放模拟;邮件卡左上 120、详情卡
  右上 170、问候区品牌 64、星轨气泡外圈 `bubble_glow`(两环 α 0x20/0x10)。
- **绘制图标族**:沿用 0.6.17 语法(方形画布、16px 基准 2px 圆头笔画、
  `ipart`/`iring`/`icell`、cut 镂空、45° 圆格链)。新增:火焰(专注)、叶片
  (平静)、气泡(连接)、托盘(收件箱导航)、行星环(星轨导航)、斜笔(写信)、
  左折返(返回)、纸飞机(发送);太阳/星芒/四角星/对勾/刷新/
  归档/信封/滑杆/月牙沿用旧族。vibe chip 内嵌 9-10px vibe 字形。
- **vibe chip**:圆角全径胶囊,vibe 色 α 底 + 墨色(亮)/vibe 色(暗)文字;
  列表未读点用 `dot_color`(neon 在亮色换 #c9b300 保证对比)。
- **语气滑杆**:348 轨道 + 三档点 + 墨色圆钮(白描边),三个等宽点击区 + 可点
  档位标签;当前档粉色胶囊显示 真诚随意/自然友好/正式得体。
- **AI 三行摘要**:paper2 圆角卡,星芒 + "AI 三行摘要" + 来源词(练习摘要/
  模型生成/生成中/服务不可用/正文截取),每条前置 ✦ 形菱形点(vibe 色)。
- **发送按钮**:idle 霓虹黄底墨字"发送"(纸飞机)→ sending"发送中…" →
  sent 薄荷绿"已随波寄出"(对勾)→ failed"发送失败 · 点按重试"(刷新)。
  单击发送(参考行为);练习失败由设置开关模拟。

## 与参考原型的取舍

- 字体:参考用 Unbounded / Space Grotesk / JetBrains Mono;运行时只有内置
  字体,标题用 `theme.font_bold`,层次靠字号(21/16.5/12.5/11/9.5)与字重。
- emoji vibe 字形(🔥🌞🍃✨🫧)由拼绘字形替代(0.6.17 结论:字体 dingbat 在
  CJK 回退下渲染不受控)。
- 参考的 framer-motion 弹簧转场/spring 列表入场:本运行时整树重铸,切换瞬时
  完成;星轨漂浮以 0.15s 定时器近似。
- 参考状态栏 9:41 与电池:不采用——宿主窗口已有自己的窗框,应用直接以屏幕
  内容开始(各屏顶部留白 12-14px)。
- 参考底部悬浮胶囊改为流内停靠(点击穿透实测,见布局数学)。
- 详情"回复"直达写信并预填收件人/主题;星轨气泡可点开邮件(参考一致);
  归档在设置里一键恢复(参考无归档恢复入口)。
- 新鲜写信默认 Mira 线程(与参考手机演示一致);练习邮件每封内置三种语气
  回信(Mira 三条与参考文案逐字一致)。

## 练习数据(与参考原型一致的八封)

Mira(海边玻璃小屋,joy,92)、云服务账单(¥236.40,focus,86)、产品周报·
Aurora(北极星 +12%,spark,64)、GitHub(仓库周报,calm,32)、读书会·山雾
小组(书目投票,link,50)、外婆(桂花,joy,95,星标)、设计系统双周报(高斯
模糊,spark,58)、HR·OctoSense(黑客松确认,focus,90)。Mira 与外婆带星标;
前三封未读。全部为虚构练习数据。
