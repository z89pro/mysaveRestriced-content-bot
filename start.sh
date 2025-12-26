#!/bin/bash

# Wait for PORT env var (required by cloud platforms)
: "${PORT:=8000}"

# Start Gunicorn in background and capture PID
gunicorn app:app --bind 0.0.0.0:"$PORT" --workers 2 --timeout 120 &
GUNICORN_PID=$!

# Start Telegram bot in background and capture PID
python3 bot.py &
BOT_PID=$!

# Log PIDs for debugging
echo "Gunicorn PID: $GUNICORN_PID on port $PORT"
echo "Bot PID: $BOT_PID"

# Wait for either process to exit, then shutdown cleanly
wait -n $GUNICORN_PID $BOT_PID

# Kill the other process and exit with failure code
kill $GUNICORN_PID $BOT_PID 2>/dev/null
exit 1
