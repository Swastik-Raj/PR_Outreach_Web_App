# Geography Filtering Guide

The Target Geography field in the Campaign & Scraper page now filters which RSS feeds are scraped based on publisher regions.

## How It Works

When you enter a geography value, the system filters the list of publishers to only scrape from those matching your specified region(s).

## Supported Geography Values

### US Coverage
- `US`, `USA`, or `United States` - Scrapes all US-based publishers (excludes International)

### Specific US Regions
- `Northeast` - NY Times, The Verge, WSJ, Fast Company, MIT Tech Review, Boston Globe, Philadelphia Inquirer
- `West Coast` - TechCrunch, Wired, CNET, VentureBeat, LA Times, SF Chronicle, San Diego Union-Tribune, Sacramento Bee, Silicon Valley Business Journal, The Information
- `East Coast` - Includes Northeast + Mid-Atlantic regions
- `Mid-Atlantic` - Washington Post
- `Southeast` - CNN Business, Miami Herald, Atlanta Journal-Constitution, Charlotte Observer
- `Southwest` - Dallas Morning News, Houston Chronicle, Austin American-Statesman, Arizona Republic
- `Midwest` - Chicago Tribune, Detroit Free Press, Minneapolis Star Tribune
- `Mountain West` - Denver Post
- `Pacific Northwest` - Seattle Times, Portland Oregonian
- `National` - Reuters, Ars Technica, Engadget, ZDNet, Forbes, USA Today, Mashable (national/multi-region publishers)

### International
- `International` - BBC Technology (non-US sources)
- `Global` - All publishers including international

### Empty/Blank
If you leave the Target Geography field empty, all publishers will be scraped (same as selecting "Global").

## Examples

- **"US"** → Scrapes all 40+ US-based RSS feeds (excludes BBC)
- **"West Coast"** → Scrapes TechCrunch, Wired, CNET, LA Times, SF Chronicle, etc. (10+ feeds)
- **"Northeast"** → Scrapes NY Times, WSJ, Boston Globe, etc. (7+ feeds)
- **"International"** → Scrapes only BBC Technology
- **"Global"** or blank → Scrapes all available feeds

## Technical Details

The geography parameter is passed through:
1. Frontend (`CampaignScraper.jsx`) → API client
2. Backend (`controller.js`) → Scraper service
3. Scraper service (`app.py`, `run_scraper.py`) → Filters publishers by region

Each publisher in `publishers.py` has a `region` field that determines which geography filters will include it.
