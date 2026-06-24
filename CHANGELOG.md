# Changelog

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
