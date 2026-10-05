# Privacy Policy — VibeMail

VibeMail is the mood layer for the OctoSense inbox: it labels each mail with
a vibe, offers AI summaries and tone rewrites, and sends mail on your
explicit tap. This policy describes version 0.7.x.

**VibeMail collects, stores and transmits no personal data of its own, and
talks to no server.** The app declares no network hosts; every network
operation happens inside the platform's host services:

- **`mail` capability** — the inbox/read/send flow runs through the
  platform's mail host service. Mailbox addresses, authorization codes and
  passwords are collected on the **host's own sign-in sheet** and kept in
  the host's vault. The app never sees, holds or transmits a credential;
  it only receives the message list, bodies and send results the service
  returns. Disconnecting an account (`mail.remove_account`) removes the
  host-side account.
- **`model` capability** — AI three-line summaries, tone-slider rewrites
  and the mood line are one-shot `model.complete` requests to the host's
  model service. The app sends only the visible list context (subject,
  sender label, vibe label) or the reply text being rewritten — never
  credentials; provider API keys stay with the host. Requests fail honestly
  (labelled on screen) when no model service or budget answers.
- **`storage` capability** — the app's sandbox (4 MiB) holds the theme
  preference (`theme.json`). No mail content is persisted there.

**Practice data.** Where no mail service exists, VibeMail shows eight
clearly labelled practice mails and a practice send-failure switch; these
are local fixtures, not real messages or real sends.

**No telemetry.** No analytics, tracking, ads or third-party services of
any kind.

Contact: https://github.com/yzbtdiy/VibeMail/issues
