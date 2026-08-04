# Deliverability checklist

Run before any new program, any domain change, and any send to a list that has been
quiet for 90+ days.

## Authentication (a human must verify in DNS)

- [ ] **SPF** — one record, all sending services included, under the 10-lookup limit
- [ ] **DKIM** — signing enabled on the sending domain, 2048-bit key
- [ ] **DMARC** — record exists; policy at least `p=none` with `rua` reporting, moving
      toward `p=quarantine` once aligned
- [ ] **Alignment** — the `From:` domain matches the SPF/DKIM domain
- [ ] **Subdomain** — marketing sends from a subdomain, not the root domain that
      carries transactional and human mail

## List health

- [ ] Consent is documented — where each contact opted in, and when
- [ ] No purchased, scraped or appended addresses (ever)
- [ ] Hard bounces removed immediately; soft bounces after 3 consecutive
- [ ] Sunset policy defined — no engagement in N days → suppression, not more sends
- [ ] Re-permission campaign designed for any list dormant 6+ months
- [ ] Role addresses (info@, sales@) segmented or removed

## Warm-up (new domain or IP)

- [ ] Start at your most engaged segment, smallest volume
- [ ] Roughly double daily volume every 2–3 days, never in one jump
- [ ] Watch complaint rate at every step; pause on any rise
- [ ] Reach full volume over 3–4 weeks, not days

## Content

- [ ] Text-to-image ratio favours text; the email is readable with images blocked
- [ ] Every link points to the sending brand's domain — no shorteners
- [ ] Plain-text alternative exists and is real, not "view in browser"
- [ ] No spam-trigger stacking: ALL CAPS subject, multiple exclamation marks, "FREE!!!"
- [ ] Alt text on every image
- [ ] Renders on mobile at 375px — single column, ≥14px body, tappable CTA

## Compliance elements

- [ ] Working one-click unsubscribe, honoured within 10 days (CAN-SPAM) / immediately (best practice)
- [ ] `List-Unsubscribe` and `List-Unsubscribe-Post` headers set
- [ ] Physical postal address in the footer
- [ ] Sender name and `From:` address identify the real sender
- [ ] Subject line is not deceptive about the content
- [ ] GDPR/CASL: lawful basis recorded; consent language available on request

## Health thresholds

| Metric | Healthy | Investigate | Stop sending |
| --- | --- | --- | --- |
| Complaint rate | < 0.1% | 0.1–0.3% | > 0.3% |
| Hard bounce rate | < 0.5% | 0.5–2% | > 2% |
| Unsubscribe rate | < 0.5% | 0.5–1% | > 1% |
| Open rate trend | stable/rising | falling 3 sends | falling sharply |

> Post-MPP, open rate is a weak signal — treat it as directional only and judge on
> clicks, replies and downstream conversion.
