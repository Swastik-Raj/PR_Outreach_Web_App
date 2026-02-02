from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from run_scraper import scrape_journalists_from_publishers
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

root_env = Path(__file__).parent.parent / ".env"
load_dotenv(root_env)

SCRAPY_EMAIL_SERVICE_URL = os.getenv("SCRAPY_EMAIL_SERVICE_URL", "http://localhost:5002")
print("=" * 50)
print("Email Scraper Service Starting...")
print(f"Environment file: {root_env}")
print(f"Scrapy Email Service URL: {SCRAPY_EMAIL_SERVICE_URL}")
print("=" * 50)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_email_with_scrapy(first_name, last_name, domain):
    if not SCRAPY_EMAIL_SERVICE_URL:
        print(f"⚠️ SCRAPY_EMAIL_SERVICE_URL missing for {first_name} {last_name}")
        return None, 0, "missing_service_url"

    url = f"{SCRAPY_EMAIL_SERVICE_URL}/find-and-verify"
    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "domain": domain
    }

    try:
        print(f"🔍 Searching with Scrapy for: {first_name} {last_name} @ {domain}")
        res = requests.post(url, json=payload, timeout=90)
        data = res.json()

        if not res.ok:
            print(f"❌ Scrapy service error: {data}")
            return None, 0, "api_error"

        if data.get("email"):
            email = data["email"]
            confidence = data.get("confidence", 0)
            verified = data.get("verified", False)
            print(f"✓ Found: {email} (confidence: {confidence}%, verified: {verified})")
            return (email, confidence, "scrapy+verification")
        else:
            print(f"⚠️ No email found: {data.get('message', 'no data')}")
    except requests.exceptions.Timeout:
        print(f"⏱️ Scrapy service timeout for {first_name} {last_name}")
        return None, 0, "timeout"
    except Exception as e:
        print(f"❌ Scrapy error for {first_name} {last_name}: {e}")

    return None, 0, "not_found"

@app.get("/scrape")
def scrape_journalists(topic: str = Query(...)):
    print(f"\n{'='*60}")
    print(f"Starting scrape for topic: {topic}")
    print(f"{'='*60}\n")

    journalists = scrape_journalists_from_publishers(topic)
    print(f"\nFound {len(journalists)} journalists from scraper\n")

    enriched = []
    MIN_CONFIDENCE = 70
    stats = {"verified": 0, "low_confidence": 0, "fallback": 0, "not_found": 0}

    for j in journalists:
        # Skip Hunter if no real author name
        if not j["first_name"] or not j["last_name"]:
            enriched.append({
                **j,
                "email": f"editor@{j['domain']}",
                "email_confidence": 0,
                "email_source": "fallback"
            })
            stats["fallback"] += 1
            continue

        email, confidence, source = find_email_with_scrapy(
            j["first_name"],
            j["last_name"],
            j["domain"]
        )

        # Reject low-confidence emails
        if not email or confidence < MIN_CONFIDENCE:
            enriched.append({
                **j,
                "email": f"editor@{j['domain']}",
                "email_confidence": confidence,
                "email_source": "low_confidence"
            })
            if confidence == 0:
                stats["not_found"] += 1
            else:
                stats["low_confidence"] += 1
            continue

        enriched.append({
            **j,
            "email": email,
            "email_confidence": confidence,
            "email_source": source
        })
        stats["verified"] += 1

    print(f"\n{'='*60}")
    print(f" Enrichment Summary:")
    print(f" Verified emails (>={MIN_CONFIDENCE}% confidence): {stats['verified']}")
    print(f" Low confidence emails: {stats['low_confidence']}")
    print(f" No email found: {stats['not_found']}")
    print(f" Fallback emails: {stats['fallback']}")
    print(f" Total journalists: {len(enriched)}")
    print(f"{'='*60}\n")

    return enriched
