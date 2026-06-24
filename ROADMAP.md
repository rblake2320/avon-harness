# Avon Copilot — Product Roadmap
*Last updated: June 24, 2026. Living document — reorder by what the data says.*

Priorities are driven by STRATEGY.md (the "Anele is broken" opening, seasonal Bug Guard
acquisition, Leader-tier leverage) and by `ConsultantProfile` analytics once reps are on.

---

## Now (next release — 1.1.0)

- [ ] **Guest-checkout reminder automation.** Surface the guest-checkout commission-loss
      warning proactively in every customer follow-up draft — this is Avon's #1 documented
      revenue leak and our most concrete "we made you money" hook.
- [ ] **Campaign-aware coaching.** The sales coach skill calculates "you need $X more this
      campaign to hit the next commission tier (or the $40 floor)." Requires a lightweight
      per-rep campaign-total input. No other tool does this.
- [ ] **Billing & subscription tiers.** Stripe — Solo / Leader / Studio. Annual default.
      Bundle discount for reps who also run MK Copilot.
- [ ] **Data deletion / export endpoints** + photo retention enforcement
      (see SECURITY-PRIVACY.md). Required before scaled customer-data handling.
- [ ] **Usage-metering dashboard.** Token cost per rep/team, visible to tenant admins.
- [ ] **Redis rate limiting.** Swap in-process store (`ratelimit.py`) for multi-replica.
- [ ] **Mobile device test.** Expo EAS, real iOS + Android — camera skin flow never run on device.

> See `MONSTER-MOVE.md` for the scale-up/exit thesis and 90-day sprint. Two items there
> (repo merge, provisional patent) are **open decisions** — not scheduled work.

## Next (1.2.0 – 1.3.0)

- [ ] **"Anele replacement" landing content + SEO.** The growth engine from STRATEGY
      Phase 1 — capture reps searching "Avon AI app not working." Honest comparison, not
      attack. This is a content/marketing deliverable tracked in the repo.
- [ ] **Bug Guard seasonal onboarding flow.** Pre-built spring-campaign content (Bug Guard
      social posts, outdoor-lifestyle customer templates, Skin So Soft skin-analysis
      prompt) so a new spring rep gets immediate value before the paywall.
- [ ] **Leader dashboard.** Team analytics for the Leader tier — downline activity,
      skill usage, aggregate compliance health. Drives Leader-led distribution.
- [ ] **Live-selling assistant.** Real-time support for TikTok/Instagram Live — Avon
      product talking points, objection handling, on-the-fly compliance (see TRENDS.md).

## Later (1.4.0+)

- [ ] **Enterprise path to LG H&H.** At scale, package the data moat (anonymized rep
      question patterns, compliance health, skin-profile distribution) into a pitch to
      The Avon Company to license Avon Copilot as the official replacement for Anele.
- [ ] **Cross-brand model improvements.** Avon + MK skin-analysis data trains a better
      shared recommendation model than either brand alone (the network effect).
- [ ] **AvonNow read-only integration** *only if* an official API appears. Never build
      against scraped/unofficial endpoints — blocked until official.

---

## Explicitly Not Doing (and why)

- **Accounting/tax/inventory.** Direct Sidekick owns the Avon accounting niche. Not our lane.
- **Order management.** AvonNow is not accessible to us; we don't replicate ordering.
- **Quoting prices.** Campaign pricing changes every ~2 weeks. Quoting any price is wrong
  by design — this is a permanent product rule, not a missing feature.
- **Fixing guest checkout at the platform level.** We can't change Avon's checkout; we
  coach reps to address it. Boundary held.
- **Income projections.** Any predicted-earnings feature is an FTC income claim. Never.
- **Referencing Avon International / Natura / Regent entities.** US entity (LG H&H) only.

---

## Versioning Discipline

- `VERSION` at repo root is the source of truth. Bump it, then sync `main.py`,
  `web/package.json`, `mobile/app.json`.
- Tag every release: `git tag -a v1.1.0 -m "..."` and push tags.
- Every release gets a CHANGELOG.md entry before the tag.
- **Re-verify Avon facts every quarter.** The brand config header carries a "Last
  verified" date. Avon's corporate situation is in flux (Regent strategy, $25M Natura
  credit line expires Dec 2026) — stale facts are worse than no facts.
