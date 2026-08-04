---
id: EV-15
brief: Can you fix the bug in our billing service?
expect_owner: marketing-director
expect_flags: []
---

**Fallback case.** Nothing in `routing.json` matches, so it lands with the Marketing
Director — whose correct answer is "this isn't marketing work, here's who should own
it", not an attempt to absorb it. Tests that the router degrades sensibly instead of
force-fitting an owner.
