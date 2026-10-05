# vibemail 0.7.25 — submission packet

Answers to the seven `hub scan` questions (packet: `evidence/hub/review.json`,
regenerated on the final 0.7.25 bytes), plus the reproduction evidence for the
hackathon ("Agentic App 黑客松 2026", scene 01 邮件场景). The manifest is
**publisher-signed** (`yzbtdiy`; key kept outside the repo) and the gate
passes with **no warnings**. The only remaining human steps are the git tag
and this issue itself.

## The seven scan questions

1. **Does the app do what its name, subtitle and description claim?**
   Yes. `bundle/main.splash` implements exactly what the listing names: a
   width-adaptive phone-column app (native at 412px, filling any window
   width) in the warm-paper `#eaeae3` × charcoal `#151413` design, five
   vibe colours invariant across both themes. Five screens: **收件箱**
   (time-of-day greeting, live unread count, an AI 心情播报 line the model
   writes from the visible list and that is labelled 模型生成 / 生成中… /
   固定文案, vibe filter chips that really filter, aura-tinted mail cards
   with unread dot / star / importance); **星轨 Orbit** (mails as floating
   bubbles — size = importance, colour = vibe, slow sin/cos drift, tap to
   open); **详情 Detail** (vibe chip, the **AI 三行摘要** card — ✦-shaped
   colour points with an honest source line: 练习摘要 / 模型生成 / 生成中 /
   服务不可用 / 正文截取 — full body, 星标 / 归档 / 回复 keys); **写信
   Compose** (recipient/subject prefilled, the **五档语气滑杆** 真诚随意 ↔
   轻松幽默 ↔ 自然友好 ↔ 简洁专业 ↔ 正式得体 rewriting the reply preview in
   real time — practice mails carry all five variants, live mail asks
   `model.complete`; single-tap send with 发送中… → 已随波寄出 / 失败保留
   草稿可重试); **我的 Settings** (theme quick-toggle plus the three-mode
   跟随系统 / 亮色 / 暗色 setting that follows the shell's live appearance
   and persists to `theme.json`, the OctoSense capability-declaration card,
   mailbox account management — connect via the host's own sheet, refresh,
   two-step disconnect, archive restore — the labelled practice outage
   switch, and the version row). A floating glass nav pill docks at the
   bottom with a tap-guard so a covered card is not opened by accident.
   All five screenshots in the listing are real captures of these screens
   (2026-10-04).

2. **Do the listing's platforms and category fit?**
   Yes. `productivity` matches a mail app. `platforms: ["windows"]` is the
   only platform actually tested: every capture and interaction in this
   packet ran on Windows 10 (26100) — in the App Hub `card-host.exe`
   (local build linking the reference mail service) at 412 / 700 / 1200
   ×860, and in the OctoSense desktop shell itself (local build, app-hub
   feature, bundle installed from a local signed catalog). No other
   platform was tested, so none is claimed.

3. **Do the granted capabilities match what the app visibly does?**
   Yes — the app requests exactly three capabilities: `mail`, `model`,
   `storage` (`grants: capabilities {"mail", "model", "storage"}, hosts {},
   storage 4194304 bytes, agent none`; no network hosts — the app speaks
   only to platform services).
   - `mail` backs the whole inbox/read/send flow through the platform's
     mail host service (`mail.accounts` / `mail.add_account` / `mail.sync`
     / `mail.list` / `mail.message` / `mail.mark_read` / `mail.send` /
     `mail.remove_account`): real IMAP/SMTP happens in the service;
     accounts are added on the **host's own sign-in sheet** (raised from
     the app's settings panel) and the authorization code stays in the
     host's vault — the app never sees a credential. Verified end to end
     in the OctoSense desktop shell: with a real mailbox connected, real
     INBOX messages are listed and classified by the keyword vibe table,
     and opening them produces real AI summaries (0.7.24/0.7.25 captures
     ev-20/21: a JD verification-code mail summarised as code/expiry/
     handling, a NetEase marketing mail honestly reported as having no
     readable body). Wrong credentials are refused by the real server (the
     service-side trace with the verbatim NO is `evidence/ev-mail-log.txt`;
     the store-shape capture of the sheet flow is ev-13..16).
   - `model` backs three visible features: the AI 三行摘要, the tone-slider
     rewrite and the 心情播报 line — one-shot `model.complete` calls with a
     JSON schema (keys never reach the app). Since 0.7.25 the request
     discipline is one call per open with a 30 s patience: the earlier
     resend loop could burn the host's per-app daily budget in one browsing
     session, and is gone. Rate/budget refusals are classified on screen
     with the host's own wording (「限速·重开重试」「今日额度用完」); where
     nothing answers "model" the app says so honestly and falls back to
     clearly labelled local content (正文截取 / 练习摘要 / 固定文案).
   - `storage` holds the theme preference (`theme.json`) inside the app's
     4 MiB sandbox. No mail content is persisted there.
   The repository additionally contains a development-only harness
   (`bridge/` + `dev/`) that swaps the adapter for a loopback IMAP/SMTP
   bridge. It is NOT part of the submitted bundle — the shipped
   `main.splash` contains no `http://` literal (the store gate refuses
   them) and speaks only to the platform service.

