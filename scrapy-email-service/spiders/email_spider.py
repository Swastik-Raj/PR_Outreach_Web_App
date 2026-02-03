import scrapy
import re
from urllib.parse import urljoin, urlparse

class EmailSpider(scrapy.Spider):
    name = 'email_finder'

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (compatible; EmailFinderBot/1.0)',
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 20,
    }

    def __init__(self, domain=None, first_name=None, last_name=None, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)
        self.domain = domain
        self.first_name = first_name.lower() if first_name else None
        self.last_name = last_name.lower() if last_name else None
        self.start_urls = [f'https://{domain}']
        self.allowed_domains = [domain]
        self.found_emails = []

        self.email_patterns = self._generate_email_patterns()

        print(f'[EmailSpider] Initialized for {first_name} {last_name} @ {domain}', flush=True)
        print(f'[EmailSpider] Start URLs: {self.start_urls}', flush=True)
        print(f'[EmailSpider] Looking for patterns: {self.email_patterns[:3]}...', flush=True)

    def _generate_email_patterns(self):
        if not self.first_name or not self.last_name:
            return []

        f = self.first_name
        l = self.last_name
        d = self.domain

        patterns = [
            f'{f}.{l}@{d}',
            f'{f}{l}@{d}',
            f'{f}_{l}@{d}',
            f'{f}-{l}@{d}',
            f'{f}@{d}',
            f'{l}@{d}',
            f'{f[0]}{l}@{d}',
            f'{f}{l[0]}@{d}',
            f'{f[0]}.{l}@{d}',
        ]
        return patterns

    def parse(self, response):
        self.logger.info(f'[spider] Parsing URL: {response.url}')

        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        text_content = response.xpath('//body//text()').getall()
        page_text = ' '.join(text_content)

        emails = re.findall(email_regex, page_text)
        self.logger.info(f'[spider] Found {len(emails)} potential emails on {response.url}')

        for email in emails:
            email = email.lower()
            if email not in self.found_emails and self.domain in email:
                self.found_emails.append(email)

                score = self._calculate_match_score(email)
                self.logger.info(f'[spider] Yielding email: {email} (score: {score})')
                yield {
                    'email': email,
                    'source_url': response.url,
                    'match_score': score,
                    'match_type': self._get_match_type(email)
                }

        # Follow links with keywords or author pages
        keywords = ['about', 'team', 'contact', 'staff', 'author', 'people', 'writers', 'contributors', 'editorial']

        # Also look for the person's name in URLs
        name_patterns = []
        if self.first_name and self.last_name:
            name_patterns = [
                self.first_name,
                self.last_name,
                f'{self.first_name}-{self.last_name}',
                f'{self.first_name}.{self.last_name}',
                f'{self.first_name}_{self.last_name}'
            ]

        links_followed = 0
        for href in response.css('a::attr(href)').getall():
            href_lower = href.lower()

            # Check keywords or name patterns
            should_follow = any(keyword in href_lower for keyword in keywords)
            should_follow = should_follow or any(pattern in href_lower for pattern in name_patterns)

            if should_follow:
                links_followed += 1
                yield response.follow(href, self.parse)

        self.logger.info(f'[spider] Following {links_followed} links from {response.url}')

    def _calculate_match_score(self, email):
        if not self.first_name or not self.last_name:
            return 50

        email_local = email.split('@')[0].lower()

        if email in self.email_patterns:
            return 100

        f_in = self.first_name in email_local
        l_in = self.last_name in email_local

        if f_in and l_in:
            return 95
        elif f_in or l_in:
            return 75
        else:
            return 50

    def _get_match_type(self, email):
        if not self.first_name or not self.last_name:
            return 'domain_match'

        email_local = email.split('@')[0].lower()

        if email in self.email_patterns:
            return 'pattern_exact'

        f_in = self.first_name in email_local
        l_in = self.last_name in email_local

        if f_in and l_in:
            return 'name_match'
        elif f_in or l_in:
            return 'partial_match'
        else:
            return 'domain_match'
