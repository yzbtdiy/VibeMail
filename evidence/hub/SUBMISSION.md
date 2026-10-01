# vibemail 0.6.10 — submission packet

Answers to the seven `hub scan` questions (packet: `evidence/hub/review.json`,
regenerated for 0.6.10), plus the reproduction evidence for the hackathon
("Agentic App 黑客松 2026", scene 01 邮件场景). The manifest is
**publisher-signed** (`yzbtdiy`; key kept outside the repo) and the gate
passes with **no warnings**. The only remaining human steps are the git tag
and this issue itself.

## The seven scan questions

1. **Does the app do what its name, subtitle and description claim?**
   Yes. `bundle/main.splash` implements exactly what the listing names: a
   **desktop-landscape** agentic mail app in the 0.6 warm-paper × forest-ink
   design (light theme default, dark theme one tap away) — a 264px sidebar
   (brand, gradient compose CTA, nav with live badges, mailbox folders, AI
   clusters, AGENT ACTIVE status card, calendar/settings footer), a 60px top
   bar (agent search, VIBE AGENT pill, theme slider, notification bell) and
   per-view bodies: 智能收件箱 (420px list + in-place reading pane whose
   collapsible inline **AI 速览** carries summary points, 待办提取,
   sentiment, meeting detection and one-tap smart replies), AI 写信 (a
   centred composer card with tone chips and an editable AI draft plus the
   COMPOSE WITH AI rail), and Agent 小队 (stats, toggles, autonomy dial,
   live activity stream with approvals). Everything decorative-looking is
   real: the mailbox folders and AI clusters are **live filters** (star /
   archive / trash are reversible toggles in the reader's tool row, badge
   counts computed from the data), and the bell / calendar / settings icons
   open **real panels** (a notification centre whose entries jump to the
   pending work, an AI-extracted meeting list, theme + practice switches and
   mailbox management: connect, refresh, two-step disconnect via
   `mail.remove_account`). The reply lifecycle — 草稿待发送 → 确认 → 发送中
   → 已发送/失败 → 重试 — lives on each mail object, so the inbox pill and
   the reader strip always agree. 0.6.1 hardens the chrome for hi-DPI
   shells (fixed top-bar content ≈640 logical px; the audits now span 940 /
   1000 / 1200 / 1440). 0.6.10 makes a real mailbox work end to end inside
   the OctoSense shell (details in Q3). Every screenshot in the listing is
   a real capture of these screens, regenerated on the final 0.6.10 bytes.

2. **Do the listing's platforms and category fit?**
   Yes. `productivity` matches a mail app. `platforms: ["windows"]` is the
   only platform actually tested: every capture and interaction in this
   packet ran on Windows 10 (26100) — in the App Hub `card-host.exe`
   (local build linking the reference mail service from
   `crates/mail-service`) at 940/1000/1200/1440×860, and in the OctoSense
   desktop shell itself (local build, app-hub feature, bundle installed
   from a local signed catalog; the shell's hi-DPI window hands the app
   ~940 logical px, which is why the audits start there). No other
   platform was tested, so none is claimed.

3. **Do the granted capabilities match what the app visibly does?**
   Yes — the app requests exactly two capabilities: `model` and `mail`
   (`grants: capabilities {"mail", "model"}, hosts {}`; no network hosts).
   - `model` backs two visible features: the 「AI 生成」 button on the
     reader's AI 速览 (summary points) and 「生成草稿」 on the compose
     screen — one-shot `model.complete` calls with a JSON schema (fast
     class; OctoSense#95 — the host picks the model from the person's own
     providers, keys never reach the app; since 0.5.4 the chips show the
     host-reported `meta.model` name). Where nothing answers "model"
     (verified in card-host, ev-09/ev-10 show the host's refusal verbatim
     on screen) the app falls back to clearly labelled local templates.
   - `mail` backs the whole inbox/read/draft/send flow through the
     platform's mail host service (`mail.accounts` / `mail.add_account` /
     `mail.sync` / `mail.list` / `mail.message` / `mail.mark_read` /
     `mail.send` / `mail.remove_account`): real IMAP/SMTP happens in the
     service; accounts are added on the host's own sign-in sheet (raised
     from the app's settings panel) and the authorization code stays in
     the host's vault — the app never sees a credential. Verified end to
     end in TWO hosts. (a) **The real OctoSense desktop shell**: the same
     bundle admitted through a signature-verified local catalog, driven by
     the shell's own Mail service. On 2026-10-01 a real mailbox
     (`yzbtdiy@yeah.net`) was connected and **5 real messages were listed
     in the app** — the 0.6.4..0.6.10 fixes this proves: the app now calls
     `mail.sync` before `mail.list` (the shell's list reads only the local
     cache), replies only raise flags consumed by a boot-time poller
     (timers registered inside reply callbacks are dropped by the shell's
     runner), and live list rows no longer read the `body` field the
     shell's list payload omits (bodies arrive via `mail.message` on
     open). Wrong credentials are still tested against the real server
     and refused (the card-host trace in `evidence/ev-mail-log.txt` holds
     the verbatim NO; the 0.6.x re-capture of that flow is
     ev-13..16). (b) A `card-host` build linking the reference mail
     service: same bundle, same flow, driven by `scripts/drive-mail.py`
     (re-runnable). Where no service is registered, the banner says so and
     practice data is the labelled fallback; sending keeps the two-step
     confirm and maps service refusals onto the same failed/retry strip.
   The repository additionally contains a development-only harness
   (`bridge/` + `dev/adapter-bridge.splash` + `scripts/dev_bundle.py`)
   that swaps the adapter for a loopback IMAP/SMTP bridge. It is NOT part
   of the submitted bundle — the shipped main.splash contains no `http://`
   literal (the store gate refuses them) and speaks only to the platform
   service — and is now optional: the platform service route supersedes
   it.

