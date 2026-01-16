#!/usr/bin/env bash
set -e

BASE_URL="http://localhost:5000/api"

echo "======================================================"
echo "🚀 INNSIGHT BACKEND FULL API TEST"
echo "======================================================"

fail() {
  echo "❌ TEST FAILED: $1"
  exit 1
}

pass() {
  echo "✅ $1"
}

request() {
  local url="$1"
  local label="$2"

  echo "→ $label"
  RESPONSE=$(curl -s -w "\n%{http_code}" "$url")
  BODY=$(echo "$RESPONSE" | head -n -1)
  CODE=$(echo "$RESPONSE" | tail -n 1)

  if [[ "$CODE" != "200" ]]; then
    echo "Status: $CODE"
    echo "$BODY"
    fail "$label"
  fi

  if [[ "$BODY" == "[]" ]]; then
    fail "$label returned empty list"
  fi

  pass "$label"
}

# ------------------------------------------------------
# BASIC
# ------------------------------------------------------
request "$BASE_URL/cities" "Cities list"

# ------------------------------------------------------
# LISTINGS
# ------------------------------------------------------
request "$BASE_URL/listings?city=amsterdam&limit=10" "Listings (Amsterdam)"

# ------------------------------------------------------
# NEIGHBORHOODS
# ------------------------------------------------------
request "$BASE_URL/neighborhoods?city=amsterdam" "Neighborhoods (Amsterdam)"

# ------------------------------------------------------
# SENTIMENT SUMMARY
# ------------------------------------------------------
request "$BASE_URL/sentiment-summary?city=amsterdam&level=city" "Sentiment summary city"
request "$BASE_URL/sentiment-summary?city=amsterdam&level=neighborhood" "Sentiment summary neighborhood"

# ------------------------------------------------------
# ROOM TYPES
# ------------------------------------------------------
request "$BASE_URL/room-types?city=amsterdam&level=city" "Room types city"
request "$BASE_URL/room-types?city=amsterdam&level=neighborhood" "Room types neighborhood"

# ------------------------------------------------------
# OCCUPANCY
# ------------------------------------------------------
request "$BASE_URL/occupancy?city=amsterdam&level=city" "Occupancy city"
request "$BASE_URL/occupancy?city=amsterdam&level=neighborhood" "Occupancy neighborhood"

# ------------------------------------------------------
# TOP HOSTS
# ------------------------------------------------------
request "$BASE_URL/top-hosts?city=amsterdam&level=city" "Top hosts city"
request "$BASE_URL/top-hosts?city=amsterdam&level=neighborhood" "Top hosts neighborhood"

# ------------------------------------------------------
# WORDCLOUD
# ------------------------------------------------------
request "$BASE_URL/wordcloud?city=amsterdam&limit=20" "Wordcloud city"

# ------------------------------------------------------
# REVIEWS SENTIMENT
# ------------------------------------------------------
request "$BASE_URL/reviews-sentiment?city=amsterdam&limit=50" "Reviews sentiment"

# ------------------------------------------------------
# NEIGHBORHOOD SENTIMENT
# ------------------------------------------------------
request "$BASE_URL/neighborhood-sentiment?city=amsterdam" "Neighborhood sentiment"

# ------------------------------------------------------
# ANALYTICS
# ------------------------------------------------------
request "$BASE_URL/analytics?city=amsterdam" "City analytics"

echo "======================================================"
echo "🎉 ALL TESTS PASSED — BACKEND IS SOLID"
echo "======================================================"
