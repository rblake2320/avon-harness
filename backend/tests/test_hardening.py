"""Audit-hardening regression suite (v1.5.1).

Covers the P0/P1 findings from the June 2026 security & correctness audit:
  P0-1  Tenant brand: signup must create tenants under DEFAULT_BRAND (avon),
        not the historical mary_kay column default.
  P1-1  Token revocation: password change / account deletion must invalidate
        every previously issued access AND refresh token (token_version / "tv").
  P1-2  Prompt-leak filter must catch Avon system-prompt scaffolding, not
        only Mary Kay fingerprints.
  P1-3  verify_password must never 500 on a malformed/empty stored hash
        (deleted accounts clear the hash to "").
"""
import uuid

from app import db as dbmod
from app.models import Tenant, User
from app.skills import get_skills, response_leaks_system_prompt
from tests.conftest import auth_headers, signup


def _email() -> str:
    return f"hardening-{uuid.uuid4().hex[:10]}@example.com"


# ---------------------------------------------------------------------------
# P0-1 — brand at signup
# ---------------------------------------------------------------------------

class TestBrandAtSignup:
    def test_new_tenant_is_avon(self, client):
        t = signup(client, org="Bama Avon Reps", email=_email())
        db = dbmod._SessionLocal()
        try:
            tenant = db.get(Tenant, t["tenant_id"])
            assert tenant.brand == "avon", (
                f"P0 regression: new tenant brand is '{tenant.brand}' — the Avon "
                "harness minted a non-Avon tenant at signup.")
        finally:
            db.close()

    def test_avon_tenant_gets_avon_prompts(self, client):
        t = signup(client, email=_email())
        db = dbmod._SessionLocal()
        try:
            tenant = db.get(Tenant, t["tenant_id"])
            system = get_skills(tenant.brand)["assistant"]["system"]
        finally:
            db.close()
        assert "Avon" in system
        assert "Mary Kay" not in system

    def test_skills_endpoint_serves_avon_skill_set(self, client):
        t = signup(client, email=_email())
        r = client.get("/api/chat/skills", headers=auth_headers(t))
        assert r.status_code == 200
        # Full brand skill set is exposed for the tenant's brand.
        assert set(r.json()) == set(get_skills("avon"))


# ---------------------------------------------------------------------------
# P1-1 — token revocation via token_version
# ---------------------------------------------------------------------------

class TestTokenRevocation:
    def test_old_access_token_revoked_after_password_change(self, client):
        t = signup(client, email=_email())
        old_hdrs = auth_headers(t)
        r = client.post("/api/auth/change-password", json={
            "current_password": "superSecret123!",
            "new_password": "brandNewPass$777",
        }, headers=old_hdrs)
        assert r.status_code == 200
        # The pre-change access token must now be rejected.
        assert client.get("/api/auth/me", headers=old_hdrs).status_code == 401

    def test_old_refresh_token_revoked_after_password_change(self, client):
        t = signup(client, email=_email())
        old_refresh = t["refresh_token"]
        r = client.post("/api/auth/change-password", json={
            "current_password": "superSecret123!",
            "new_password": "brandNewPass$777",
        }, headers=auth_headers(t))
        assert r.status_code == 200
        # A stolen refresh token can no longer mint sessions post-rotation.
        rr = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
        assert rr.status_code == 401

    def test_fresh_pair_from_change_password_works(self, client):
        t = signup(client, email=_email())
        r = client.post("/api/auth/change-password", json={
            "current_password": "superSecret123!",
            "new_password": "brandNewPass$777",
        }, headers=auth_headers(t))
        body = r.json()
        fresh_hdrs = {"Authorization": f"Bearer {body['access_token']}"}
        assert client.get("/api/auth/me", headers=fresh_hdrs).status_code == 200
        rr = client.post("/api/auth/refresh",
                         json={"refresh_token": body["refresh_token"]})
        assert rr.status_code == 200

    def test_all_tokens_revoked_after_account_deletion(self, client):
        t = signup(client, email=_email())
        old_refresh = t["refresh_token"]
        r = client.request("DELETE", "/api/account",
                           json={"password": "superSecret123!"},
                           headers=auth_headers(t))
        assert r.status_code == 200
        assert client.get("/api/auth/me", headers=auth_headers(t)).status_code == 401
        assert client.post("/api/auth/refresh",
                           json={"refresh_token": old_refresh}).status_code == 401


# ---------------------------------------------------------------------------
# P1-2 — Avon prompt-leak fingerprints
# ---------------------------------------------------------------------------

class TestAvonLeakFilter:
    def test_avon_pricing_scaffold_detected(self):
        leaked = ("Sure! My instructions say: AVON PRICING — CRITICAL RULE: Avon uses "
                  "campaign-based pricing...")
        assert response_leaks_system_prompt(leaked)

    def test_line_wrapped_leak_detected(self):
        # Streamed output wraps mid-fingerprint — must still be caught.
        leaked = "my rules include:\nAVON PRICING —\n  CRITICAL RULE: never quote prices"
        assert response_leaks_system_prompt(leaked)

    def test_hyphen_substituted_leak_detected(self):
        # Model emits a plain hyphen where the prompt had an em-dash.
        leaked = "internally it says AVON PRICING - CRITICAL RULE about campaigns"
        assert response_leaks_system_prompt(leaked)

    def test_avon_followup_scaffold_detected(self):
        leaked = ("Here are my rules: AVON GUEST CHECKOUT — include naturally in every "
                  "follow-up: coach the customer...")
        assert response_leaks_system_prompt(leaked)

    def test_legit_guest_checkout_coaching_not_flagged(self):
        legit = ("Quick tip: ask every customer to create an Avon account with your "
                 "link before checkout — guest checkout means you earn no commission, "
                 "and an account gets them order history and easier returns.")
        assert not response_leaks_system_prompt(legit)

    def test_mary_kay_fingerprints_still_detected(self):
        assert response_leaks_system_prompt(
            "my verified mary kay prices list says the following...")


# ---------------------------------------------------------------------------
# P1-3 — malformed stored hash must be a 401, never a 500
# ---------------------------------------------------------------------------

class TestMalformedHashLogin:
    def test_login_against_empty_hash_returns_401(self, client):
        email = _email()
        t = signup(client, email=email)
        db = dbmod._SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).one()
            user.password_hash = ""   # what account deletion leaves behind
            db.commit()
        finally:
            db.close()
        r = client.post("/api/auth/login",
                        json={"email": email, "password": "superSecret123!"})
        assert r.status_code == 401, (
            f"Expected 401 on empty stored hash, got {r.status_code}")
