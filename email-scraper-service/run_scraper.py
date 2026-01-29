import feedparser
from urllib.parse import quote
import re
from collections import defaultdict

def parse_name(full_name):
    if not full_name or "Editorial" in full_name or "Team" in full_name:
        return "", ""

    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

def extract_topics(title, summary=""):
    topic_keywords = [
        "artificial intelligence", "ai", "machine learning", "ml",
        "education", "edtech", "technology", "startup",
        "data science", "analytics", "automation",
        "chatgpt", "gpt", "llm", "generative ai",
        "cloud computing"
    ]

    text = (title + " " + summary).lower()
    return [kw.title() for kw in topic_keywords if kw in text]

def get_publication_location(publication):
    location_map = {
        "TechCrunch": {"city": "San Francisco", "state": "CA", "country": "USA"},
        "The Verge": {"city": "New York", "state": "NY", "country": "USA"},
    }

    return location_map.get(publication, {
        "city": "New York",
        "state": "NY",
        "country": "USA"
    })

def extract_domain(publication):
    safe = re.sub(r"[^a-zA-Z0-9]", "", publication).lower()
    return f"{safe}.com"

def scrape_journalists_from_topic(topic: str):
    encoded_topic = quote(topic)
    rss_url = f"https://news.google.com/rss/search?q={encoded_topic}"
    feed = feedparser.parse(rss_url)

    journalists = defaultdict(lambda: {
        "first_name": "",
        "last_name": "",
        "publication_name": "",
        "domain": "",
        "city": "",
        "state": "",
        "country": "",
        "topics": set(),
        "recent_articles": []
    })

    for entry in feed.entries[:20]:
        publication = entry.get("source", {}).get("title", "news")
        author = entry.get("author")

        if not author or "Editorial" in author or "Team" in author:
            continue

        first_name, last_name = parse_name(author)
        domain = extract_domain(publication)
        location = get_publication_location(publication)

        article_title = entry.get("title", "")
        article_summary = entry.get("summary", "")
        topics = extract_topics(article_title, article_summary)

        key = f"{first_name}-{last_name}-{publication}"
        journalist = journalists[key]

        journalist.update({
            "first_name": first_name,
            "last_name": last_name,
            "publication_name": publication,
            "domain": domain,
            "city": location["city"],
            "state": location["state"],
            "country": location["country"],
        })

        journalist["topics"].update(topics)
        journalist["recent_articles"].append({
            "title": article_title,
            "url": entry.get("link", ""),
            "published": entry.get("published", "")
        })

    return [
        {
            **j,
            "topics": list(j["topics"]),
            "recent_articles": j["recent_articles"][:5]
        }
        for j in journalists.values()
    ]
