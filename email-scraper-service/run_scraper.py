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
    """
    Parse a full name string into (first_name, last_name) tuples.
    Handles multiple authors separated by 'and', '&', or commas.
    Returns a list of (first_name, last_name) tuples.
    """
    if not full_name:
        return []

    bad_terms = ["Editorial", "Staff", "Team", "Newsroom"]
    if any(bad.lower() in full_name.lower() for bad in bad_terms):
        return []

    # Split by common delimiters for multiple authors
    # Handle patterns like: "John Doe and Jane Smith" or "A, B and C"
    import re

    # Replace various separators with a uniform delimiter
    normalized = full_name
    normalized = re.sub(r'\s+and\s+', '|', normalized, flags=re.IGNORECASE)
    normalized = re.sub(r'\s*&\s*', '|', normalized)

    # Split by the delimiter
    author_names = [name.strip() for name in normalized.split('|')]

    # Also handle comma-separated lists (but not commas within names)
    # This handles "Smith, Jones and Brown"
    expanded_names = []
    for name in author_names:
        # Check if this looks like "Last1, Last2, Last3" pattern
        if ',' in name:
            parts = [p.strip() for p in name.split(',')]
            # If all parts are single words (likely last names only), skip
            if all(len(p.split()) == 1 for p in parts):
                continue
            expanded_names.extend(parts)
        else:
            expanded_names.append(name)

    # Parse each individual name
    results = []
    for name in expanded_names:
        name = name.strip()
        if not name:
            continue

        parts = name.split()
        if len(parts) == 1:
            # Single name - use as first name only
            results.append((parts[0], ""))
        elif len(parts) >= 2:
            # Multiple parts - first is first_name, rest is last_name
            first = parts[0]
            last = " ".join(parts[1:])
            results.append((first, last))

    return results


def scrape_journalists_from_publishers(topic: str, geography: str = None):
    journalists = defaultdict(lambda: {
        "first_name": "",
        "last_name": "",
        "publication_name": "",
        "domain": "",
        "topics": set(),
        "recent_articles": []
    })

    # Filter publishers by geography if specified
    publishers_to_scrape = PUBLISHERS
    if geography and geography.strip():
        geography_lower = geography.lower().strip()

        # Map common geography terms to publisher regions
        region_mapping = {
            'us': ['Northeast', 'West Coast', 'National', 'Midwest', 'Southeast', 'Southwest',
                   'Mid-Atlantic', 'Mountain West', 'Pacific Northwest'],
            'usa': ['Northeast', 'West Coast', 'National', 'Midwest', 'Southeast', 'Southwest',
                    'Mid-Atlantic', 'Mountain West', 'Pacific Northwest'],
            'united states': ['Northeast', 'West Coast', 'National', 'Midwest', 'Southeast', 'Southwest',
                              'Mid-Atlantic', 'Mountain West', 'Pacific Northwest'],
            'northeast': ['Northeast'],
            'west coast': ['West Coast'],
            'east coast': ['Northeast', 'Mid-Atlantic'],
            'national': ['National'],
            'midwest': ['Midwest'],
            'south': ['Southeast', 'Southwest'],
            'southeast': ['Southeast'],
            'southwest': ['Southwest'],
            'mid-atlantic': ['Mid-Atlantic'],
            'mountain west': ['Mountain West'],
            'pacific northwest': ['Pacific Northwest'],
            'global': None,  # None means all publishers
            'international': ['International']
        }

        # Get matching regions
        matching_regions = region_mapping.get(geography_lower)

        if matching_regions is not None:
            # Filter publishers by matching regions
            publishers_to_scrape = [
                pub for pub in PUBLISHERS
                if pub.get('region') in matching_regions
            ]
            print(f"Filtered to {len(publishers_to_scrape)} publishers for geography '{geography}'")
            print(f"Regions included: {matching_regions}")
        else:
            # If geography specified but not recognized, try partial match on region
            publishers_to_scrape = [
                pub for pub in PUBLISHERS
                if geography_lower in pub.get('region', '').lower()
            ]
            if publishers_to_scrape:
                print(f"Partial match: {len(publishers_to_scrape)} publishers for geography '{geography}'")
            else:
                print(f"Geography '{geography}' not recognized, using all publishers")
                publishers_to_scrape = PUBLISHERS

    for idx, pub in enumerate(publishers_to_scrape, 1):
        print(f"[{idx}/{len(publishers_to_scrape)}] Fetching RSS from {pub['name']}...")
        try:
            feed = feedparser.parse(pub["rss"])
            print(f"  Found {len(feed.entries)} articles")
        except Exception as e:
            print(f"  ERROR fetching {pub['name']}: {e}")
            continue

        for entry in feed.entries[:20]:
            author_raw = extract_author(entry, pub["author_fields"])
            parsed_authors = parse_name(author_raw)

            if not parsed_authors:
                continue

            # Create separate entries for each co-author
            for first_name, last_name in parsed_authors:
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
