# vibemail 0.5.0 — submission packet

Answers to the seven `hub scan` questions (packet: `evidence/hub/review.json`,
regenerated for 0.5.0), plus the reproduction evidence for the hackathon
("Agentic App 黑客松 2026", scene 01 邮件场景). The publisher key, manifest
signing and the OctoSense-App-Hub issue are **HUMAN steps** and remain open.

## The seven scan questions

1. **Does the app do what its name, subtitle and description claim?**
   Yes. `bundle/main.splash` implements exactly what the listing names: the
   0.5.0 forest-ink × warm-paper UI — a **desktop-landscape** agentic mail
   app with a sidebar, a top bar and three surfaces — 智能收件箱 (`inbox_screen`: AI 分诊 banner with live
   counts, filter chips, priority meters, label chips; a permanent
   master-detail — mail CARD list on the left, the reader opening in place
   on the right, no screen push), the reader (`reader_pane`: AI 摘要 card
   with points, suggested actions, meeting detection and sentiment;
   one-tap smart replies; five-state reply strip), AI 写信
   (`write_screen`: tone chips, prompt panel, editable AI draft with
   source pill), and Agent 小队 (`agents_screen`: stats, toggles,
   autonomy dial, live activity stream with approvals). The reply
   lifecycle — 草稿待发送 → 确认 → 发送中 → 已发送/失败 → 重试 — lives on
   each mail object, so the inbox pill and the reader strip always agree.
   0.5.0 is a full rebuild from the latest design: sidebar navigation
   (写信·AI 起草 / 收件箱 / Agent 小队, folders, AI clusters), a top bar with
   an agent-ask search and a theme pill, a three-pane inbox (list |
   in-place reader | AI Copilot: 摘要 / 待办提取 / 语气洞察 / 智能回复), a
   compose card with a COMPOSE WITH AI rail, and the agent squad panel
   (stats / toggles / autonomy / live stream). Two full themes — forest
   dark (default) and warm-sand light — flip from the top-bar pill
   (ev-21, listing screenshot 05): the entire palette flips in place
   while content and layout stay identical. Every screenshot in the
   listing is a real capture of these screens.

2. **Do the listing's platforms and category fit?**
   Yes. `productivity` matches a mail app. `platforms: ["windows"]` is the
   only platform actually tested: every capture and interaction in this
   packet ran on Windows 10 (26100) — in the App Hub `card-host.exe`
   (local build 2026-09-30, which registers the mail host service from
   `crates/mail-service`) at 1200×860 and 1440×860 (the two audited
   desktop widths), and in the
   OctoSense desktop shell itself (local build of the OctoSense repo,
   app-hub feature, with the bundle installed from a local signed
   catalog). No other platform was tested, so none is claimed.

3. **Do the granted capabilities match what the app visibly does?**
   Yes — the app requests exactly two capabilities: `model` and `mail`
   (`grants: capabilities {"mail", "model"}, hosts {}`; no network hosts).
   - `model` backs two visible features: the 「AI 生成」 button on the read
     view (summary points) and 「生成草稿」 on the compose screen, both
     one-shot `model.complete` calls with a JSON schema (fast class;
     OctoSense#95, merged 2026-09-28 — the host picks the model from the
     person's own providers, daily per-app budget, keys never reach the
     app). Where nothing answers "model" (verified in card-host, shown
     verbatim on screen — ev-09, ev-10) the app falls back to clearly
     labelled local templates.
   - `mail` backs the whole inbox/read/draft/send flow through the
     platform's mail host service (`mail.accounts` / `mail.add_account` /
     `mail.list` / `mail.message` / `mail.mark_read` / `mail.send`): real
     IMAP/SMTP happens in the service; accounts are added on the host's own
     sign-in sheet and the authorization code stays in the host's vault —
     the app never sees a credential. Verified end to end in TWO hosts.
     (a) **The real OctoSense desktop shell** (strongest evidence,
     ev-17..19): a local hub instance (`hub keygen` → `certify` →
     `sign-manifest` → `publish` to a local catalog; anchor via
     `OCTOSENSE_HUB_ANCHOR`, install layout via `OCTOSENSE_APP_DATA`)
     admitted the very same `vibemail` bundle through the store's
     signature-verified catalog — launched with
     `--test-action launch-hub:vibemail` — and the shell's OWN Mail
     service answered: the banner's 添加账号 raised the official
     「OctoSense · Add a mail account」 sheet, and a wrong password was
     tested against the real `imap.qq.com:993`, which rejected it (ev-19
     shows the service's own refusal text; the model service is registered
     in that shell too). (b) A `card-host` build linking a reference mail
     service (`OctoSense-App-Hub/crates/mail-service`, the documented
     "Adding a new host service" path): the shipped bundle runs real mail
     the same way (ev-13..16, with `imap.qq.com`'s verbatim NO in the
     sheet). Where no service is registered (stock `card-host`), the
     banner says so and practice data is the labelled fallback. Sending
     keeps the two-step confirm and maps service refusals onto the same
     failed/retry strip.
   The repository additionally contains a development-only harness
   (`bridge/` + `dev/adapter-bridge.splash` + `scripts/dev_bundle.py`)
   that swaps the adapter for a loopback IMAP/SMTP bridge (ev-11 bridge
   off, ev-12 bridge unconfigured). It is NOT part of the submitted bundle
   — the shipped main.splash contains no `http://` literal (the store gate
   refuses them) and speaks only to the platform service — and is now
   optional: the platform service route above supersedes it.

