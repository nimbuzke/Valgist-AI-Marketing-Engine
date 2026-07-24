---
name: compliance-gate
description: Use before marking ANY outbound-facing asset publish-ready — emails, ads, landing pages, social posts, SMS, PR, influencer/affiliate content. Runs the pre-publish compliance handoff so nothing ships unreviewed.
---

# Compliance gate

No outbound asset is "publish-ready" until Compliance Guard has passed it. This is a
hard gate, not a suggestion.

## Steps

1. **Self-check first** so the review is fast. Confirm the asset has, as applicable:
   - Clear sender identity and a working unsubscribe/opt-out (email/SMS).
   - Required disclosures (FTC #ad/#sponsored for influencer/affiliate; testimonials).
   - Substantiation for any health, financial, superlative, or comparative claim.
   - Consent/privacy language for forms, cookies, and data capture (GDPR/CCPA).
   - Platform-policy fit for the destination channel.
2. **Package the review request**: the asset, its channel, its audience, and the
   claims you're making. Save it per the `save-to-knowledge` skill.
3. **Hand off to Compliance Guard** and wait for an explicit pass/fail.
4. **On fail**, apply every required fix and re-submit. Do not ship on a partial pass.
5. **On pass**, note the approval (date + reviewer) alongside the asset before it goes out.

## Note

Compliance Guard maintains its checklists in `06-playbooks/compliance-checklists.md`,
which is read-only in chat — read it to self-check, but let Compliance Guard update it.
