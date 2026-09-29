# agentic-mail bridge — IMAP/SMTP ↔ HTTP（仅本机）

受隔离规则限制，OctoSense 应用不能自己说 IMAP/SMTP（受管应用禁用原始套接字，
且应用不得持有邮箱凭据）。这个网桥跑在**你的电脑**上：持有邮箱授权码（只存在
`config.json`，永远不进应用包），把收发能力以 HTTP JSON 暴露给应用。API 形状
刻意对齐平台官方 mail 宿主服务（`mail.list`/`mail.message`/`mail.send`），
将来切换官方服务时应用侧几乎不用改。

**安全边界**：仅监听 `127.0.0.1`，明文 HTTP——应用的策略恰好是"明文只允许
回环"，所以无需证书、不暴露到网络。凭据只在本文件和网桥进程内存中。

## 运行

```sh
cp config.example.json config.json   # 填入你的邮箱与授权码
python bridge.py                     # http://127.0.0.1:8443
```

授权码获取（不是登录密码）：
- QQ 邮箱：设置 → 账户 → 开启 IMAP/SMTP 服务 → 生成授权码；imap.qq.com:993 / smtp.qq.com:465
- 163 邮箱：设置 → POP3/SMTP/IMAP → 开启并获取授权码；imap.163.com:993 / smtp.163.com:465
- Gmail：开启两步验证 → 应用专用密码；imap.gmail.com:993 / smtp.gmail.com:465

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | `{ready, email}`；未配置/登录失败时 `{ready:false, error}` |
| GET | `/list?limit=20` | 最新 N 封：`{total, messages:[{id,sender,address,subject,preview,time,body,unread}]}` |
| GET | `/message?id=` | 单封全文 |
| POST | `/send` `{to,subject,body}` | SMTP 真实发送 → `{accepted:true}` |
| POST | `/mark_read` `{id}` | 标已读 |

## 测试

```sh
python bridge/test_bridge.py   # 解析层 5 个用例（无网络、无账号）
```

真实收发的端到端验证需要 `config.json` 里的有效账号；应用侧在
card-host 里即可完整演示（见仓库根 README「复现」）。
