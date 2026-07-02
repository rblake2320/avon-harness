#!/bin/bash
# Live smoke walkthrough — boots the REAL server against REAL Redis and an on-disk
# SQLite DB and drives it over real HTTP. No TestClient, no mocks, no fixtures.
#
# Run from repo root in a DISPOSABLE environment (flushes the local Redis instance):
#   ./scripts/live_smoke.sh
#
# Covers: privacy-page accuracy, brand-at-signup (P0 regression), full token
# revocation lifecycle, Redis-backed brute-force lockout + rate limiting, the
# consent gate with a real JPEG upload, deleted-account login (the former 500),
# and the Redis-unreachable loud-fallback path.
#
# With ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY exported, section 6's
# post-consent analyze exercises the full provider pipeline instead of the clean
# no-key 502; chat streaming can then be smoke-tested manually against :8200.
set -u
PY="${PYTHON:-python3}"
UV="${UVICORN:-uvicorn}"
B=http://localhost:8200
pass=0; fail=0
ck() { # ck <label> <expected> <actual>
  if [ "$2" = "$3" ]; then echo "PASS  $1"; pass=$((pass+1));
  else echo "FAIL  $1 (expected=$2 actual=$3)"; fail=$((fail+1)); fi
}

sq() { $PY -c "import sqlite3;r=sqlite3.connect('/tmp/avon_live.db').execute(\"$1\").fetchone();print(r[0] if r else '')"; }
sqx() { $PY -c "import sqlite3;c=sqlite3.connect('/tmp/avon_live.db');c.execute(\"$1\");c.commit()"; }

redis-cli ping >/dev/null 2>&1 || redis-server --daemonize yes --port 6379 --dir /tmp
redis-cli flushall >/dev/null

cd "$(dirname "$0")/../backend"
rm -f /tmp/avon_live.db
export JWT_SECRET="live-walkthrough-secret-0123456789abcdef"
export MASTER_KEY=$($PY -c "import os,base64;print(base64.b64encode(os.urandom(32)).decode())")
export DATABASE_URL="sqlite:////tmp/avon_live.db"
export REDIS_URL="redis://localhost:6379/0"
export RATE_LIMIT_PER_MINUTE=5
$UV app.main:app --port 8200 --log-level warning > /tmp/uvicorn.log 2>&1 &
SRV=$!
for i in $(seq 1 30); do curl -s -m 1 $B/api/health >/dev/null 2>&1 && break; sleep 0.5; done

echo "== 1. Health & privacy page (served text must reflect real implementation) =="
ck "health" '{"status":"ok"}' "$(curl -s $B/api/health)"
ck "privacy states argon2id" "argon2id" "$(curl -s $B/privacy | grep -o 'argon2id' | head -1)"
ck "privacy no bcrypt claim" "" "$(curl -s $B/privacy | grep -o 'bcrypt')"
ck "privacy no HttpOnly-cookie claim" "" "$(curl -s $B/privacy | grep -o 'HttpOnly')"

echo "== 2. Signup over the wire -> brand verified in the REAL on-disk DB =="
SIGNUP=$(curl -s -X POST $B/api/auth/signup -H 'Content-Type: application/json' \
  -d '{"org_name":"Live Walkthrough Org","email":"ron@livewalk.com","password":"realPassword#2026"}')
