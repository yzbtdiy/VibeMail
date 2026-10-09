<!-- Submit vibemail 0.7.27 — submit-app.yml 表单字段答案底稿 -->
<!-- 表单:https://github.com/OctoSense-org/OctoSense-App-Hub/issues/new?template=submit-app.yml -->
<!-- 标记 <FILL> 的字段在 tag 工作流成功后回填真实值;其余可直接粘贴。 -->
<!-- 七问完整书面回答在 evidence/hub/SUBMISSION.md(tag 提交内)。 -->

## Release status

GitHub release ready(可编辑源码已测试、已 stamp;tag 推送后由
`.github/workflows/publish-app.yml` 密封与证明)。

## App id / Version / Repository URL

- App id:`vibemail`
- Version:`0.7.27`
- Repository:https://github.com/yzbtdiy/VibeMail

## Requested capabilities and app behavior

- `mail` — 收件箱 / 阅读 / 发送全流程(`mail.accounts` / `add_account` /
  `sync` / `list` / `message` / `mark_read` / `send` / `remove_account`)。
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
- 0.7.27 字节上的桌面 Shell 内真实邮箱 + 真实模型输出未重跑(应用字节
  与 0.7.25 相同——仅 manifest 升版/剥签名/新口径 stamp;Shell 实证为
  2026-10-04 的 ev-20/21 与真实 INBOX 记录)。
- v0.7.27 的 GitHub release 工作流运行与下载包核验(本 issue 内给出)。

## Tag / Full commit SHA / Bundle path

- Tag:`v0.7.27`(annotated,pushed)
- Commit:`<FILL — git rev-parse v0.7.27^{commit} 或 git ls-remote 确认>`
- Bundle path:`bundle/`

## GitHub workflow run URL

<FILL — Actions「Publish OctoSense app」成功运行链接>

## Release and pack URL / Release pack SHA256

- Release:`<FILL — v0.7.27 release 链接>`
- `app.bundle.pack.json` SHA256:`<FILL — release-receipt.json 的 pack_sha256>`
- 下载核验:`hub publisher-unpack app.bundle.pack.json --out review-bundle`
  + `hub publisher-verify review-bundle`,输出见下。

## Bundle BLAKE3 digest

`a67cf5686ca37e29dcf376ec7364464d4c70f52f995d9836e35e264c84aaffaa`
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

开发副本门禁(0.7.27 最终字节,Windows):

```
> hub check bundle --allow-unsigned

vibemail 0.7.27 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"mail", "model", "storage"}, hosts {}, storage 4194304 bytes, agent none
```

(unsigned 警告是 GitHub provenance 路线的固有形态:可编辑源码保持未签名,
tag 工作流的证明清单提供密封。)

下载包核验:<FILL — hub publisher-verify review-bundle 的完整输出>

## Scan answers / Screenshots

七问书面回答(含来源引用)在 tag 提交内 `evidence/hub/SUBMISSION.md`,
问题包 `evidence/hub/review.json`(0.7.27 字节生成)。要点:

1. 应用与 listing 声明一致 —— 五屏手机列应用(收件箱/星轨/详情/写信/
   我的),真实截图 5 张(2026-10-09 现运行时截取)。
2. `productivity` / `platforms: ["windows"]` 吻合(唯一实测平台)。
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
- [x] 已推送的 tag 不可变(v0.7.25 与 v0.7.26 保留为历史:v0.7.25 为旧摘要
  口径的签名版;v0.7.26 因 tag 与工作流注册同拍竞态未触发运行,按规则以
  0.7.27 新版本新 tag 修正,字节与 0.7.26 相同)
- [x] 未验证项如实标注,证据未伪造
