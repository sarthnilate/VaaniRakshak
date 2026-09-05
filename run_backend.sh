#!/bin/bash
# ============================================================
# VAANIRAKSHAK — Backend Server Launcher
# ============================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo "🛡️  VAANIRAKSHAK — Live Threat Defense Engine"
echo "=================================================="

if [ ! -d "backend/venv" ]; then
    echo "⚠️  Creating Python virtual environment..."
    python3 -m venv backend/venv
    source backend/venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r backend/requirements.txt
else
    source backend/venv/bin/activate
fi

export PYTHONPATH="$DIR"
echo "🚀 Starting FastAPI server at http://127.0.0.1:8000 ..."
echo "📖 Interactive API docs at http://127.0.0.1:8000/docs"
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
