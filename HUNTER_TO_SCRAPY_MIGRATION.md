# Migration Guide: Hunter API → Scrapy Email Service

This guide explains what changed when switching from Hunter API to Scrapy-based email finding and verification.

## Summary of Changes

The project now uses a custom Scrapy-based email finding and verification service instead of Hunter.io API. This provides:

- ✅ **Free**: No API costs or rate limits
- ✅ **Control**: Full control over scraping logic
- ✅ **Verification**: Built-in SMTP and DNS verification
- ✅ **Customizable**: Easy to add custom patterns and logic

## What Changed

### 1. New Service Added
**Location**: `/scrapy-email-service/`

A new Flask service that:
- Crawls domains to find emails using Scrapy
- Verifies emails using DNS and SMTP checks
- Returns confidence scores based on scraping + verification

### 2. Email Scraper Service Updated
**File**: `/email-scraper-service/app.py`

**Before (Hunter API)**:
```python
def find_email_with_hunter(first_name, last_name, domain):
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "first_name": first_name,
        "last_name": last_name,
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }
    res = requests.get(url, params=params)
    # ...
```

**After (Scrapy Service)**:
```python
def find_email_with_scrapy(first_name, last_name, domain):
    url = f"{SCRAPY_EMAIL_SERVICE_URL}/find-and-verify"
    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "domain": domain
    }
    res = requests.post(url, json=payload, timeout=90)
    # ...
```

### 3. Environment Variables
**File**: `.env`

**Before**:
```bash
HUNTER_API_KEY=your_api_key_here
```

**After**:
```bash
SCRAPY_EMAIL_SERVICE_URL=http://localhost:5002
```

### 4. Documentation Updated
- `DATA_FLOW_EXPLAINED.md` - Updated flow diagrams
- `SCRAPY_SETUP.md` - New setup guide
- `.env.example` - Updated with new variables

## Response Format Comparison

### Hunter API Response
```json
{
  "email": "john.doe@example.com",
  "confidence": 99,
  "source": "hunter"
}
```

### Scrapy Service Response
```json
{
  "email": "john.doe@example.com",
  "confidence": 95,
  "source": "scrapy+verification",
  "verified": true,
  "dns_valid": true,
  "smtp_valid": true,
  "match_type": "name_match",
  "source_url": "https://example.com/about"
}
```

**Key Differences**:
- More detailed verification information
- Source URL where email was found
- Match type classification
- SMTP verification status

## Setup Instructions

### 1. Install Dependencies
```bash
cd scrapy-email-service
pip install -r requirements.txt
```

### 2. Update Environment
Add to `.env`:
```bash
SCRAPY_EMAIL_SERVICE_URL=http://localhost:5002
```

### 3. Start the Service
```bash
cd scrapy-email-service
./start.sh
```

Or manually:
```bash
python app.py
```

### 4. Verify It's Running
```bash
curl http://localhost:5002/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "scrapy-email-service"
}
```

## Service Startup Order

The correct order to start all services:

1. **Scrapy Email Service** (Port 5002)
   ```bash
   cd scrapy-email-service
   python app.py
   ```

2. **Email Scraper Service** (Port 5001)
   ```bash
   cd email-scraper-service
   python app.py
   ```

3. **Backend** (Port 5000)
   ```bash
   cd backend
   npm start
   ```

4. **Frontend** (Port 3000)
   ```bash
   cd frontend
   npm run dev
   ```

## Testing the Integration

### Test 1: Scrapy Service Directly
```bash
curl -X POST http://localhost:5002/find-and-verify \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jane",
    "lastName": "Doe",
    "domain": "nytimes.com"
  }'
```

### Test 2: Through Email Scraper Service
```bash
curl "http://localhost:5001/scrape?topic=technology"
```

### Test 3: Full Flow
1. Start all services
2. Open frontend: http://localhost:3000
3. Go to "Campaign Scraper" page
4. Enter topic and company
5. Click "Start Campaign"
6. Check console logs for email finding results

## Troubleshooting

### Scrapy service not responding
**Problem**: `Connection refused` errors

**Solution**:
```bash
# Check if service is running
curl http://localhost:5002/health

# If not, start it
cd scrapy-email-service
python app.py
```

### Email scraper can't reach Scrapy service
**Problem**: Email enrichment failing

**Solution**:
1. Check `.env` has correct URL:
   ```bash
   SCRAPY_EMAIL_SERVICE_URL=http://localhost:5002
   ```
2. Restart email scraper service
3. Check Scrapy service is running

### Low confidence scores
**Problem**: Emails found but confidence < 70%

**Possible causes**:
- SMTP verification blocked by mail server (common)
- Domain has no valid MX records
- Email not publicly visible on website

**Solutions**:
- Lower confidence threshold (not recommended)
- Add fallback to alternative verification methods
- Use manual verification for important contacts

### Scraping timeouts
**Problem**: Requests timeout after 60-90 seconds

**Possible causes**:
- Website is slow to respond
- Too many pages to crawl
- Scrapy spider stuck

**Solutions**:
- Reduce `DEPTH_LIMIT` in `scrapy-email-service/settings.py`
- Reduce `CLOSESPIDER_PAGECOUNT`
- Increase timeout in email scraper service

## Performance Comparison

| Metric | Hunter API | Scrapy Service |
|--------|-----------|----------------|
| Speed | ~1-2s | ~10-30s |
| Accuracy | Very High | Good-High |
| Cost | $49-199/mo | Free |
| Rate Limit | 50-500/mo | Unlimited |
| Customization | None | Full |
| Verification | API-based | SMTP-based |

## Rollback Instructions

If you need to revert to Hunter API:

### 1. Restore email-scraper-service/app.py
```python
# Change back to Hunter API
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def find_email_with_hunter(first_name, last_name, domain):
    # ... original Hunter code
```

### 2. Update .env
```bash
HUNTER_API_KEY=your_api_key_here
# Remove or comment out:
# SCRAPY_EMAIL_SERVICE_URL=http://localhost:5002
```

### 3. Restart services
```bash
# Stop Scrapy service
# Restart email scraper service
```

## Benefits Summary

### Cost Savings
- **Before**: $49-199/month for Hunter API
- **After**: $0/month (free)

### Scalability
- **Before**: 50-500 emails/month limit
- **After**: Unlimited lookups

### Control
- **Before**: Black box API
- **After**: Full control over:
  - Scraping logic
  - Verification methods
  - Match scoring
  - Custom patterns
  - Rate limiting

### Data Quality
- **Before**: Trust Hunter's data
- **After**:
  - See exactly where emails were found
  - Verify emails in real-time
  - Combine multiple data sources
  - Custom validation rules

## Next Steps

1. ✅ Test the Scrapy service with real domains
2. ✅ Monitor confidence scores and adjust thresholds
3. ✅ Add custom scraping patterns for specific publishers
4. ✅ Implement result caching to avoid re-scraping
5. ✅ Add retry logic for failed lookups
6. ✅ Monitor SMTP verification success rates
7. ✅ Consider adding proxy support for large-scale scraping

## Support

For issues or questions:
1. Check `SCRAPY_SETUP.md` for detailed setup
2. Review `scrapy-email-service/README.md` for API docs
3. Check service logs for error messages
4. Test individual components in isolation
