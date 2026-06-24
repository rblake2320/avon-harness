# CLAUDE.md — avon-harness

Project-specific instructions for Claude Code working in this repository.

## Project overview

**Avon Copilot** is a model-agnostic AI harness for Avon Representatives with
The Avon Company (US entity, owned by LG H&H).

Built on the same architecture as MK Harness — the entire backend, auth, CRM,
providers, compliance filter, and skin analysis is shared. Only the brand config
differs (`backend/app/brands/avon.py`).

**Target users:** US Avon reps — NOT Avon International (sold to Regent LP Dec 2025).

Stack: FastAPI backend · React/Vite web · Expo React Native mobile · shared TypeScript SDK.

Key invariant: **the rest of the application never names a provider**. All LLM traffic flows
through `backend/app/providers/` only.

---

## Avon-Specific Rules

1. **Never quote prices.** Avon uses campaign-based pricing (new brochure every ~2 weeks).
   The brand config enforces this, but never add specific prices to `avon.py`.

2. **No income disclosure statement.** Avon does not publish an official US IDS.
   The compliance guidance in `avon.py` handles this — do not add IDS references.

3. **Guest checkout warning.** The #1 Avon rep complaint — guest checkout loses commission.
   The brand config instructs the AI to always surface this when follow-up topics come up.

4. **US entity only.** The Avon Company (LG H&H). Do not reference Avon International,
   Natura&Co's Avon, or any non-US entity. These are different companies.

5. **Anew is the flagship.** Anew skincare > Skin So Soft (iconic, #1 Bug Guard) >
   Avon Color > Fragrances. Skin So Soft Bug Guard is the highest-volume product seasonally.

---

## Common commands

### Backend
```bash
cd backend
pip install -r requirements.txt

# Dev server
MK_ALLOW_DEV_SECRETS=1 \
JWT_SECRET=dev-secret-dev-secret-dev-secret-123 \
MASTER_KEY=$(python3 -c "import os,base64;print(base64.b64encode(os.urandom(32)).decode())") \
uvicorn app.main:app --reload --port 8200

# Tests
python -m pytest -v
```

### Web
```bash
cd web && npm install && npm run dev   # http://localhost:5173
```

---

## Architecture

Identical to MK Harness. Brand config in `backend/app/brands/avon.py`.
All skills (assistant, product_qa, sales_coach, follow_up, party_planner, social)
are built dynamically from the Avon brand config via `get_skills("avon")`.

**Adding a new brand from here:**
1. Create `backend/app/brands/<brand>.py` with a `BrandConfig` instance.
2. Register in `backend/app/brands/registry.py`.
3. Set `Tenant.brand = "<brand>"` at signup.
4. Done — all routes, compliance, CRM, and skin analysis work immediately.

---

## Environment variables

Same as MK Harness, plus:

| Variable | Notes |
|----------|-------|
| `DEFAULT_BRAND` | Set to `avon` — already default in config.py |
| `SKIN_ANALYSIS_URL` | `http://localhost:8101` if local PanDerm is running |

---

## Testing

Run `python -m pytest -v` — all 45 tests must pass.
The test suite uses `avon` brand config for brand-related tests (update conftest
`DEFAULT_BRAND` env var if needed for brand-specific test cases).

---

## Skin analysis — compliance guardrails (do not weaken)

Same rules as MK Harness. Anew skincare maps well to the cosmetic-only observation
categories. Skin So Soft products map to body care / hydration recommendations.
The `see_professional` flag is the only exit for ambiguous clinical findings.
