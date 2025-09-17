#!/bin/bash

# Start FastAPI app using uvicorn
# make sure it autorestarts on code changes for development
uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload