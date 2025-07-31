#!/bin/bash
# test_brain.sh - Automated test for /brainstorm API (multi-user isolation, CRUD)
set -e

API=http://localhost:8080
REG_API="$API/api/register/"
LOGIN_API="$API/api/login/"
BRAIN_API="$API/brainstorm"


# Register & login User A
echo "🛠️  Registering User A"
curl -s -X POST $REG_API -H "Content-Type: application/json" \
    -d '{"username":"user_a","email":"user_a@test.com","password":"123456"}' >/dev/null

echo "🛠️  Logging in User A"
login_a=$(curl -s -X POST $LOGIN_API -H "Content-Type: application/json" \
    -d '{"email":"user_a@test.com","password":"123456"}')
token_a=$(echo $login_a | jq -r '.data.access_token // empty')
echo "→ Token A: $token_a"

# Register & login User B
echo "🛠️  Registering User B"
curl -s -X POST $REG_API -H "Content-Type: application/json" \
    -d '{"username":"user_b","email":"user_b@test.com","password":"654321"}' >/dev/null

echo "🛠️  Logging in User B"
login_b=$(curl -s -X POST $LOGIN_API -H "Content-Type: application/json" \
    -d '{"email":"user_b@test.com","password":"654321"}')
token_b=$(echo $login_b | jq -r '.data.access_token // empty')
echo "→ Token B: $token_b"

# User A creates a brainstorm entry
echo "✏️  User A saves a brainstorm entry"
save_a=$(curl -s -X POST "$BRAIN_API/save" \
    -H "Authorization: Bearer $token_a" -H "Content-Type: application/json" \
    -d '{"fiveW": {"why":"a_why","what":"a_what","where":"a_where","when":"a_when","who":"a_who"}}')
id_a=$(echo $save_a | jq -r '.id')
echo "→ Entry ID for User A: $id_a"

# User B creates a brainstorm entry
echo "✏️  User B saves a brainstorm entry"
save_b=$(curl -s -X POST "$BRAIN_API/save" \
    -H "Authorization: Bearer $token_b" -H "Content-Type: application/json" \
    -d '{"fiveW": {"why":"b_why","what":"b_what","where":"b_where","when":"b_when","who":"b_who"}}')
id_b=$(echo $save_b | jq -r '.id')
echo "→ Entry ID for User B: $id_b"

# User A gets their brainstorm list
echo "📦  User A GET /brainstorm/"
get_a=$(curl -s -X GET "$BRAIN_API/" \
    -H "Authorization: Bearer $token_a")
echo "User A data: $get_a"

# User B gets their brainstorm list
echo "📦  User B GET /brainstorm/"
get_b=$(curl -s -X GET "$BRAIN_API/" \
    -H "Authorization: Bearer $token_b")
echo "User B data: $get_b"

echo "🔍  Validating data isolation: each user should see only their own data"
if echo "$get_a" | grep -q b_why; then
    echo "❌ User A can see User B's data! Isolation failed."
else
    echo "✅ User A only sees their own data."
fi
if echo "$get_b" | grep -q a_why; then
    echo "❌ User B can see User A's data! Isolation failed."
else
    echo "✅ User B only sees their own data."
fi

# User A updates their entry
echo "🔄  User A updates their own entry"
curl -s -X PUT "$BRAIN_API/$id_a" \
    -H "Authorization: Bearer $token_a" -H "Content-Type: application/json" \
    -d '{"why":"a_why_updated"}' | jq

# User B deletes their own entry
echo "🗑️  User B deletes their own entry"
curl -s -X DELETE "$BRAIN_API/$id_b" \
    -H "Authorization: Bearer $token_b"

# Verify entries after update/delete
echo "📦  User A GET /brainstorm/ (after update/delete)"
curl -s -X GET "$BRAIN_API/" -H "Authorization: Bearer $token_a" | jq
echo "📦  User B GET /brainstorm/ (after update/delete)"
curl -s -X GET "$BRAIN_API/" -H "Authorization: Bearer $token_b" | jq

echo "✅ Test completed."
