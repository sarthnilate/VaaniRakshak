#!/bin/bash
# ============================================================
# VAANIRAKSHAK — Live Security Command Center Dashboard Launcher
# ============================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/dashboard"

echo "=================================================="
echo "📊 VAANIRAKSHAK — React Security Dashboard"
echo "=================================================="

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

echo "🚀 Starting Vite Dev Server on http://localhost:5173 ..."
exec npm run dev
