---
name: community-plan
description: Use when asked to start, grow or run a community — Discord/Slack/forum strategy, engagement calendars, moderation guidelines, UGC or ambassador programs. Produces a plan with rituals, rules and health metrics rather than a channel list.
---

# Community plan

Communities die of silence, not of bad design. Plan the recurring rituals first —
everything else is infrastructure around them.

## Inputs

- `01-brand/personas/` — who this community is actually for
- `00-org/ORG.md` §9 — standing constraints and what we don't discuss
- `06-playbooks/community-playbook.md` — existing strategy, if any

## Steps

1. **Answer why members show up** before choosing a platform. Peer access? Early
   information? Status? Help? A community with no member-side reason is a support
   queue with a nicer name.
2. **Choose one platform** and say what you're giving up. Discord for real-time and
   younger audiences; Slack for B2B practitioners; a forum for searchable, durable
   answers; a subreddit only if you can accept losing control.
3. **Design the structure minimally.** Three to five channels at launch. Every empty
   channel is a signal that nobody's here. Add channels when a conversation outgrows
   its home, never in anticipation.
4. **Define the rituals** — this is the plan. Weekly thread, monthly AMA, member
   spotlight, release notes with discussion. Each ritual gets an owner, a cadence, and
   a fallback if turnout is low.
5. **Write moderation guidelines before you need them:** the rules in plain language,
   the escalation ladder (warn → mute → remove), who decides, and the appeals path.
   Publish them where members can read them.
6. **Plan the first 30 days honestly.** Seed conversations, invite a founding cohort
   personally, and make sure someone answers every post within hours. Empty is fatal.
7. **Design the UGC and ambassador layer** only once there's activity to build on:
   prompts, usage rights, amplification path; tiers, perks, and explicit expectations.
8. **Set health metrics** that mean something: percentage of members who post,
   member-to-member reply ratio, time-to-first-response, retention by cohort. Member
   count is a vanity number and a poor target.

## Output contract

Draft to `07-agent-outputs/` → promoted to `06-playbooks/community-playbook.md`;
calendars go to `03-campaigns/community/`.

```markdown
---
title: Community plan — <name>
profile: community-manager
status: draft
summary: <platform> community for <audience>, <n> rituals.
---

# Community plan

**Why members show up** · **Platform + trade-off** · **Audience**

## Structure
| Channel | Purpose | Who posts |

## Rituals
| Ritual | Cadence | Owner | Format | Low-turnout fallback |

## Moderation
Rules (plain language) · escalation ladder · decision owner · appeals

## First 30 days
Week-by-week seeding plan and the founding cohort.

## UGC & ambassadors
Prompts · rights · amplification · tiers · perks · expectations

## Health metrics
| Metric | Definition | Target | Review cadence |
```

## Quality bar

- [ ] The member-side reason to show up is stated, not assumed
- [ ] One platform chosen, with the trade-off named
- [ ] ≤5 channels at launch
- [ ] Every ritual has an owner, a cadence and a low-turnout fallback
- [ ] Moderation rules written in plain language with an appeals path
- [ ] Health metrics are engagement-based; member count is not a target

## Hand-offs

- **Social Organic** — recruitment content
- **Reputation Manager** — sentiment overlap with public reviews
- **Compliance Guard** — UGC usage rights and ambassador disclosure
