#!/bin/sh
set -e

uvicorn api_server:app --host 0.0.0.0 --port 8080 &

exec streamlit run main.py --server.address=0.0.0.0 --server.port=8501
