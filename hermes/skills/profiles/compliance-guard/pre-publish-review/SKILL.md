---
name: pre-publish-review
description: Use to review an outbound asset for legal and platform compliance before it ships. Produces a pass/fail report with line-level flags and required fixes. This is the gate other profiles hand off to.
---

# Pre-publish compliance review

Return a clear **PASS** or **FAIL** with specific, actionable flags. Never a vague
"looks fine."

## Steps

1. **Identify** the asset type, destination channel, and audience/region — the rules
   depend on all three.
2. **Run the checklist** for that asset (maintained in
   `06-playbooks/compliance-checklists.md`, read-only — read it to review):
   - **Email/SMS** — sender identity, functioning opt-out, consent basis
     (CAN-SPAM / GDPR / TCPA), quiet hours where relevant.
   - **Ads** — platform restricted-content and prohibited-claim rules.
   - **Influencer/affiliate/testimonial** — clear FTC disclosure (#ad/#sponsored),
     material-connection statements.
   - **Claims** — flag any health, financial, superlative, or comparative claim that
     lacks substantiation; require evidence or a rewrite.
   - **Data/privacy** — form, cookie, and consent language for GDPR/CCPA.
3. **Report**, line by line: quote the offending text, name the rule, give the required
   fix. Mark severity (blocker vs. advisory).
4. **Verdict**: PASS only if there are zero blockers. Otherwise FAIL with the fix list.
5. **Log** the review as an audit trail entry (date, asset, verdict).

## Notes

- Draft any checklist improvements to `07-agent-outputs/` and hand to the Marketing
  Director to promote into `06-playbooks/` — that folder is read-only in chat.
- When in doubt, fail closed and escalate to a human.
