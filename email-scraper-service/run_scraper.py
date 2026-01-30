import feedparser
from collections import defaultdict
from publishers import PUBLISHERS
from urllib.parse import urlparse


def extract_author(entry, author_fields):
    for field in author_fields:
        value = entry.get(field)
        if value:
            return value.replace("By ", "").strip()
    return ""

def parse_name(full_name):
    if not full_name:
        return "", ""

    bad_terms = ["Editorial", "Staff", "Team", "Newsroom"]
    if any(bad.lower() in full_name.lower() for bad in bad_terms):
        return "", ""

    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def scrape_journalists_from_publishers(topic: str):
    journalists = defaultdict(lambda: {
        "first_name": "",
        "last_name": "",
        "publication_name": "",
        "domain": "",
        "topics": set(),
        "recent_articles": []
    })

    for pub in PUBLISHERS:
        feed = feedparser.parse(pub["rss"])

        for entry in feed.entries[:20]:
            author_raw = extract_author(entry, pub["author_fields"])
            first_name, last_name = parse_name(author_raw)

            if not first_name:
                continue

            key = f"{first_name}-{last_name}-{pub['domain']}"

            journalist = journalists[key]
            journalist["first_name"] = first_name
            journalist["last_name"] = last_name
            journalist["publication_name"] = pub["name"]
            journalist["domain"] = pub["domain"]

            journalist["recent_articles"].append({
                "title": entry.get("title", ""),
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
