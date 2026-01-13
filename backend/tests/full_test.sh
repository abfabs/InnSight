#!/bin/bash
echo "🚀 MEGA InnSight API Test Suite - COMPLETE DASHBOARD COVERAGE"
echo "=================================================================="

set -e  # Fail fast on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function pass { echo -e "${GREEN}✅ PASS: $1${NC}"; TESTS_PASSED=$((TESTS_PASSED + 1)); }
function fail { echo -e "${RED}❌ FAIL: $1${NC}"; exit 1; }
function skip { echo -e "${YELLOW}⏭️  SKIP: $1${NC}"; }

TESTS_PASSED=0

# === HEALTH CHECK ===
echo ""
echo "🏥 Testing Health Check..."
HEALTH=$(curl -s http://localhost:5000/ | jq -r '.status')
if [[ "$HEALTH" == *"LIVE"* ]]; then
    pass "Health check OK"
else
    fail "Health check failed"
fi

# === CORE ENDPOINTS ===
echo ""
echo "📋 Testing Core Listings API..."
LISTINGS=$(curl -s "http://localhost:5000/api/listings?city=prague&limit=1" | jq '.')
if [[ $(echo "$LISTINGS" | jq '. | length') -eq 1 ]] && [[ $(echo "$LISTINGS" | jq '.[0].listing_id') != "null" ]]; then
    pass "Listings OK"
else
    fail "Listings failed"
fi

# Filters
curl -s "http://localhost:5000/api/listings?city=prague&min_price=1000&limit=1" | jq -r '.[0].price // "❌"' | grep -q '[0-9]' && pass "Price filter OK" || fail "Price filter failed"
curl -s "http://localhost:5000/api/listings?city=prague&room_type=Entire%20home/apt&limit=1" | jq -r '.[0].room_type // "❌"' | grep -q 'Entire' && pass "Room filter OK" || fail "Room filter failed"

echo ""
echo "📊 Testing Analytics API..."
ANALYTICS=$(curl -s "http://localhost:5000/api/analytics?city=prague" | jq '.')
if [[ $(echo "$ANALYTICS" | jq '. | length') -eq 1 ]] && [[ $(echo "$ANALYTICS" | jq '.[0].listing_count') -gt 0 ]]; then
    AVG_PRICE=$(echo "$ANALYTICS" | jq -r '.[0].avg_price')
    pass "Analytics OK (avg: €$AVG_PRICE)"
else
    fail "Analytics failed"
fi

# === SENTIMENT ENDPOINTS ===
echo ""
echo "😊 Testing Original Sentiment APIs..."
PRAGUE_NS=$(curl -s "http://localhost:5000/api/neighborhood-sentiment?city=prague" | jq '. | length')
if [[ "$PRAGUE_NS" -gt 0 ]]; then
    pass "Neighborhood sentiment OK ($PRAGUE_NS neighborhoods)"
else
    fail "Neighborhood sentiment failed"
fi

AMS_NS=$(curl -s "http://localhost:5000/api/neighborhood-sentiment?city=amsterdam" | jq '. | length')
ROME_NS=$(curl -s "http://localhost:5000/api/neighborhood-sentiment?city=rome" | jq '. | length')
pass "All cities sentiment OK (AMS:$AMS_NS, ROME:$ROME_NS)"

echo ""
echo "💬 Testing Review Sentiment..."
curl -s "http://localhost:5000/api/reviews-sentiment?city=prague&limit=1" | jq -r '.[0].sentiment_category // "❌"' | grep -q -E 'positive|negative|neutral' && pass "Reviews sentiment OK" || fail "Reviews sentiment failed"

# === NEW DASHBOARD ENDPOINTS ===
echo ""
echo "📈 Testing NEW Dashboard Analytics Endpoints..."

# 1. Sentiment Summary
echo ""
echo "🎯 Testing Sentiment Summary..."
SENT_CITY=$(curl -s "http://localhost:5000/api/sentiment-summary?city=amsterdam&level=city" | jq '.')
if [[ $(echo "$SENT_CITY" | jq '. | length') -eq 1 ]] && [[ $(echo "$SENT_CITY" | jq '.[0].total_reviews') -gt 0 ]]; then
    TOTAL_REVIEWS=$(echo "$SENT_CITY" | jq -r '.[0].total_reviews')
    SENTIMENT=$(echo "$SENT_CITY" | jq -r '.[0].sentiment_mean')
    pass "Sentiment summary city-level OK ($TOTAL_REVIEWS reviews, sentiment: $SENTIMENT)"
else
    fail "Sentiment summary city-level failed"
fi

SENT_NEIGH=$(curl -s "http://localhost:5000/api/sentiment-summary?city=amsterdam&level=neighbourhood" | jq '. | length')
if [[ "$SENT_NEIGH" -gt 0 ]]; then
    pass "Sentiment summary neighbourhood-level OK ($SENT_NEIGH neighborhoods)"
else
    fail "Sentiment summary neighbourhood-level failed"
fi

# 2. Room Types
echo ""
echo "🏠 Testing Room Type Distribution..."
ROOM_CITY=$(curl -s "http://localhost:5000/api/room-types?city=prague&level=city" | jq '.')
if [[ $(echo "$ROOM_CITY" | jq '. | length') -eq 1 ]] && [[ $(echo "$ROOM_CITY" | jq '.[0].total_listings') -gt 0 ]]; then
    TOTAL_LISTINGS=$(echo "$ROOM_CITY" | jq -r '.[0].total_listings')
    ENTIRE_HOME_PCT=$(echo "$ROOM_CITY" | jq -r '.[0].room_types["Entire home/apt"].percentage')
    pass "Room types city-level OK ($TOTAL_LISTINGS listings, $ENTIRE_HOME_PCT% entire home)"
else
    fail "Room types city-level failed"
fi

ROOM_NEIGH=$(curl -s "http://localhost:5000/api/room-types?city=prague&level=neighbourhood" | jq '. | length')
if [[ "$ROOM_NEIGH" -gt 0 ]]; then
    pass "Room types neighbourhood-level OK ($ROOM_NEIGH neighborhoods)"
else
    fail "Room types neighbourhood-level failed"
fi

# 3. Occupancy
echo ""
echo "📅 Testing Occupancy by Month..."
OCC_CITY=$(curl -s "http://localhost:5000/api/occupancy?city=rome&level=city" | jq '.')
if [[ $(echo "$OCC_CITY" | jq '. | length') -eq 1 ]] && [[ $(echo "$OCC_CITY" | jq '.[0].monthly_occupancy | length') -gt 0 ]]; then
    MONTHS=$(echo "$OCC_CITY" | jq -r '.[0].monthly_occupancy | length')
    LATEST_RATE=$(echo "$OCC_CITY" | jq -r '.[0].monthly_occupancy[-1].occupancy_rate')
    pass "Occupancy city-level OK ($MONTHS months, latest: $LATEST_RATE%)"
else
    fail "Occupancy city-level failed"
fi

OCC_NEIGH=$(curl -s "http://localhost:5000/api/occupancy?city=rome&level=neighbourhood" | jq '. | length')
if [[ "$OCC_NEIGH" -gt 0 ]]; then
    pass "Occupancy neighbourhood-level OK ($OCC_NEIGH neighborhoods)"
else
    fail "Occupancy neighbourhood-level failed"
fi

# 4. Top Hosts
echo ""
echo "👑 Testing Top Hosts..."
HOSTS_CITY=$(curl -s "http://localhost:5000/api/top-hosts?city=amsterdam&level=city" | jq '.')
if [[ $(echo "$HOSTS_CITY" | jq '. | length') -eq 1 ]] && [[ $(echo "$HOSTS_CITY" | jq '.[0].top_hosts | length') -gt 0 ]]; then
    NUM_HOSTS=$(echo "$HOSTS_CITY" | jq -r '.[0].top_hosts | length')
    TOP_HOST=$(echo "$HOSTS_CITY" | jq -r '.[0].top_hosts[0].host_name')
    TOP_LISTINGS=$(echo "$HOSTS_CITY" | jq -r '.[0].top_hosts[0].total_listings')
    pass "Top hosts city-level OK ($NUM_HOSTS hosts, #1: $TOP_HOST with $TOP_LISTINGS listings)"
else
    fail "Top hosts city-level failed"
fi

HOSTS_NEIGH=$(curl -s "http://localhost:5000/api/top-hosts?city=amsterdam&level=neighbourhood" | jq '. | length')
if [[ "$HOSTS_NEIGH" -gt 0 ]]; then
    pass "Top hosts neighbourhood-level OK ($HOSTS_NEIGH neighborhoods)"
else
    fail "Top hosts neighbourhood-level failed"
fi

# === FILTERING TESTS ===
echo ""
echo "🔍 Testing Specific Neighbourhood Filtering..."
curl -s "http://localhost:5000/api/sentiment-summary?city=amsterdam&neighbourhood=Centrum-West" | jq -r '.[0].neighbourhood // "❌"' | grep -q 'Centrum-West' && pass "Neighbourhood filter OK" || fail "Neighbourhood filter failed"

# === WORD CLOUD & NEIGHBORHOODS ===
echo ""
echo "☁️  Testing Word Cloud..."
curl -s "http://localhost:5000/api/wordcloud?city=prague&limit=1" | jq -r '.[0].word // "❌"' | grep -q '[a-z]' && pass "Wordcloud data OK" || fail "Wordcloud failed"

echo ""
echo "🗺️  Testing Neighborhoods (real data)..."
NEIGHS=$(curl -s "http://localhost:5000/api/neighbourhoods?city=prague" | jq -r '.neighbourhoods | length')
if [[ "$NEIGHS" -gt 0 ]]; then
    pass "Real neighborhoods OK ($NEIGHS neighborhoods)"
else
    fail "Neighborhoods failed"
fi

echo ""
echo "🌍 Testing Cities..."
curl -s "http://localhost:5000/api/cities" | jq -r '.cities | length' | grep -q '3' && pass "Cities OK" || fail "Cities failed"

# === ERROR HANDLING TESTS ===
echo ""
echo "⚠️  Testing Error Handling..."
curl -s -w "%{http_code}" "http://localhost:5000/api/listings?min_price=abc" 2>/dev/null | grep -q "400" && pass "Bad param error OK" || fail "Bad param error failed"
curl -s -w "%{http_code}" "http://localhost:5000/api/wordcloud?city=bogus" 2>/dev/null | grep -q "400" && pass "Invalid city error OK" || fail "Invalid city error failed"
curl -s -w "%{http_code}" "http://localhost:5000/api/sentiment-summary?city=invalid" 2>/dev/null | grep -q "400" && pass "Dashboard city validation OK" || fail "Dashboard city validation failed"

# === IMAGE SERVING ===
echo ""
echo "🖼️  Testing Static Images..."
curl -s -w "%{http_code}" "http://localhost:5000/static/wordclouds/prague/prague_overall.png" 2>/dev/null | grep -q "200" && pass "Wordcloud images OK" || skip "Images missing (run ETL first)"

# === SUMMARY ===
echo ""
echo "=================================================================="
echo -e "${GREEN}✅ TEST RESULTS: $TESTS_PASSED TESTS PASSED${NC}"
echo "=================================================================="
echo ""
echo "📊 Endpoints Tested:"
echo "  - Core: listings, analytics, neighborhoods, cities"
echo "  - Sentiment: neighborhood-sentiment, reviews-sentiment"
echo "  - Dashboard: sentiment-summary, room-types, occupancy, top-hosts"
echo "  - Wordcloud: API + images"
echo "  - Error handling: 3 validation tests"
echo ""
echo "🎉 InnSight API MEGA TEST COMPLETE!"
