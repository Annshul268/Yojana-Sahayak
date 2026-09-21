#!/usr/bin/env bash
set -e

echo "Starting Yojana Sahayak development servers..."

# Ensure we are in project root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Source virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$ROOT_DIR"

echo "Starting FastAPI Backend on http://127.0.0.1:8000..."
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Streamlit Frontend on http://127.0.0.1:8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1 &
FRONTEND_PID=$!

cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
}

trap cleanup EXIT INT TERM

wait
