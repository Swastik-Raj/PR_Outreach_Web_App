from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape")
def scrape_journalists(topic: str = Query(...)):
    """
    Replace this logic with your real scraper
    """

    # TEMP MOCK (replace with real scraping)
    journalists = [
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@publication.com",
            "publication_name": "Tech Weekly",
            "recent_articles": [
                {
                    "title": f"{topic} trends in 2024",
                    "url": "https://example.com/article"
                }
            ]
        }
    ]

    return journalists
