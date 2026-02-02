BOT_NAME = 'email-finder'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 1

USER_AGENT = 'Mozilla/5.0 (compatible; EmailFinderBot/1.0; +http://emailfinder.local)'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

DEPTH_LIMIT = 3

CLOSESPIDER_PAGECOUNT = 20

LOG_LEVEL = 'WARNING'

ITEM_PIPELINES = {}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10

HTTPCACHE_ENABLED = False