4. **Is any part of the interface deceptive?**
   No. It imitates no system prompt, payment sheet, login or other brand.
   The simulated send-failure is clearly labelled a practice scenario
   (「练习场景:模拟服务中断」) and the AI features are labelled AI 摘要 /
   AI 草稿 with the disclosure that no real mail service is connected.
   No password/OTP inputs exist.

5. **Does any text read as an instruction to an assistant rather than
   content for a person?**
   No. All strings are user-facing UI copy or practice mail content.

6. **Is any wording abusive or aimed at a private individual?**
   No. Sender names (林晓薇、陈立群、沈括、妈妈 etc.) are generic fictional
   practice personas from the reference design.

7. **Route: pass, human-review, or reject?**
   Pass. Static, capability-lean, honest about being a concept demo. The
   hub check output on the exact submitted bytes:

   ```
   vibemail 0.5.0 — PASSED
     grants: capabilities {"mail", "model"}, hosts {}, storage 16777216 bytes, agent none
   ```

## Reproduction evidence (hackathon: 真实任务、授权与结果核验)

Everything below is reproducible on Windows with the bundled scripts:

- `scripts/drive-demo.py` drives the **real card-host window** over the
  Makepad remote bridge (`/snap`, `/click`, `/t`, `/m`, `/g`) through the
  full task at the desktop width (1200×860): open the urgent mail →
  AI 生成 (honest
  model refusal, verbatim on screen) → AI compose with prompt → smart
  reply → **explicit confirm** → sent (state visible in inbox as 已回复)
  → simulated outage → **send fails, draft kept** → re-enable →
  **retry succeeds** → Agent squad approval. Each step asserts the
  expected screen text before capturing; the driver parks the real mouse
  cursor away from the driven window (OS cursor events otherwise eat the
  synthetic taps).
- Captures: `bundle/screenshots/01..04` (the listing: inbox, read, write,
  agents) and `evidence/ev-01..ev-10` (lifecycle: pending draft, confirm
  sheet, sent strip, inbox pill, failed send, kept draft, retry sent,
  agents approval; model service: ev-09 summary-unavailable state, ev-10
  draft fallback, both showing the host's verbatim refusal).
- **Width robustness**: `scripts/audit_missing.py 1200 900` and
  `scripts/audit_overflow.py 1200 900` walk every screen at both audited
  desktop widths — every expected text visible, no clipped geometry
  (`build/missing-report.txt`). The 0.3.x layout is desktop-landscape
  only (rail + card list + in-place reader); the portrait UI is retired.
- `scripts/drive-mail.py` drives the **shipped bundle** in the same
  card-host through the platform mail service: no-account banner
  (ev-13) → 添加账号 raises the host's sign-in sheet (ev-14) → a wrong
  authorization code is tested against the real `imap.qq.com` and the
  sheet shows the server's refusal verbatim (ev-15) → 取消 drops the
  sheet and the app returns to the no-account state (ev-16). The
  service-side trace (`[mail] add_account / sheet.submit / sign-in
  failed / sheet.retry / sheet.cancel`) confirms every hop.
- **Inside the OctoSense desktop shell** (ev-17..19): the same bundle,
  installed through a local signed hub catalog
  (`../octosense-local-hub/`: `hub keygen`/`certify`/`publish`, anchor +
  `OCTOSENSE_APP_DATA` env; see its README), runs as a real window
  manager client. ev-17: the app (0.5.0 UI) in the shell's desktop;
  ev-18: the shell's own 「OctoSense · Add a mail account」 sheet; ev-19:
  the official Mail service's real IMAP login against `imap.qq.com`
  rejected — the sheet says so in its own words. Reproduce with
  `python scripts/official_sheet_run.py <port>` while the shell runs with
  `MAKEPAD_REMOTE=<port>` and `--test-action launch-hub:vibemail`.
- Final widget tree and host log: `evidence/final-snap.json`,
  `evidence/final-log.txt`.

Practice-data boundary (per the hackathon FAQ): the Agent squad, the
activity stream and the send-failure simulation are local; the mail path
is REAL — through the platform mail host service, with credentials
collected on the host's sheet and kept host-side (ev-13..16 were recorded
without a mailbox, so they show the honest no-account and
rejected-sign-in states; a live mailbox needs only a valid authorization
code typed into the host sheet). Model calls are REAL host requests
(schema-checked, one-shot): in card-host the host honestly refuses and
the UI shows it; in an OctoSense desktop Shell built from main ≥
2026-09-28 with AI providers configured, the same buttons produce real
model output.

## Remaining human steps

- [ ] `hub keygen` + `hub sign-manifest` (publisher key stays outside the repo)
- [ ] `hub check --publisher-key <id>=<hex>` → PASSED with no warning
- [ ] Tag the commit, open `Submit vibemail 0.5.0` on OctoSense-App-Hub
      with this packet's answers attached
