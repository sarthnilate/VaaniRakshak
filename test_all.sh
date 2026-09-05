#!/bin/bash
# ============================================================
# VAANIRAKSHAK — Full Verification & Security Test Runner
# ============================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=================================================="
echo "🛡️  VAANIRAKSHAK — Running All Automated Test Suites"
echo "=================================================="

source backend/venv/bin/activate
export PYTHONPATH="$DIR"

echo "🧪 Running Backend Unit, AI Pipeline, Temporal Risk, Attack Lab, Benchmark & Security Tests..."
pytest backend/tests/ -v --tb=short

echo ""
echo "⚛️  Verifying Dashboard TypeScript Build..."
cd dashboard
npm run build

echo ""
echo "=================================================="
echo "✅ ALL VERIFICATION GATES PASSED (100% GREEN)!"
echo "=================================================="
