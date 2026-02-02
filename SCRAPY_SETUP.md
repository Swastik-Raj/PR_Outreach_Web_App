# Scrapy Email Service Setup Guide

This guide explains how to set up and use the Scrapy-based email finding and verification service that replaces Hunter API.

## Overview

The Scrapy Email Service provides:
- **Email Discovery**: Crawls domains to find email addresses
- **Email Verification**: Validates emails using DNS and SMTP checks
- **Free Alternative**: No API costs (unlike Hunter.io)
- **Better Control**: Customizable scraping logic

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend → Backend → Email Scraper Service (FastAPI)       │
│                              ↓                               │
│                   Scrapy Email Service (Flask)               │
│                              ↓                               │
│              Scrapy Spider + Email Verifier                  │
│                              ↓                               │
│                   Web Scraping + SMTP Verification           │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### 1. Navigate to the service directory
```bash
cd scrapy-email-service
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

Or use the provided startup script:
```bash
chmod +x start.sh
./start.sh
```

### 3. Configure environment variables
Add to your `.env` file in the project root:
```bash
SCRAPY_EMAIL_SERVICE_URL=http://localhost:5002
```

## Running the Service

### Option 1: Using the startup script
```bash
cd scrapy-email-service
./start.sh
```

### Option 2: Manual startup
```bash
cd scrapy-email-service
python app.py
```

The service will start on `http://localhost:5002`

## Testing the Service

### Health Check
```bash
curl http://localhost:5002/health
```

### Find Email
```bash
curl -X POST http://localhost:5002/find-email \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "domain": "example.com"
  }'
```

### Find and Verify Email (Recommended)
```bash
curl -X POST http://localhost:5002/find-and-verify \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "domain": "nytimes.com"
  }'
```

### Verify Email Only
```bash
curl -X POST http://localhost:5002/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com"
  }'
```

## How It Works

### Email Discovery Process
1. **Pattern Generation**: Creates common email patterns based on name and domain
   - `first.last@domain.com`
   - `firstlast@domain.com`
   - `first@domain.com`
   - `f.last@domain.com`
   - etc.

2. **Web Crawling**: Scrapy spider crawls the domain looking for emails
   - Searches text content for email addresses
   - Prioritizes pages like /about, /team, /contact, /staff
   - Respects robots.txt
   - Limited to 20 pages per domain

3. **Match Scoring**: Each found email is scored based on name matching
   - 100: Exact pattern match
   - 95: Full name match
   - 75: Partial name match
   - 50: Domain match only

### Email Verification Process
1. **Format Validation**: Checks email format using regex
2. **DNS Check**: Verifies domain has valid MX records
3. **SMTP Check**: Connects to mail server to verify email exists
4. **Confidence Score**: Combines all checks (0-100)

### Confidence Levels
- **95-100**: Email found with SMTP verification ✅
- **70-94**: Valid DNS but SMTP inconclusive ⚠️
- **50-69**: Valid DNS, no SMTP verification ⚠️
- **20-49**: Valid format but DNS issues ❌
- **0-19**: Invalid format or domain ❌

## Integration with Existing System

The Scrapy service is already integrated:

1. **Email Scraper Service** (`email-scraper-service/app.py`):
   - Calls Scrapy service for each journalist
   - Replaces Hunter API calls
   - Returns enriched data with emails

2. **Backend Controller** (`backend/src/controller.js`):
   - Receives pre-enriched data from scraper
   - Filters by confidence (>= 70%)
   - Saves to Supabase

## Advantages Over Hunter API

| Feature | Hunter API | Scrapy Service |
|---------|-----------|----------------|
| Cost | $49-199/month | Free |
| Control | Limited | Full control |
| Customization | No | Yes |
| Verification | API-based | SMTP-based |
| Rate Limits | 50-500/month | Unlimited |
| Accuracy | High | Good |

## Troubleshooting

### Service won't start
```bash
# Check if port 5002 is already in use
lsof -i :5002

# Kill the process if needed
kill -9 <PID>
```

### SMTP verification failing
Some mail servers block SMTP verification attempts. This is normal. The service will still return results with lower confidence scores.

### Scraping timeout
If scraping takes too long, the service will timeout after 60 seconds. This is by design to prevent hanging requests.

### No emails found
- Check that the domain is correct
- Verify the website has publicly visible email addresses
- Some sites hide emails using JavaScript or images
- Try a different domain

## Configuration

Edit `scrapy-email-service/settings.py` to adjust:
- `DEPTH_LIMIT`: How deep to crawl (default: 3)
- `CLOSESPIDER_PAGECOUNT`: Max pages to crawl (default: 20)
- `DOWNLOAD_DELAY`: Delay between requests (default: 1 second)
- `CONCURRENT_REQUESTS`: Parallel requests (default: 2)

## Limitations

1. **Robots.txt**: Service respects robots.txt by default
2. **Rate Limiting**: Some sites may block too many requests
3. **JavaScript Sites**: Cannot scrape JavaScript-rendered content
4. **SMTP Blocking**: Some mail servers block verification
5. **Timeout**: 60-second limit per scraping operation

## Best Practices

1. **Use find-and-verify endpoint**: Combines scraping + verification for best results
2. **Filter by confidence**: Only use emails with >= 70% confidence
3. **Handle timeouts**: Implement retry logic for timeout errors
4. **Cache results**: Cache successful lookups to avoid re-scraping
5. **Respect limits**: Don't overwhelm target servers with requests

## Next Steps

1. Monitor the service logs for errors
2. Adjust confidence thresholds based on results
3. Add custom scraping patterns for specific domains
4. Implement result caching for better performance
