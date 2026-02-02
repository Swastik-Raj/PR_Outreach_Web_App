# Scrapy Email Service

A powerful email finding and verification service that replaces Hunter API using Scrapy web scraping and SMTP verification.

## Features

- **Email Discovery**: Crawls domains to find email addresses matching journalist names
- **Email Verification**: Validates emails using DNS MX record checks and SMTP verification
- **Pattern Matching**: Intelligent scoring based on common email patterns
- **Batch Processing**: Verify multiple emails at once

## Installation

```bash
cd scrapy-email-service
pip install -r requirements.txt
```

## Running the Service

```bash
python app.py
```

The service will start on `http://localhost:5001`

## API Endpoints

### Find Email
```bash
POST /find-email
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "domain": "example.com"
}
```

### Verify Email
```bash
POST /verify-email
Content-Type: application/json

{
  "email": "john.doe@example.com"
}
```

### Find and Verify (Recommended)
```bash
POST /find-and-verify
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "domain": "example.com"
}
```

### Verify Emails Batch
```bash
POST /verify-emails-batch
Content-Type: application/json

{
  "emails": ["email1@example.com", "email2@example.com"]
}
```

### Health Check
```bash
GET /health
```

## How It Works

### Email Discovery
1. Generates common email patterns based on first name, last name, and domain
2. Crawls the target domain looking for email addresses
3. Scores each found email based on how well it matches the target person
4. Prioritizes pages like /about, /team, /contact, /staff

### Email Verification
1. **Format Check**: Validates email format using regex
2. **DNS Check**: Verifies the domain has valid MX records
3. **SMTP Check**: Connects to the mail server to verify the email exists
4. **Confidence Score**: Combines all checks into a 0-100 confidence score

### Confidence Scoring
- **95-100**: Email found with SMTP verification
- **70-94**: Valid DNS but SMTP verification inconclusive
- **50-69**: Valid DNS but no SMTP verification
- **20-49**: Valid format but DNS issues
- **0-19**: Invalid format or domain

## Environment Variables

```bash
PORT=5001  # Service port (default: 5001)
```

## Integration with Backend

The backend service automatically calls this service through `scrapy.service.js`:

```javascript
import { findJournalistEmail } from './enrichment/scrapy.service.js';

const result = await findJournalistEmail({
  firstName: 'John',
  lastName: 'Doe',
  domain: 'example.com'
});
```

## Notes

- The service respects robots.txt by default
- Crawling is limited to 20 pages per domain
- SMTP verification may not work for all domains (firewalls, rate limits)
- The service uses a 60-second timeout for scraping operations
