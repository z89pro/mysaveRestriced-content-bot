#!/bin/bash

# Start Gunicorn (Web Server) in the background
# This listens on the PORT provided by the cloud platform
gunicorn app:app --bind 0.0.0.0:$PORT &

# Start the Telegram Bot in the foreground
python3 bot.py