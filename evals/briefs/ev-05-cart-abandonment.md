---
id: EV-05
brief: Build a cart abandonment flow.
expect_owner: email-lifecycle
expect_flags: [compliance]
---

Every email in the flow needs sender identity, a working unsubscribe and a physical
address, matched to the regimes ticked in `ORG.md` §3. The flow also needs exit
conditions — the classic failure is continuing to send after the purchase completes.
