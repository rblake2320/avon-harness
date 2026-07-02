# Changelog

## 1.5.1 — 2026-07-01 (security & correctness audit)

### Fixed (P0)
- **Brand at signup**: every new tenant was created with `brand="mary_kay"` (the
  model column default); `DEFAULT_BRAND=avon` was never applied. New tenants on
  this harness received Mary Kay system prompts, price rules, and compliance
  patterns. Signup now sets `Tenant.brand` from server config (validated against
  the brand registry), the column default follows config, and the hardcoded
  `"mary_kay"` fallbacks in chat/customers routes now follow config too.
  Remediation for existing dev/staging data: `UPDATE tenants SET brand='avon';`

### Fixed (P1)
- **Token revocation**: password change and account deletion now revoke ALL
  previously issued access and refresh tokens via a `token_version` ("tv") claim.
  Previously a stolen refresh token survived a password change for up to 14 days.
  `POST /api/auth/change-password` now additionally returns a fresh
  `access_token` + `refresh_token` pair (additive; `ok: true` unchanged).
  Migration for existing DBs:
  `ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0;`
- **Prompt-leak filter was Mary Kay-only**: added Avon system-prompt fingerprints
  (pricing rule scaffold, compensation block header, follow-up coaching scaffold),
  chosen to avoid false positives on legitimate guest-checkout coaching.
- **`redis` was imported but undeclared**: added `redis==6.2.0` to requirements.
  With `REDIS_URL` set and the package missing, rate limiting and brute-force
  lockout silently degraded to per-process state (not multi-replica safe).
  The fallback also now logs an ERROR instead of being silent.
- **500 on malformed stored password hash**: `verify_password` now returns False
  on `InvalidHashError`/`VerificationError` (account deletion clears the hash to
  `""`; a login attempt against such a row previously raised an unhandled 500).
- **Privacy policy corrected to match implementation**: argon2id (not bcrypt),
  bearer-token auth (no HttpOnly session cookie exists).

