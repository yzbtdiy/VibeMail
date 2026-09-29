# agentic-mail 0.1.0 — submission packet

Answers to the seven `hub scan` questions (packet: `evidence/hub/review.json`,
generated 2026-09-29), plus the reproduction evidence for the hackathon
("Agentic App 黑客松 2026", scene 01 邮件场景). The publisher key, manifest
signing and the OctoSense-App-Hub issue are **HUMAN steps** and remain open.

## The seven scan questions

1. **Does the app do what its name, subtitle and description claim?**
   Yes. `bundle/main.splash` implements exactly the five screens the listing
   names: 智能收件箱 (`inbox_screen`: AI 分诊 banner, 重要邮件 / 稍后处理
   groups), 邮件阅读 (`read_screen`: AI 摘要 card with bullet points and a
   suggested action, attachment card, quick-reply chips), AI 写信起草
   (`write_screen`: prompt input, 语气选择 chips, editable AI draft),
   跟进待办 (`todo_screen`: segmented tabs 待跟进 / 我承诺的 / 已完成),
   and 我的 (`me_screen`, which also carries the practice-data disclosure).
   The reply lifecycle — 草稿待发送 → 确认 → 发送中 → 已发送/失败 → 重试 —
   lives on each mail object, so the inbox pill and the read strip always
   agree. Every screenshot in the listing is a real capture of these screens
   (see evidence below).

2. **Do the listing's platforms and category fit?**
   Yes. `productivity` matches a mail app. `platforms: ["windows"]` is the
   only platform actually tested: every capture and interaction in this
   packet ran on Windows 10 (26100) against the App Hub `card-host.exe`
   built 2026-09-28. No other platform was tested, so none is claimed.

3. **Do the granted capabilities match what the app visibly does?**
   Yes — the app requests exactly two capabilities: `model` and `mail`
   (`grants: capabilities {"mail", "model"}, hosts {}`; no network hosts).
   - `model` backs two visible features: the 「AI 生成」 button on the read
     view (summary points + suggested action) and 「重新生成」 on the
     drafting screen, both one-shot `model.complete` calls with a JSON
     schema (fast class; OctoSense#95, merged 2026-09-28 — the host picks
     the model from the person's own providers, daily per-app budget, keys
     never reach the app). Where nothing answers "model" (verified in
     card-host, shown verbatim on screen — ev-09, ev-10) the app falls
     back to clearly labelled local templates.
   - `mail` backs the whole inbox/read/draft/send flow through the
     platform's mail host service (`mail.accounts` / `mail.list` /
     `mail.message` / `mail.mark_read` / `mail.send`): real IMAP/SMTP
     happens in the service; accounts are added on the host's own sheet
     and credentials stay in the system vault. card-host answers no
     service, and the banner shows exactly that with practice data as the
     labelled fallback (see 01-inbox.png); in an OctoSense desktop Shell
     the same code path is live mail. Sending keeps the two-step confirm
     and maps service refusals onto the same failed/retry strip.
   The repository additionally contains a development-only harness
   (`bridge/` + `dev/adapter-bridge.splash` + `scripts/dev_bundle.py`)
   that swaps the adapter for a loopback IMAP/SMTP bridge so the real
   flow can be captured on a dev machine (ev-11 bridge off, ev-12 bridge
   unconfigured). It is NOT part of the submitted bundle: the shipped
   main.splash contains no `http://` literal (the store gate refuses
   them) and speaks only to the platform service.

4. **Is any part of the interface deceptive?**
   No. It imitates no system prompt, payment sheet, login or other brand.
   The simulated send-failure is clearly labelled a practice scenario
   (「练习场景:模拟服务中断」) and the AI features are labelled AI 摘要 /
   AI 起草 with the disclosure that no real mail service is connected.
   No password/OTP inputs exist.

5. **Does any text read as an instruction to an assistant rather than
   content for a person?**
   No. All strings are user-facing UI copy or practice mail content.

6. **Is any wording abusive or aimed at a private individual?**
   No. Sender names (张伟、李娜、王强、陈晨、小林) are generic fictional
   practice personas.

7. **Route: pass, human-review, or reject?**
   Pass. Static, capability-free, honest about being a concept demo. The
   hub check output on the exact submitted bytes:

   ```
   agentic-mail 0.1.0 — PASSED
     [warning] publisher-signature: unsigned: accountability rests on the hub alone
     grants: capabilities {"mail", "model"}, hosts {}, storage 16777216 bytes, agent none
   ```

## Reproduction evidence (hackathon: 真实任务、授权与结果核验)

Everything below is reproducible on Windows with the bundled scripts:

- `scripts/drive-demo.py` drives the **real card-host window** over the
  Makepad remote bridge (`/snap`, `/click`, `/t`, `/m`, `/g`) through the
  full task: open the urgent mail → AI draft → insert → **explicit confirm**
  → sent (state visible in inbox as 已回复) → simulated outage → **send
  fails, draft kept** → edit → **retry succeeds** → todo tabs → profile.
  Each step asserts the expected screen text before capturing.
- Captures: `bundle/screenshots/01..05` (the listing) and
  `evidence/ev-01..ev-10` (lifecycle: pending draft, confirm sheet,
  sent strip, inbox pill, failed send, kept draft, retry sent, todo tab;
  model service: ev-09 summary-unavailable state, ev-10 draft fallback,
  both showing the host's verbatim refusal). The driver asserts the
  refusal text is on screen before finishing.
- Final widget tree and host log: `evidence/final-snap.json`,
  `evidence/final-log.txt`.

Practice-data boundary (per the hackathon FAQ): mail, todos, send and
failure are local simulation — the app connects to no real mail service
and fabricates no real-world facts. Model calls are REAL host requests
(schema-checked, one-shot): in card-host the host honestly refuses and
the UI shows it; in an OctoSense desktop Shell built from main ≥ 2026-09-28
with AI providers configured, the same buttons produce real model output
(rehearse via PUBLISHING §4; not captured in this packet, which was
recorded on Windows card-host only).

## Remaining human steps

- [ ] `hub keygen` + `hub sign-manifest` (publisher key stays outside the repo)
- [ ] `hub check --publisher-key <id>=<hex>` → PASSED with no warning
- [ ] Tag the commit, open `Submit agentic-mail 0.1.0` on OctoSense-App-Hub
      with this packet's answers attached
