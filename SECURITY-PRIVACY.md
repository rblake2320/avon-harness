# Security & Privacy Posture
*Last updated: June 24, 2026. Re-verify legal landscape quarterly.*
*Engineering documentation, not legal advice. Have counsel review before any production
launch with real customer data.*

Avon Copilot shares the MK Copilot backend, so this posture is identical in substance.
The product stores customer PII, customer photos (skin analysis), and **attributes derived
from those photos** (undertone, Fitzpatrick skin type). In 2026 that derived data is legally
sensitive. This records what the law requires, what we already do, and the gaps to close.

---

## The single biggest liability: derived skin data is "consumer health data"

**Washington's My Health My Data Act (MHMDA, RCW 19.373)** covers data "derived or inferred"
by algorithms from photos. Our `skin_undertone`, `fitzpatrick_type`, and `skin_profile_json`
fall inside that definition. MHMDA:
- Triggers **regardless of whether the person is identified**.
- Requires **separate opt-in consents**: to *collect*, to *share*, and a signed authorization
  to *sell*.
- Carries a **private right of action** (treble damages up to $25K + fees). First class
  action filed Feb 2025.

Nevada and Connecticut have similar consumer-health-data regimes. This is the controlling
constraint for the skin-analysis feature.

### Biometric laws (secondary but real)
- **Illinois BIPA** covers a "scan of face geometry" *only if the person can be identified*
  (*Castelaz v. Estée Lauder*, Jan 2024 — cosmetics face-analysis claim dismissed on this
  ground). Still requires **written opt-in** + a **public retention policy**; $1,000 / $5,000
  per person (per-person cap, SB 2979, Aug 2024).
- **Texas CUBI** — AG-enforced, aggressive post-*Meta* ($1.4B, Jul 2024).
- **Posture: get written opt-in for skin analysis regardless of state.**

### General state privacy laws (~19 in effect by 2026)
CCPA/CPRA, Virginia, Colorado, Texas, Maryland MODPA, plus IN/KY/RI from Jan 2026. All
except CA/UT require **opt-in for sensitive/biometric data**; **Maryland MODPA bans selling
sensitive data even with consent**. As the platform we are a **processor / service provider**
and need **Data Processing Agreements** (VCDPA-model + CCPA §7051 terms) with subcontractor
flow-down to any LLM/vision vendor.

### AI-specific
- AI marketing copy alone needs no disclosure.
- **Chatbots need disclosure** (California SB 243, live Jan 2026) — the chat UI must tell
  users they're talking to AI. (Note: Avon's own Anele assistant is a cautionary example of
  an under-built chatbot; ours must be both compliant and accurate.)
- EU AI Act high-risk delayed to Dec 2027; Colorado AI Act replaced (eff. Jan 2027); Texas
  TRAIGA + California AB 2013 live Jan 2026. None block us today; track them.

### FTC
Income-claim enforcement is live (Air AI banned Mar 2026). Our income-claim filter is the
right call — **doubly important for Avon, which publishes no US Income Disclosure Statement**.
Also: **never train AI on customer photos without renewed consent** (FTC algorithmic
disgorgement risk).

---

## What we already do right

- **Local-first skin analysis.** When `SKIN_ANALYSIS_URL` is set, photos are processed on
  local hardware (PanDerm, port 8101) and **never leave the machine**.
- **EXIF stripping** before any image reaches a provider.
- **Compliance gate** strips all medical/oncology output; only cosmetic dimensions kept.
- **Encryption at rest** for API keys (AES-256-GCM, AAD-bound to `tenant:user:provider`).
- **Multi-tenant isolation** enforced and tested (cross-tenant → 404).
- **Derive-then-keep-attributes** data shape — we store the derived profile, not raw images.

---

## Gaps to close before scaled customer-data handling

Tracked in ROADMAP.md "Now".

1. **Consent capture** — explicit, logged opt-in before skin analysis (MHMDA + BIPA).
2. **AI disclosure in chat UI** (California SB 243).
3. **Raw photo retention enforcement** — process in memory, store derived attributes,
   discard raw image by default; auto-purge any cache on a published schedule (≤ 3 years).
4. **Data deletion + export endpoints** — `DELETE /api/customers/{id}` cascading to derived
   skin data; honor deletion within **45 days** with vendor pass-through.
5. **Published privacy policy + retention schedule** (BIPA requires a public one).
6. **DPAs with any cloud LLM/vision vendor**, subcontractor flow-down.
7. **No-training guarantee** — customer photos never train models without fresh consent.
8. **Per-tenant data-residency option** (local PanDerm enables the strongest version).

---

## Operating rules (do not weaken)

- `SKIN_FORBIDDEN_TERMS` and the post-response compliance check stay. Medical output is
  discarded server-side, never stored.
- The income-claim filter (58 patterns, two-layer) stays — Avon's liability shield given no IDS.
- Local PanDerm is the recommended production config for privacy-sensitive deployments;
  cloud vision is the fallback where customer photos are involved.
- Never quote Avon prices (campaign pricing) — a separate brand rule, but it's also a
  customer-trust safeguard.
- Secrets only in environment / `~/.secrets` (chmod 600). Never inline, never tracked.