4. **Is any part of the interface deceptive?**
   No. It imitates no system prompt, payment sheet, login or other brand;
   no credential is ever typed inside the app. The simulated send-failure
   is clearly labelled a practice scenario (练习开关, togglable from
   Settings), every AI feature carries its provenance line
   (模型生成 / 生成中 / 固定文案 / 模型改写 / 练习文案), and the mailbox
   banner states exactly which state it is in (未添加 / 已连接 + address +
   count / 不可用 / 0.7.20's honest 「真实邮件正在同步,稍候片刻…」). No
   password/OTP inputs exist in the app.

5. **Does any text read as an instruction to an assistant rather than
   content for a person?**
   No. All strings are user-facing UI copy or practice mail content.

6. **Is any wording abusive or aimed at a private individual?**
   No. Practice senders (Mira 海边小屋、云服务账单、Aurora 周报、外婆 etc.)
   are generic fictional personas from the reference design; live mail is
   rendered as received.

7. **Route: pass, human-review, or reject?**
   Pass. Static, capability-lean, honest about being a concept demo whose
   mail and model paths are real host-service calls. The hub check output
   on the exact submitted bytes (publisher-signed, no
   `--allow-unsigned`):

   ```
   hub check bundle --publisher-key yzbtdiy=1095438c…b5759
   vibemail 0.7.25 — PASSED
     grants: capabilities {"mail", "model", "storage"}, hosts {}, storage 4194304 bytes, agent none
   ```

## Reproduction evidence (hackathon: 真实任务、授权与结果核验)

Everything below is reproducible on Windows with the bundled scripts
(0.7.25 bytes, 2026-10-04 unless noted):

- **Route regression** (`route_test.json`, 6 routes / 42 steps,
  `scripts/run_routes.py`): real clicks against the real card-host window
  at 412×860 — vibe filter + detail summary, orbit bubble open + tri-state
  theme, tone-slider rewrite, single-tap send + replied chip, outage →
  draft kept → retry, archive/restore. 6/6 pass (the runner exits 0 only
  on a full pass; failed steps leave diagnostic captures, which are kept
  out of the repo).
- **Width robustness**: `scripts/audit_overflow.py 412 700 1200` and
  `scripts/audit_missing.py 412 700 1200` walk every screen at all three
  audited widths — no clipped geometry, every expected text present (the
  missing audit boots a fresh instance per screen: long-lived instances'
  scrolls and clicks interfere, a measured finding).
- **Unit tests**: `python -m unittest discover -s service` — 8/8 (the
  compose/send state-machine twin of `main.splash`); bridge parsers 5/5.
- `scripts/drive-demo.py` drives the **real card-host window** over the
  Makepad remote bridge through the full task: boot inbox → vibe filter →
  detail AI summary → tone slider (真诚 / 正式) → single-tap send (已回复
  pill syncs) → simulated outage → **send fails, draft kept** → retry
  succeeds → dark theme. Captures: `bundle/screenshots/01..05` (the
  listing; 05 is the dark theme) and `evidence/ev-01..10` (2026-10-04).
- `scripts/drive-mail.py` drives the **shipped bundle** through the
  platform mail service: Settings → 邮箱账号 → 添加账号 raises the host's
  own sign-in sheet → a wrong authorization code is refused by the real
  server → 取消 returns to the no-account state (ev-13..16; service-side
  verbatim NO in `evidence/ev-mail-log.txt`; last run 2026-10-02,
  re-runnable).
- **A real mailbox with real model output in the shell**: `run.cmd shell`
  (local signed catalog, `../octosense-local-hub/`) → settings → 添加账号
  with a valid authorization code → the banner reads 已连接 + the real
  INBOX is listed (keyword vibe classification, 0.7.20's honest sync
  notice during the ~1 min IMAP window). Opening a real mail fetches the
  body and produces a real three-line summary on first open (ev-20/21,
  0.7.24/0.7.25); with the local-hub budget override in place a whole
  validation round consumed **5 model calls** — the 0.7.25 one-call-per-
  open discipline, verified.
- **Three-mode theme follows the shell**: flipping the shell's appearance
  both ways is followed within ~1-2 s each way (direction semantics fixed
  in 0.6.15); pinned 亮色 / 暗色 ignore the shell; the choice persists in
  `theme.json`. Pixel-sampled by `build/dbg_pixels2.py` (grounds, dark
  cards, all five vibe colours on orbit, neon send CTA).
- Final widget tree and host log snapshots: `evidence/final-snap.json`,
  `evidence/final-log.txt`.

Practice-data boundary (per the hackathon FAQ): the eight practice mails
(with five tone variants each), their importance scores and the
send-failure switch are local and labelled; the mail path is REAL —
platform mail host service, credentials collected on the host's sheet and
kept host-side, verified against a live mailbox; the model path is REAL
host requests (one-shot, schema-checked): in card-host the host honestly
refuses and the UI shows it verbatim; in a shell with AI providers
configured the same buttons produce real model output (ev-20/21).

## Remaining human steps

- [x] `hub keygen` (publisher key kept outside the repo)
- [x] `hub sign-manifest bundle --key … --key-id yzbtdiy`
- [x] `hub check bundle --publisher-key yzbtdiy=<hex>` → PASSED, no warnings
- [ ] Tag the commit (`v0.7.25`), open `Submit vibemail 0.7.25` on
      OctoSense-App-Hub with this packet's answers attached
