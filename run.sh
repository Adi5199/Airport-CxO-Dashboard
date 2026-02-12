#!/bin/bash
set -e

echo "======================================"
echo "  BIAL Airport Operations Dashboard"
echo "  GenAI-Powered Executive Insights"
echo "======================================"
echo ""

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Use venv Python if available, otherwise system Python
if [ -f "$ROOT_DIR/.venv/bin/python3" ]; then
    PYTHON="$ROOT_DIR/.venv/bin/python3"
    PIP="$ROOT_DIR/.venv/bin/pip3"
elif [ -f "$ROOT_DIR/venv/bin/python3" ]; then
    PYTHON="$ROOT_DIR/venv/bin/python3"
    PIP="$ROOT_DIR/venv/bin/pip3"
else
    PYTHON="python3"
    PIP="pip3"
fi
echo "[*] Using Python: $PYTHON"

# Check/generate data
if [ ! -d "$ROOT_DIR/data/generated" ] || [ -z "$(ls -A "$ROOT_DIR/data/generated" 2>/dev/null)" ]; then
    echo "[*] Generating mock data..."
    cd "$ROOT_DIR/data/generators" && "$PYTHON" generate_all_data.py && cd "$ROOT_DIR"
    echo "[+] Data generated."
fi

# Install backend deps if needed
if ! "$PYTHON" -c "import fastapi" 2>/dev/null; then
    echo "[*] Installing backend dependencies..."
    "$PIP" install -r "$ROOT_DIR/backend/requirements.txt" -q
fi

# Install frontend deps if needed
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
    echo "[*] Installing frontend dependencies..."
    cd "$ROOT_DIR/frontend" && npm install --silent && cd "$ROOT_DIR"
fi

# Kill any existing processes on our ports
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend
echo "[*] Starting FastAPI backend on port 8000..."
cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR" "$PYTHON" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --log-level warning &
BACKEND_PID=$!

# Wait for backend to be ready
echo "[*] Waiting for backend..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "[+] Backend ready."
        break
    fi
    sleep 1
done

# Start frontend
echo "[*] Starting Next.js frontend on port 3000..."
cd "$ROOT_DIR/frontend" && npm run dev -- -p 3000 &
FRONTEND_PID=$!

sleep 3

echo ""
echo "======================================"
echo "  Dashboard: http://localhost:3000"
echo "  API Docs:  http://localhost:8000/docs"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop both services"

cleanup() {
    echo ""
    echo "[*] Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "[+] Done."
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
