#!/bin/bash

echo "Starting Scrapy Email Service..."
echo "================================"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Starting service on port 5002..."
echo "================================"
python app.py
