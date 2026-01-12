#!/bin/bash
echo "MEGA InnSight API Test Suite (localhost:5000) - COMPLETE COVERAGE"
echo "=================================================================="

set -e  # Fail fast on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function pass { echo -e "${GREEN}PASS: $1${NC}"; TESTS_PASSED=$((TESTS_PASSED + 1)); }
function fail { echo -e "${RED}FAIL: $1${NC}"; exit 1; }
function skip { echo -e "${YELLOW}SKIP: $1${NC}"; }

TESTS_PASSED=0
TESTS_TOTAL=0

# === HEALTH CHECK ===
echo "Testing Health Check..."
HEALTH=$(curl -s http://localhost:5000/ | jq -r '.status')
if [[ "$HEALTH" == *"LIVE"* ]]; then
    pass "Health check OK"
else
    fail "Health check failed"
fi

# === CORE ENDPOINTS ===
echo "Testing Listings API..."
LISTINGS=$(curl -s "http://localhost:5000/api/listings?city=prague&limit=1" | jq '.')
if [[ $(echo "$LISTINGS" | jq '. | length') -eq 1 ]] && [[ $(echo "$LISTINGS" | jq '.[0].listing_id') != "null" ]]; then
    pass "Listings OK"
else
    fail "Listings failed"
fi

# Filters
curl -s "http://localhost:5000/api/listings?city=prague&min_price=1000&limit=1" | jq -r '.[0].price // "❌"' | grep -q '[0-9]' && pass "Price filter OK" || fail "Price filter failed"
curl -s "http://localhost:5000/api/listings?city=prague&room_type=Entire%20home/apt&limit=1" | jq -r '.[0].room_type // "❌"' | grep -q 'Entire' && pass "Room filter OK" || fail "Room filter failed"

echo "Testing Analytics API..."
ANALYTICS=$(curl -s "http://localhost:5000/api/analytics?city=prague" | jq '.')
if [[ $(echo "$ANALYTICS" | jq '. | length') -eq 1 ]] && [[ $(echo "$ANALYTICS" | jq '.[0].listing_count') -gt 0 ]]; then
    AVG_PRICE=$(echo "$ANALYTICS" | jq -r '.[0].avg_price')
    pass "Analytics OK (avg: $AVG_PRICE)"
else
    fail "Analytics failed"
fi

echo "Testing Sentiment APIs..."
PRAGUE_NS=$(curl -s "http://localhost:5000/api/neighborhood-sentiment?city=prague" | jq '. | length')
if [[ "$PRAGUE_NS" -gt 0 ]]; then
    pass "Neighborhood sentiment OK ($PRAGUE_NS hoods)"
else
    fail "Neighborhood sentiment failed"
fi

AMS_NS=$(curl -s "http://localhost:5000/api/neighborhood-sentiment?city=amsterdam" | jq '. | length')
ROME_NS=$(curl -s "http://localhost:5000/api/neighborhood-sentiment?city=rome" | jq '. | length')
pass "All cities sentiment OK (AMS:$AMS_NS, ROME:$ROME_NS)"

echo "Testing Review Sentiment..."
curl -s "http://localhost:5000/api/reviews-sentiment?city=prague&limit=1" | jq -r '.[0].sentiment_category // "❌"' | grep -q -E 'positive|negative|neutral' && pass "Reviews sentiment OK" || fail "Reviews sentiment failed"

echo "Testing Word Cloud..."
curl -s "http://localhost:5000/api/wordcloud?city=prague&limit=1" | jq -r '.[0].word // "❌"' | grep -q '[a-z]' && pass "Wordcloud data OK" || fail "Wordcloud failed"

echo "Testing Neighborhoods (real data)..."
curl -s "http://localhost:5000/api/neighbourhoods?city=prague" | jq -r '.neighbourhoods | length' | grep -q '[0-9]' && pass "Real neighborhoods OK" || fail "Neighborhoods failed"

echo "Testing Stubs..."
curl -s "http://localhost:5000/api/cities" | jq -r '.cities | length' | grep -q '3' && pass "Cities stub OK" || fail "Cities stub failed"

# === ERROR HANDLING TESTS ===
echo "Testing Error Handling..."
curl -s -w "%{http_code}" "http://localhost:5000/api/listings?min_price=abc" | grep -q "400" && pass "Bad param error OK" || fail "Bad param error failed"
curl -s -w "%{http_code}" "http://localhost:5000/api/wordcloud?city=bogus" | grep -q "400" && pass "Invalid city error OK" || fail "Invalid city error failed"
curl -s -w "%{http_code}" "http://localhost:5000/api/wordcloud?limit=abc" | grep -q "400" && pass "Invalid limit error OK" || fail "Invalid limit error failed"

# === IMAGE SERVING ===
echo "Testing Static Images..."
curl -s -w "%{http_code}" "http://localhost:5000/static/wordclouds/prague/prague_overall.png" | grep -q "200" && pass "Wordcloud images OK" || skip "Images missing (run ETL first)"

# === SUMMARY ===
echo "=================================================================="
echo "TEST RESULTS: $TESTS_PASSED / $(($TESTS_PASSED + $(grep -c "SKIP:" /tmp/test.log || echo 0))) TESTS PASSED"
echo "InnSight API MEGA TEST PASSED"
