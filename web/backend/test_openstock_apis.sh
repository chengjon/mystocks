#!/bin/bash

API_BASE="http://localhost:8000/api"

echo "=== Testing OpenStock APIs ==="
echo ""

# 1. Login to get token
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//;s/"$//')

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi
echo "✅ Login successful"
echo ""

# 2. Test watchlist groups (to verify datetime serialization)
echo "2. Testing watchlist groups API..."
GROUPS_RESPONSE=$(curl -s "${API_BASE}/watchlist/groups" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$GROUPS_RESPONSE" | grep -q '"id"'; then
  echo "✅ Watchlist groups API working"
  echo "   Response sample: $(echo $GROUPS_RESPONSE | head -c 200)..."
else
  echo "❌ Watchlist groups API failed"
  echo "   Response: $GROUPS_RESPONSE"
fi
echo ""

# 3. Test stock search
echo "3. Testing stock search API..."
SEARCH_RESPONSE=$(curl -s "${API_BASE}/stock-search/search?q=平安&market=cn" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$SEARCH_RESPONSE" | grep -q '"symbol"'; then
  echo "✅ Stock search API working"
  echo "   Found $(echo $SEARCH_RESPONSE | grep -o '"symbol"' | wc -l) results"
else
  echo "❌ Stock search API failed"
  echo "   Response: $SEARCH_RESPONSE"
fi
echo ""

# 4. Test stock quote
echo "4. Testing stock quote API..."
QUOTE_RESPONSE=$(curl -s "${API_BASE}/stock-search/quote/000001?market=cn" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$QUOTE_RESPONSE" | grep -q '"current"'; then
  echo "✅ Stock quote API working"
  echo "   Response sample: $(echo $QUOTE_RESPONSE | head -c 200)..."
else
  echo "❌ Stock quote API failed"
  echo "   Response: $QUOTE_RESPONSE"
fi
echo ""

# 5. Test stock news (to verify datetime handling)
echo "5. Testing stock news API..."
NEWS_RESPONSE=$(curl -s "${API_BASE}/stock-search/news/000001?market=cn" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$NEWS_RESPONSE" | grep -q '"headline"'; then
  echo "✅ Stock news API working"
  NEWS_COUNT=$(echo $NEWS_RESPONSE | grep -o '"headline"' | wc -l)
  echo "   Found $NEWS_COUNT news items"
  # Check if datetime is a number (timestamp)
  if echo "$NEWS_RESPONSE" | grep -q '"datetime":[0-9]'; then
    echo "✅ News datetime format is correct (timestamp)"
  else
    echo "⚠️  News datetime format might be incorrect"
  fi
else
  echo "❌ Stock news API failed"
  echo "   Response: $NEWS_RESPONSE"
fi
echo ""

echo "=== Test Complete ==="