ACCESS=$(echo "$SIGNUP" | $PY -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
REFRESH=$(echo "$SIGNUP" | $PY -c "import sys,json;print(json.load(sys.stdin)['refresh_token'])")
TID=$(echo "$SIGNUP" | $PY -c "import sys,json;print(json.load(sys.stdin)['tenant_id'])")
BRAND=$(sq "SELECT brand FROM tenants WHERE id='$TID'")
ck "P0: tenant brand in real DB" "avon" "$BRAND"

echo "== 3. Auth lifecycle over real HTTP =="
ck "GET /me with access token" "200" "$(curl -s -o /dev/null -w '%{http_code}' $B/api/auth/me -H "Authorization: Bearer $ACCESS")"
ck "refresh works pre-change" "200" "$(curl -s -o /dev/null -w '%{http_code}' -X POST $B/api/auth/refresh -H 'Content-Type: application/json' -d "{\"refresh_token\":\"$REFRESH\"}")"

CHG=$(curl -s -X POST $B/api/auth/change-password -H "Authorization: Bearer $ACCESS" \
  -H 'Content-Type: application/json' \
  -d '{"current_password":"realPassword#2026","new_password":"rotatedPassword#2026"}')
NEW_ACCESS=$(echo "$CHG" | $PY -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
ck "P1: OLD access token revoked" "401" "$(curl -s -o /dev/null -w '%{http_code}' $B/api/auth/me -H "Authorization: Bearer $ACCESS")"
ck "P1: OLD refresh token revoked" "401" "$(curl -s -o /dev/null -w '%{http_code}' -X POST $B/api/auth/refresh -H 'Content-Type: application/json' -d "{\"refresh_token\":\"$REFRESH\"}")"
ck "fresh token from change-password works" "200" "$(curl -s -o /dev/null -w '%{http_code}' $B/api/auth/me -H "Authorization: Bearer $NEW_ACCESS")"
TV=$(sq "SELECT token_version FROM users WHERE email='ron@livewalk.com'")
ck "token_version bumped in real DB" "1" "$TV"

echo "== 4. Brute-force lockout backed by REAL Redis =="
for i in 1 2 3 4 5; do
  curl -s -o /dev/null -X POST $B/api/auth/login -H 'Content-Type: application/json' \
    -d '{"email":"ron@livewalk.com","password":"wrong-guess-'$i'"}'
done
ck "6th attempt locked out (429)" "429" "$(curl -s -o /dev/null -w '%{http_code}' -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"email":"ron@livewalk.com","password":"rotatedPassword#2026"}')"
ck "lockout counter lives in Redis" "5" "$(redis-cli get 'bf:ron@livewalk.com')"
redis-cli del 'bf:ron@livewalk.com' >/dev/null
ck "correct login after Redis key cleared" "200" "$(curl -s -o /dev/null -w '%{http_code}' -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"email":"ron@livewalk.com","password":"rotatedPassword#2026"}')"

echo "== 5. Rate limiting backed by REAL Redis (limit=5/min) =="
CODES=""
for i in 1 2 3 4 5 6 7; do
  CODES="$CODES $(curl -s -o /dev/null -w '%{http_code}' -X POST $B/api/chat/stream \
    -H "Authorization: Bearer $NEW_ACCESS" -H 'Content-Type: application/json' \
    -d '{"message":"hi","skill":"nonexistent_skill"}')"
done
echo "   codes:$CODES"
ck "rate limiter returns 429 within burst" "429" "$(echo $CODES | tr ' ' '\n' | grep -m1 429)"
ck "rate-limit zset exists in Redis" "1" "$(redis-cli --scan --pattern 'rl:*' | wc -l | tr -d ' ')"

# Section 5 exhausted this user's 5/min rate budget — correct behavior. Expire the
# sliding window (equivalent to waiting 60s) so section 6 tests consent, not the limiter.
for k in $(redis-cli --scan --pattern 'rl:*'); do redis-cli del "$k" >/dev/null; done

echo "== 6. Consent gate blocks skin analysis BEFORE any processing (real JPEG upload) =="
$PY -c "from PIL import Image; Image.new('RGB',(640,480),(180,140,120)).save('/tmp/face.jpg','JPEG')"
R6=$(curl -s -w '\n%{http_code}' -X POST $B/api/skin/analyze -H "Authorization: Bearer $NEW_ACCESS" -F "file=@/tmp/face.jpg")
ck "analyze without consent -> 403" "403" "$(echo "$R6" | tail -1)"
ck "machine-readable consent code" "operator_consent_required" "$(echo "$R6" | head -1 | $PY -c "import sys,json;print(json.load(sys.stdin)['detail']['code'])")"

curl -s -o /dev/null -X POST $B/api/consent/skin -H "Authorization: Bearer $NEW_ACCESS" \
  -H 'Content-Type: application/json' -d '{"subject":"operator","accepted":true}'
for k in $(redis-cli --scan --pattern 'rl:*'); do redis-cli del "$k" >/dev/null; done
R6B=$(curl -s -w '\n%{http_code}' -X POST $B/api/skin/analyze -H "Authorization: Bearer $NEW_ACCESS" -F "file=@/tmp/face.jpg")
# With consent granted and no provider keys configured, the pipeline runs for real up to
# the provider boundary and must fail CLEANLY (502), never 500.
ck "post-consent, no provider keys -> clean 502 (not 500)" "502" "$(echo "$R6B" | tail -1)"
CONSENT_HASH=$(sq "SELECT length(text_sha256) FROM consent_records LIMIT 1")
ck "consent text hash persisted (sha256 len)" "64" "$CONSENT_HASH"

echo "== 7. Deleted-account login: the former 500 path, over the wire =="
DEL=$(curl -s -X POST $B/api/auth/signup -H 'Content-Type: application/json' \
  -d '{"org_name":"Delete Me Org","email":"deleteme@livewalk.com","password":"realPassword#2026"}')
DEL_ACCESS=$(echo "$DEL" | $PY -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
ck "account deletion succeeds" "200" "$(curl -s -o /dev/null -w '%{http_code}' -X DELETE $B/api/account -H "Authorization: Bearer $DEL_ACCESS" -H 'Content-Type: application/json' -d '{"password":"realPassword#2026"}')"
sqx "UPDATE users SET email='deleteme@livewalk.com' WHERE email LIKE 'deleted_%@deleted'"
ck "P1: login vs empty hash -> 401 not 500" "401" "$(curl -s -o /dev/null -w '%{http_code}' -X POST $B/api/auth/login -H 'Content-Type: application/json' -d '{"email":"deleteme@livewalk.com","password":"realPassword#2026"}')"

echo "== 8. Redis-unreachable scenario: loud ERROR + graceful fallback =="
kill $SRV 2>/dev/null; sleep 1
REDIS_URL="redis://localhost:9999/0" $UV app.main:app --port 8201 --log-level warning > /tmp/uvicorn2.log 2>&1 &
SRV2=$!
for i in $(seq 1 30); do curl -s -m 1 $B:1/api/health >/dev/null 2>&1 && break; curl -s -m 1 http://localhost:8201/api/health >/dev/null 2>&1 && break; sleep 0.5; done
curl -s -o /dev/null -X POST http://localhost:8201/api/auth/login -H 'Content-Type: application/json' -d '{"email":"x@ywalk.com","password":"whatever123"}'
ck "app still serves with Redis down" '{"status":"ok"}' "$(curl -s http://localhost:8201/api/health)"
ck "loud ERROR logged on configured-but-dead Redis" "1" "$(grep -c 'REDIS_URL is set but Redis is unusable' /tmp/uvicorn2.log)"
kill $SRV2 2>/dev/null

echo
echo "=================================================="
echo "LIVE WALKTHROUGH: $pass passed, $fail failed"
echo "=================================================="
exit $fail
