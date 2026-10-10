<!-- Submit vibemail 0.7.29 — issue #84 新 Release 评论底稿 -->
<!-- SUBMITTING 规则:首次准入之前,每个新 Release 以评论发在同一 issue,并更新 issue 标题与 Version 字段 -->
<!-- 标题更新为:Submit vibemail 0.7.29 -->
<!-- 标记 <FILL> 的字段在 tag 工作流成功后回填真实值;其余可直接粘贴。 -->
<!-- 七问完整书面回答在 tag 提交内 evidence/hub/SUBMISSION.md。 -->

## Release status

GitHub release ready(可编辑源码已测试、已 stamp;tag 推送后由
`.github/workflows/publish-app.yml` 密封与证明)。本版为 #84 评审意见的
整改落地:发送迁移 `mail.review_send`、练习文案标注、重新盖章升版,
外加 CJK 标签行高修复与 Windows 发送定位澄清。

## App id / Version / Repository URL

- App id:`vibemail`
- Version:`0.7.29`
- Repository:https://github.com/yzbtdiy/VibeMail

## Requested capabilities and app behavior

- `mail` — 收件箱 / 阅读 / 发送全流程(`mail.accounts` / `add_account` /
  `sync` / `list` / `message` / `mark_read` / `review_send` / `remove_account`;
  自 10-04 起宿主 `mail.send` 只回 approval_required,0.7.28 起发送走
  前台审阅通道 `mail.review_send`——宿主弹出原生审阅单、亲手批准后才发出,
  取消审阅进入 cancelled 态(未发送、草稿保留可重发、邮件不打失败标)。
  **物理批准目前仅 macOS/Android;Windows 定位为读信 + AI + 草稿**,
  宿主拒绝时按类如实提示(回调分类器 finish_review 由 13 个单测覆盖)。
  凭据只在**宿主自己的登录 sheet** 上收集并保存在宿主侧,应用不接触;
  断开连接走两步确认。无账号 / 服务不可用时如实显示并回退到已标注的
  练习数据。
- `model` — AI 三行摘要、语气滑杆五档改写与心情播报,均为一次性
  `model.complete`(schema 校验);0.7.25 起为单次请求 + 30 秒耐心,
  限速/额度拒绝按宿主文案如实分类,不可用时如实标注并回退本地内容。
- `storage` — 4 MiB 沙箱内仅存主题偏好 `theme.json`。
- 不声明任何网络主机(`hosts {}`);不申请 net/web/camera/location 等。

## What is not verified

- 除 Windows 10(26100)外未在任何平台测试(listing 只声明 windows)。
- 物理审批发送(Approve & Send)仅 macOS/Android:Windows 上无法端到端
  驱动真实审阅单——回调分类器由单测覆盖,真实 sheet 未在 Windows 驱动。
- 桌面 Shell 内真实邮箱 + 真实模型输出的截图为 2026-10-04(0.7.24/0.7.25
  字节;读信与模型路径此后未变,0.7.28 起仅发送通道变更)。
- v0.7.29 的 GitHub release 工作流运行与下载包核验(本评论内给出)。

## Tag / Full commit SHA / Bundle path

- Tag:`v0.7.29`(annotated,pushed)
- Commit:`6cc9218cf87ec251384a0836d75ff28268d33268`
- Bundle path:`bundle/`

## GitHub workflow run URL

https://github.com/yzbtdiy/VibeMail/actions/runs/38018888782

## Release and pack URL / Release pack SHA256

- Release:https://github.com/yzbtdiy/VibeMail/releases/tag/v0.7.29
- `app.bundle.pack.json` SHA256:`fd48c9e326ce0dd220fef7b0caf65fbb5621346c3c26924aaa2b6ca7dcf7627f`
- 下载核验:`hub publisher-unpack app.bundle.pack.json --out review-bundle`
  + `hub publisher-verify review-bundle`,输出见下。

## Bundle BLAKE3 digest

`d6d08e57833cdd2df5db3da6ed527648c1f27c098a5ab9bf77a9adb9ee37aae0`
(可编辑源码 manifest 的 integrity.bundle_blake3;可移植口径)

## Privacy policy URL / Support contact

- Privacy:https://github.com/yzbtdiy/VibeMail/blob/main/PRIVACY.md
- Support:https://github.com/yzbtdiy/VibeMail/issues

## Platforms tested / App Hub revision the gate ran on

- 平台:Windows 10(26100);card-host 412 / 700 / 1200×860 + OctoSense
  桌面 Shell(本地构建)
- 门禁工具:OctoSense-App-Hub main(本地检出
  `a78fb03053320913e59d4ec8b39773dcc6996cff`)构建的 `hub`;
  工作流侧使用其 pin 修订 `655114c4943cd2490daaefa2173e7b5aaa20669f`

## Gate and publisher verification output

开发副本门禁(0.7.29 最终字节,Windows):

```
> hub check bundle --allow-unsigned

vibemail 0.7.29 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"mail", "model", "storage"}, hosts {}, storage 4194304 bytes, agent none
```

(unsigned 警告是 GitHub provenance 路线的固有形态:可编辑源码保持未签名,
tag 工作流的证明清单提供密封。)

下载包核验(Windows,2026-10-10,pack 取自 release 资产):

```
> hub publisher-unpack build\app.bundle.pack.json --out build\review-bundle
{"app_id":"vibemail","digest":"d6d08e57833cdd2df5db3da6ed527648c1f27c098a5ab9bf77a9adb9ee37aae0","findings":[],"passed":true,"resources":[],"schema":1,"stage":"structural","version":"0.7.29"}

> hub publisher-verify build\review-bundle
{"app_id":"vibemail","digest":"d6d08e57833cdd2df5db3da6ed527648c1f27c098a5ab9bf77a9adb9ee37aae0","findings":[],"passed":true,"resources":[],"schema":1,"stage":"structural","version":"0.7.29"}
```

(sealed pack 的 digest 与可编辑源码 manifest 完全一致;本地 SHA256 复算与
release-receipt.json 的 pack_sha256 相符:`fd48c9e3…7627f`。)

## Scan answers / Screenshots

七问书面回答(含来源引用)在 tag 提交内 `evidence/hub/SUBMISSION.md`,
问题包 `evidence/hub/review.json`(0.7.29 字节生成)。要点:

1. 应用与 listing 声明一致 —— 五屏手机列应用(收件箱/星轨/详情/写信/
   我的),真实截图 5 张;发送走 `mail.review_send` 前台审阅,练习数据下
   语气滑杆标注「练习文案」与「练习摘要」口径对齐。
2. `productivity` / `platforms: ["windows"]` 吻合(唯一实测平台);
   listing 明确 Windows 发送定位(物理批准仅 macOS/Android)。
3. 授予能力与可见功能精确对应(见上「Requested capabilities」);
   无多授权。
4. 无欺骗性界面:无伪造系统/支付/登录 UI,应用内无任何凭据输入;
   练习场景与 AI 来源均如实标注。
5. 无面向助手的指令文本。
6. 无辱骂或针对真实个人的内容(练习发件人均为虚构角色)。
7. 建议:pass(静态、最小授权、诚实降级,mail/model 为真实宿主调用)。

## Optional legacy authentication

(留空 —— 本提交为 GitHub publisher 路线)

## Confirmations

- [x] 无任何密钥/秘密进入仓库或提交包
- [x] 已推送的 tag 不可变(v0.7.25 / v0.7.26 / v0.7.27 保留为历史:
  v0.7.25 为旧摘要口径的签名版;v0.7.26 因 tag 与工作流注册同拍竞态
  未触发运行,按规则以 0.7.27 新版本新 tag 修正;0.7.29 为 #84 整改版)
- [x] 未验证项如实标注,证据未伪造