4. **Is any part of the interface deceptive?**
   No. It imitates no system prompt, payment sheet, login or other brand.
   The simulated send-failure is clearly labelled a practice scenario
   (「练习:模拟服务中断」, togglable from the settings panel), the AI
   features are labelled AI 速览 / AI 草稿 with the practice/AI provenance
   line, and the mailbox banner states exactly which state it is in
   (未添加 / 已连接 + address + count / 不可用). No password/OTP inputs
   exist in the app.

5. **Does any text read as an instruction to an assistant rather than
   content for a person?**
   No. All strings are user-facing UI copy or practice mail content.

6. **Is any wording abusive or aimed at a private individual?**
   No. Sender names (林晓薇、陈立群、沈括、妈妈 etc.) are generic fictional
   practice personas from the reference design.

7. **Route: pass, human-review, or reject?**
   Pass. Static, capability-lean, honest about being a concept demo whose
   mail and model paths are real host-service calls. The hub check output
   on the exact submitted bytes (publisher-signed, no
   `--allow-unsigned`):

   ```
   hub check bundle --publisher-key yzbtdiy=1095438c…b5759
   vibemail 0.6.10 — PASSED
     grants: capabilities {"mail", "model"}, hosts {}, storage 16777216 bytes, agent none
   ```

## Reproduction evidence (hackathon: 真实任务、授权与结果核验)

Everything below is reproducible on Windows with the bundled scripts:

- **Route regression** (`route_test.json`, 6 routes / 43 steps,
  `scripts/run_routes.py`): real clicks against the real card-host window
  at 1200×860 — in-place read + honest model refusal, smart-reply with
  two-step confirmed send and inbox pill sync, outage → draft kept →
  retry, agent approval + theme flip, sidebar folder/cluster filters, and
  the notification/calendar/settings panels. 6/6 pass on the submitted
  bytes.
- **Width robustness**: `scripts/audit_overflow.py 940 1000 1200 1440`
  and `scripts/audit_missing.py 940 1000 1200 1440` walk every screen at
  all four audited widths — no clipped geometry, every expected text
  present.
- `scripts/drive-demo.py` drives the **real card-host window** over the
  Makepad remote bridge through the full task: open the urgent mail →
  AI 生成 (honest model refusal, verbatim on screen) → AI compose →
  smart reply → **explicit confirm** → sent (已回复 pill syncs) →
  simulated outage → **send fails, draft kept** → re-enable → **retry
  succeeds** → agent approval. Captures: `bundle/screenshots/01..05` (the
  listing; 05 is the dark theme) and `evidence/ev-01..10` — all
  regenerated on the final 0.6.10 UI.
- `scripts/drive-mail.py` drives the **shipped bundle** through the
  platform mail service: settings → 邮箱账号 → 添加账号 raises the
  host's own sign-in sheet → a wrong authorization code is refused by the
  real server → 取消 returns to the no-account state (ev-13..16,
  re-captured on the 0.6.x settings UI; the service-side trace with the
  verbatim NO is `evidence/ev-mail-log.txt`).
- **A real mailbox in the shell**: `run.cmd shell` (local signed catalog,
  `../octosense-local-hub/`) → settings → 添加账号 with a valid
  authorization code → the banner reads 已连接 <address> · N 封真实邮件
  and the list shows the real INBOX (verified 2026-10-01 with a yeah.net
  mailbox: 5 real messages). New mail arrives via 设置 → 刷新
  (`mail.sync` then `mail.list`; the service lists the newest 20 INBOX
  messages).
- Final widget tree and host log: `evidence/final-snap.json`,
  `evidence/final-log.txt`.

Practice-data boundary (per the hackathon FAQ): the Agent squad, the
activity stream and the send-failure simulation are local; the mail path
is REAL — platform mail host service, credentials collected on the host's
sheet and kept host-side, verified against a live mailbox; the model path
is REAL host requests (schema-checked, one-shot): in card-host the host
honestly refuses and the UI shows it; in a shell with AI providers
configured the same buttons produce real model output (passed with a
configured MiniMax at 0.5.x; the flows are unchanged).

## Remaining human steps

- [x] `hub keygen` (publisher key kept outside the repo)
- [x] `hub sign-manifest bundle --key … --key-id yzbtdiy`
- [x] `hub check bundle --publisher-key yzbtdiy=<hex>` → PASSED, no warnings
- [ ] Tag the commit (`v0.6.10`), open `Submit vibemail 0.6.10` on
      OctoSense-App-Hub with this packet's answers attached