### Hardened post-review (durability pass)
- **Leak-filter evasion resistance**: fingerprint matching now normalizes dash
  variants (em/en/minus → hyphen) and collapses whitespace on BOTH sides, so a
  prompt leaked with line-wraps or hyphen substitution ("AVON PRICING -\nCRITICAL
  RULE") is still caught. Regression tests included for both evasion vectors.
- **`scripts/live_smoke.sh`**: full end-to-end walkthrough against a REAL running
  server + REAL Redis + on-disk DB over real HTTP — no TestClient, no mocks.
  Verified 24/24 in this audit: brand-at-signup in the actual DB file, complete
  token-revocation lifecycle over the wire, Redis-backed lockout and rate limiting
  (counters inspected in Redis itself), consent gate with a real JPEG upload,
  deleted-account login, and the Redis-down loud-fallback (ERROR log confirmed).

### Tests
- 78 → 92: new `tests/test_hardening.py` regression suite covering all of the
  above (brand-at-signup, token revocation across access/refresh/deletion, Avon
  leak fingerprints + false-positive guard, malformed-hash login).

### Docs
- README badge/repo references pointed at `mk-harness`; now `avon-harness`.
- Stale "59 tests" counts updated in README and CLAUDE.md.


All notable changes to Avon Copilot are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

`VERSION` at the repo root is the single source of truth for the current version.
Keep `backend/app/main.py`, `web/package.json`, and `mobile/app.json` in sync with it.

Avon Copilot is built on the same proven backend as MK Copilot — only the brand config
differs. Backend/auth/CRM/provider/compliance changes are shared lineage with that repo.

---

## [Unreleased]

### Planned
See `ROADMAP.md`.

---

## [1.3.0] — 2026-06-25

Web client — first real, demo-able pass (shared with MK Copilot 1.4.0). The React/Vite
app now compiles and builds. Brand behavior stays server-side; the web shell uses the
neutral "Consultant Studio" platform brand.

### Added
- **SDK extended** to match the backend: `signup({ref})`, consent, billing, skin-data
  export/delete, suggestions, structured `ApiError` (status + `detail.code`).
- **SB 243 AI disclosure** — once-per-session modal, persistent strip, per-output `AI`
  badge; server `ai_disclosure` rendered in skin results.
- **Billing view** — annual-first plans, Stripe Checkout hand-off, portal link, shareable
  referral link with earned-credit display.
- **Referral capture** (`?ref=`), **consent-gated skin analysis** (403-code-driven modal),
  **Power Hour** daily suggestions with one-click AI follow-up. Mobile-responsive.

### Verified
- `tsc -b --noEmit` clean; `vite build` succeeds.

---

## [1.2.0] — 2026-06-24

Revenue infrastructure (shared with MK Copilot 1.3.0). Stripe billing, annual-first,
90-day trial, referral flywheel.

### Added
- **Stripe billing via REST (`app/billing.py`)** — httpx, no SDK; HMAC-SHA256 webhook
  verification.
- **Billing routes**: `POST /api/billing/checkout`, `GET /api/billing/me`,
  `GET /api/billing/plans`, `POST /api/billing/portal`, `POST /api/billing/webhook`.
- **Subscription model** mirroring Stripe state, webhook-driven.
- **Referral program** — `referral_code` per user, signup `?ref=`, $5 credit on the
  referred user's first paid invoice (`ReferralCredit`, idempotent).
- **Entitlement gate (`app/entitlements.py`)** — off until `BILLING_ENFORCED=1`.
- **Config** — `STRIPE_SECRET_KEY/WEBHOOK_SECRET/PRICES`, `BILLING_*`, `REFERRAL_CREDIT_CENTS`.
  Avon tiers: solo / leader / studio. All from env.

### Tests
- 52 → 59. Same billing coverage as MK (plans test asserts Avon's `leader` tier).

---

## [1.1.0] — 2026-06-24

Customer skin-data privacy core (shared with MK Copilot 1.2.0). Closes the launch-blocking
gaps from `SECURITY-PRIVACY.md`, driven by Washington's My Health My Data Act private right
of action over derived skin attributes.

### Added
- **Consent capture** — `ConsentRecord` model + `app/consent.py`; `POST/GET/DELETE
  /api/consent/skin` for operator and per-customer consent (versioned, SHA-256 integrity
  hash, mirrored to `AuditLog`).
- **Consent gate on skin analysis** — `require_skin_consent()` blocks before the photo is
  read; `403` with `operator_consent_required` / `customer_consent_required`.
- **AI disclosure** — persistent `ai_disclosure` on every skin response + history row.
- **Subject-rights endpoints** — `GET /api/me/skin-data/export` (access/portability) and
  `DELETE /api/me/skin-data` (purge + deletion receipt; optional `?customer_id=`).

### Changed
- **Photo retention made explicit** — raw + sanitized image buffers `del`-eted after use;
  `AuditLog` `skin.analyze` records `photo_discarded=1`. No raw image ever persisted.

### Tests
- 46 → 52. New: consent gate, status/grant/revoke flow, export, deletion, isolation.

---

## [1.0.0] — 2026-06-24

Initial Avon Copilot release. Forks the proven MK Copilot 1.1.0 backend (brand-agnostic
architecture, Power Hour, consultant analytics, local PanDerm, 58-pattern FTC filter)
and adds a verified-current Avon brand configuration.

### Added
- **Avon brand config** (`backend/app/brands/avon.py`) — set as the default brand.
  Verified current to June 2026:
  - **Never quotes prices** — Avon uses campaign-based pricing (new brochure every ~2
    weeks). The AI always directs reps to the current campaign brochure.
  - **Exact commission tiers** (per-campaign, Beauty & Jewelry): 20% ($40–$119),
    30% ($120–$349), 40% ($350–$1,499), 45% ($1,500–$6,499), 50% ($6,500+).
    Fashion/Home caps at 25%. $40 floor = zero below it. 3 campaigns inactive =
    automatic deactivation.
  - **Guest checkout coaching** — the #1 documented rep revenue leak; the AI surfaces it
    on customer follow-ups.
  - **Anew flagship** product line knowledge (Ultimate, Vitamin C, Clinical, Platinum,
    Reversalist), Skin So Soft / Bug Guard seasonal lead, AVON CHI ESSENTIALS haircare
    (launched late 2025).
  - **No US Income Disclosure Statement** — Avon publishes none; compliance guidance
    handles income framing through the universal FTC filter plus Avon-specific patterns.
- **STRATEGY.md** — Avon-specific go-to-market. Lead tactic: the "Anele is broken"
  opening (Avon's own in-app AI assistant, v3.1.3 March 2026, 3.96/5 from 26K reviews,
  documented as arguing with users — a confirmed unmet-need signal).
- Inherited from MK 1.1.0: Power Hour suggestions, ConsultantProfile analytics, skin
  profile in CRM, local PanDerm integration, brand-agnostic skill builder.

### Entity accuracy (verified June 2026)
- Targets **The Avon Company** (US/Canada/PR, owned by LG H&H) — operationally stable,
  North America +35% Q1 2026, new CEO Lee Sun-ju (ex-L'Oréal, Sept 2025).
- **Avon Products Inc.** (the bankrupt parent) resolved via **liquidation trust effective
  Oct 7, 2025** — no longer a business; US entity was never part of it.
- **Avon International** sold to Regent LP for £1 (Dec 31, 2025); **Avon Russia** sold to
  Arnest Group (Feb 2026); **Avon Latin America** retained by Natura. The brand config
  references only the US entity.

### Tests
- 46 tests passing. Brand tests assert Avon as the default with Mary Kay still registered
  as a fallback brand.
