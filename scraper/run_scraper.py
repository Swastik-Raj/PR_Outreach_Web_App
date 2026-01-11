import sys
import feedparser
import json
from urllib.parse import quote
import re

topic = sys.argv[1] if len(sys.argv) > 1 else "technology"

encoded_topic = quote(topic)

rss_url = f"https://news.google.com/rss/search?q={encoded_topic}"

feed = feedparser.parse(rss_url)

results = []

for entry in feed.entries[:10]:

    publication = entry.get("source", {}).get("title", "news")
    author = entry.get("author") or f"{publication} Editorial Team"

    safe_domain = re.sub(r"[^a-zA-Z0-9]", "", publication).lower()

    results.append({
        "name": author,
        "publication": publication,
        "article": entry.get("title", "Untitled Article"),
        "email": f"editor@{safe_domain}.com"
    })

print(json.dumps(results))


"""
PRODUCTION NOTE: Real Journalist Email Discovery :== Disabled for Demo

In a production system, journalist emails could be discovered using the
following steps. This logic is intentionally commented out to avoid
scraping private contact information during demos.

Steps:
1. Visit the article URL
2. Parse the HTML page
3. Locate author profile link
4. Visit author profile page
5. Extract email from:
   - mailto: links
   - contact sections
   - author bio blocks
"""

# import requests
# from bs4 import BeautifulSoup
#
# article_url = entry.get("link")
# response = requests.get(article_url, timeout=10)
# soup = BeautifulSoup(response.text, "html.parser")
#
# # Example patterns commonly used by publishers:
# # <a href="mailto:author@publication.com">
# mailto = soup.select_one("a[href^='mailto:']")
#
# if mailto:
#     email = mailto["href"].replace("mailto:", "")
#
# else:
#     # Fallback: Visit author profile page
#     author_link = soup.select_one("a.author, a.byline")
#     if author_link:
#         profile_url = author_link["href"]
#         profile_page = requests.get(profile_url)
#         profile_soup = BeautifulSoup(profile_page.text, "html.parser")
#
#         email_element = profile_soup.find(text=lambda t: "@" in t)
#         email = email_element if email_element else None
#
# # Final fallback: domain-based guessing + verification
# # email = f"{first_name}.{last_name}@publication.com"
