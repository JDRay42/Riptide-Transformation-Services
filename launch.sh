#!/bin/bash

# Script for development use to lauch the app.  In production, use a WSGI server such as Gunicorn.

# Source the environment variables
source .env

# Start the Uvicorn server with the specified settings and SSL paths
uvicorn src.main:app --host 0.0.0.0 --port $PORT --ssl-keyfile=$SSL_KEY_PATH --ssl-certfile=$SSL_CERT_PATH
