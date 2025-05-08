#!/bin/bash

# Start the backend server in the background
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8081 &

# Give the server a moment to start (optional)
sleep 2

# Ask the user if they want to run the RSS scraping
read -p "Do you want to run the RSS scraping? (Y/N): " answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Running RSS scraping..."
    python backend/app/run_rss_scraper.py
else
    echo "Skipping RSS scraping."
fi

# Wait for the backend server to finish
wait