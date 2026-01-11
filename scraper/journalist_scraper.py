import requests
from bs4 import BeautifulSoup

def scrape_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    for item in soup.select("article"):
        title = item.find("h2").get_text()
        link = item.find("a")["href"]
        articles.append({
            "title": title,
            "url": link
        })

    return articles