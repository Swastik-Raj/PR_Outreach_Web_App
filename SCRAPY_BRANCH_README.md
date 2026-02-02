# Scrapy Email Service Branch

**Branch Purpose**: Testing Scrapy as a replacement for Hunter API for email finding and verification

## What's New in This Branch

This branch replaces the Hunter.io API with a custom Scrapy-based email finding and verification service.

### Key Changes

1. **New Scrapy Email Service** (`/scrapy-email-service/`)
   - Flask-based API for email discovery and verification
   - Uses Scrapy for web crawling
   - SMTP and DNS verification
   - Free and unlimited usage

2. **Updated Email Scraper Service** (`/email-scraper-service/app.py`)
   - Now calls Scrapy service instead of Hunter API
   - Uses `find_email_with_scrapy()` function
   - Returns enriched data with verification status

3. **No More Hunter API Dependency**
   - Removed `HUNTER_API_KEY` requirement
   - Added `SCRAPY_EMAIL_SERVICE_URL` configuration
   - Cost savings: $0/month vs $49-199/month

## Quick Start

### 1. Install Dependencies
```bash
cd scrapy-email-service
pip install -r requirements.txt
```

### 2. Start Scrapy Service
```bash
cd scrapy-email-service
python app.py
```
Service runs on `http://localhost:5002`

### 3. Update Environment
Add to `.env`:
```bash
SCRAPY_EMAIL_SERVICE_URL=http://localhost:5002
```

### 4. Start Other Services
```bash
# Email scraper (terminal 2)
cd email-scraper-service
python app.py

# Backend (terminal 3)
cd backend
npm start

# Frontend (terminal 4)
cd frontend
npm run dev
```

### 5. Test Integration
```bash
./test-scrapy-integration.sh
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│                  http://localhost:3000                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (Node/Express)                  │
│                  http://localhost:5000                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│            Email Scraper Service (FastAPI)               │
│                  http://localhost:5001                   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Scrapes RSS feeds → Gets journalist data        │  │
│  │              ↓                                    │  │
│  │  Calls Scrapy Email Service for enrichment       │  │
│  └──────────────────────┬───────────────────────────┘  │
└─────────────────────────┼──────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Scrapy Email Service (Flask)                    │
│              http://localhost:5002                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  1. Generates email patterns                     │  │
│  │  2. Crawls domain with Scrapy                    │  │
│  │  3. Finds matching emails                        │  │
│  │  4. Verifies with DNS + SMTP                     │  │
│  │  5. Returns confidence score                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### Scrapy Email Service (Port 5002)

#### `POST /find-and-verify` (Recommended)
Finds and verifies email in one call.

**Request**:
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "domain": "example.com"
}
```

**Response**:
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

#### `POST /verify-email`
Verifies an existing email.

#### `GET /health`
Health check endpoint.

## Features Comparison

| Feature | Hunter API | Scrapy Service |
|---------|-----------|----------------|
| **Cost** | $49-199/mo | Free |
| **Rate Limits** | 50-500/mo | Unlimited |
| **Speed** | 1-2s | 10-30s |
| **Accuracy** | Very High | Good-High |
| **Control** | None | Full |
| **Verification** | API-based | SMTP-based |
| **Customization** | No | Yes |
| **Source URLs** | No | Yes |

## Documentation

- **`SCRAPY_SETUP.md`** - Detailed setup and configuration guide
- **`HUNTER_TO_SCRAPY_MIGRATION.md`** - Complete migration guide
- **`scrapy-email-service/README.md`** - API documentation
- **`DATA_FLOW_EXPLAINED.md`** - Updated data flow (now uses Scrapy)

## Testing

Run the integration test:
```bash
./test-scrapy-integration.sh
```

This tests:
1. Scrapy service health
2. Email scraper service health
3. Direct email finding
4. Email verification
5. Full integration flow

## Performance Notes

### Pros
- ✅ No API costs or monthly fees
- ✅ Unlimited lookups
- ✅ Full control over scraping logic
- ✅ Real-time SMTP verification
- ✅ Source URLs for found emails
- ✅ Customizable confidence thresholds

### Cons
- ⚠️ Slower than Hunter API (10-30s vs 1-2s)
- ⚠️ Some mail servers block SMTP verification
- ⚠️ Requires additional service to run
- ⚠️ May need proxies for large-scale scraping

## Troubleshooting

### Service won't start
```bash
# Check Python version (needs 3.8+)
python3 --version

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Low confidence scores
- Normal for some domains
- SMTP blocking is common
- Emails may not be publicly visible
- Adjust threshold if needed

### Timeouts
- Reduce `DEPTH_LIMIT` in settings.py
- Reduce `CLOSESPIDER_PAGECOUNT`
- Some sites are just slow

## Rollback Plan

To revert to Hunter API:
1. Restore original `email-scraper-service/app.py`
2. Add `HUNTER_API_KEY` back to `.env`
3. Remove `SCRAPY_EMAIL_SERVICE_URL`
4. Restart services

See `HUNTER_TO_SCRAPY_MIGRATION.md` for details.

## Next Steps

1. ✅ Test with real journalist domains
2. ✅ Monitor confidence scores
3. ✅ Add custom patterns for specific publishers
4. ✅ Implement result caching
5. ✅ Consider proxy support for scale
6. ✅ Fine-tune confidence thresholds

## Support

For issues:
1. Check service logs
2. Review documentation files
3. Test individual components
4. Check GitHub issues

## Files Added/Modified

### New Files
- `/scrapy-email-service/*` - Complete Scrapy service
- `SCRAPY_SETUP.md` - Setup guide
- `HUNTER_TO_SCRAPY_MIGRATION.md` - Migration guide
- `SCRAPY_BRANCH_README.md` - This file
- `test-scrapy-integration.sh` - Integration test script

### Modified Files
- `/email-scraper-service/app.py` - Uses Scrapy instead of Hunter
- `.env` - Added `SCRAPY_EMAIL_SERVICE_URL`
- `.env.example` - Updated configuration
- `DATA_FLOW_EXPLAINED.md` - Updated flow diagrams

### Unchanged Files
- Backend, Frontend, Database - No changes needed
- Existing functionality preserved
- API contracts maintained
