#!/bin/sh

# Start the Flask app
python3 order_handler.py &

# Start the HTTP server on 0.0.0.0
python3 -m http.server 8000 --bind 0.0.0.0