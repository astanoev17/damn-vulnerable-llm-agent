#!/bin/sh
set -e

# Start API on 8080
uvicorn api_server:app --host 0.0.0.0 --port 8080 &

# Start Streamlit on 8501 (your UI)
exec streamlit run main.py --server.address=0.0.0.0 --server.port=8501
