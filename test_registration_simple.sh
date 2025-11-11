#!/bin/bash

# Simple registration test script

API_URL="http://localhost:8000"

echo "=========================================="
echo "Testing Registration Flow"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running at $API_URL"
    echo "   Please start it with: docker-compose up backend"
    exit 1
fi

echo ""
echo "2. Registering a new user..."
EMAIL="test_$(date +%s)@example.com"
PASSWORD="testpass123"
NAME="Test User"

RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\",
    \"name\": \"$NAME\"
  }")

echo "Response: $RESPONSE"

# Check if registration was successful
if echo "$RESPONSE" | grep -q "Registration successful"; then
    echo "✅ Registration successful!"
    echo "   Email: $EMAIL"
    echo ""
    echo "3. Check backend logs for verification token:"
    echo "   docker-compose logs backend | grep 'VERIFICATION TOKEN'"
    echo ""
    echo "4. To verify email, use the token from logs:"
    echo "   curl -X POST $API_URL/api/auth/verify-email -H 'Content-Type: application/json' -d '{\"token\": \"TOKEN_FROM_LOGS\"}'"
else
    echo "❌ Registration failed"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
fi

