import re
import requests

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def find_email(url):
    html = requests.get(url).text
    emails = re.findall(EMAIL_REGEX, html)
    return emails[0] if emails else None