## Setup

### Backend
cd backend
npm install
cp src/.env.example src/.env
npm start

### Frontend
cd frontend
npm install
npm run dev

### Scraper
cd scraper
pip install feedparser
python run_scraper.py "AI Teaching Tools"
