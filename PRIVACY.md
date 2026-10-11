# Privacy Policy — VibeMail

VibeMail is the mood layer for the OctoSense inbox: it labels each mail with
a vibe, offers AI summaries and tone rewrites, and sends mail on your
explicit tap. This policy describes version 0.8.x.

**VibeMail collects, stores and transmits no personal data of its own, and
talks to no server.** The app declares no network hosts; every network
operation happens inside the platform's host services:

- **`mail` capability** — the inbox/read/send flow runs through the
  platform's mail host service. Mailbox addresses, authorization codes and
  passwords are collected on the **host's own sign-in sheet** and kept in
  the host's vault. The app never sees, holds or transmits a credential;
  it only receives the message list, bodies and send results the service
  returns. Saving a reply as a draft (`mail.compose`, 0.8.0) stores it in
  the host-side draft box under the app's own namespace and is receipt-
  checked (`mail.compose_status`); drafts are only ever edited with the
  host's revision lock. Disconnecting an account (`mail.remove_account`)
  removes the host-side account.
- **`model` capability** — AI three-line summaries (the same one call also
  extracts a schedule proposal, 0.8.0), tone-slider rewrites, the mood line
  and the one-line weekly phrase are one-shot `model.complete` requests to
  the host's model service. The app sends only the visible list context
  (subject, sender label, vibe label), the open mail's subject/body, the
  reply text being rewritten, or the weekly counts — never credentials;
  provider API keys stay with the host. Requests fail honestly (labelled on
  screen) when no model service or budget answers.
- **`storage` capability** — the app's sandbox (4 MiB) holds the theme
  preference (`theme.json`) plus the staged export files (a `.ics` event or
  the weekly report text) written right before you confirm the host's export
  sheet. No mail content is persisted there. `storage.accounts` is declared
  so the app agent's tools can be bound to the current account by the Shell.
- **`files` capability** (0.8.0) — exporting a schedule proposal (`.ics`) or
  the weekly report (text) goes through the host's file sheet
  (`files.export`): you pick the destination, the host moves the bytes. The
  app never learns an OS path.
- **`glance` capability** (0.8.0) — publishing the desktop glance card
  (`glance.publish`) shows the unread count, the per-vibe distribution and
  the mood line on the host's glance screen for 24 hours. The card is a
  template plus data (`initial`) — it contains no executable script.

**App agent (0.8.0).** VibeMail ships a **read-only** app agent
(`bundle/tools.json` + `bundle/AGENT.md`, profile `read-only`, no background
triggers). Its only two tools are read-level and host-implemented:
`vibemail.draft_status` (the host-verified draft ledger) and
`vibemail.glance_cards` (this app's published glance cards). The agent
cannot send, draft, edit, delete, publish or withdraw anything; both tools
are marked `private_data` and are never shared.

**Practice data.** Where no mail service exists, VibeMail shows eight
clearly labelled practice mails and a practice send-failure switch; these
are local fixtures, not real messages or real sends.

**No telemetry.** No analytics, tracking, ads or third-party services of
any kind.

Contact: https://github.com/yzbtdiy/VibeMail/issues
