#!/bin/bash
# Kill any running uvicorn process for main:app
pkill -f "uvicorn main:app" 2>/dev/null
cd backend/app
uvicorn main:app --reload --host 0.0.0.0 --port 8081 