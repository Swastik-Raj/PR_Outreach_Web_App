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
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        text_content = response.xpath('//body//text()').getall()
        page_text = ' '.join(text_content)

        emails = re.findall(email_regex, page_text)

        for email in emails:
            email = email.lower()
            if email not in self.found_emails and self.domain in email:
                self.found_emails.append(email)

                score = self._calculate_match_score(email)
                yield {
                    'email': email,
                    'source_url': response.url,
                    'match_score': score,
                    'match_type': self._get_match_type(email)
                }

        for href in response.css('a::attr(href)').getall():
            if any(keyword in href.lower() for keyword in ['about', 'team', 'contact', 'staff', 'author', 'people']):
                yield response.follow(href, self.parse)

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
