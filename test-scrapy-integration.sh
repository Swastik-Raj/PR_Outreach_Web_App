#!/bin/bash

echo "========================================="
echo "Scrapy Email Service Integration Test"
echo "========================================="
echo ""

SCRAPY_URL="http://localhost:5002"
SCRAPER_URL="http://localhost:5001"

echo "Test 1: Scrapy Service Health Check"
echo "-------------------------------------"
curl -s $SCRAPY_URL/health | python3 -m json.tool || echo "❌ Scrapy service not running on port 5002"
echo ""
echo ""

echo "Test 2: Email Scraper Service Health"
echo "-------------------------------------"
curl -s $SCRAPER_URL/docs 2>&1 | grep -q "FastAPI" && echo "✓ Email scraper service is running" || echo "❌ Email scraper service not running on port 5001"
echo ""
echo ""

echo "Test 3: Find and Verify Email (Direct)"
echo "-------------------------------------"
echo "Testing with: first_name=Sam, last_name=Altman, domain=openai.com"
curl -s -X POST $SCRAPY_URL/find-and-verify \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Sam",
    "lastName": "Altman",
    "domain": "openai.com"
  }' | python3 -m json.tool || echo "❌ Failed to call Scrapy service"
echo ""
echo ""

echo "Test 4: Verify Email Format"
echo "-------------------------------------"
curl -s -X POST $SCRAPY_URL/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }' | python3 -m json.tool || echo "❌ Failed to verify email"
echo ""
echo ""

echo "Test 5: Full Integration Test"
echo "-------------------------------------"
echo "Testing scraper service with topic=AI"
curl -s "$SCRAPER_URL/scrape?topic=AI" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'✓ Found {len(data)} journalists')
    if len(data) > 0:
        first = data[0]
        print(f'  Example: {first.get(\"first_name\", \"?\")} {first.get(\"last_name\", \"?\")}')
        print(f'  Email: {first.get(\"email\", \"None\")}')
        print(f'  Confidence: {first.get(\"email_confidence\", 0)}%')
        print(f'  Source: {first.get(\"email_source\", \"?\")}')
except:
    print('❌ Failed to parse response')
" || echo "❌ Full integration test failed"
echo ""
echo ""

echo "========================================="
echo "Test Summary"
echo "========================================="
echo ""
echo "If all tests passed, the Scrapy integration is working correctly!"
echo ""
echo "Next steps:"
echo "1. Check confidence scores of found emails"
echo "2. Monitor service logs for errors"
echo "3. Test with different domains and names"
echo ""
echo "To view logs:"
echo "  - Scrapy service: Check terminal where 'python app.py' is running"
echo "  - Email scraper: Check terminal where scraper is running"
echo ""
