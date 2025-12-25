#!/bin/bash

# Start Flask API in background
echo "Starting Flask API on http://localhost:5001..."
uv run python -m backend.api.app &
FLASK_PID=$!

# Wait for Flask to start
sleep 2

# Start React dev server
echo "Starting React frontend on http://localhost:5173..."
cd frontend && npm run dev &
VITE_PID=$!

echo ""
echo "Both servers are running!"
echo "Flask API: http://localhost:5001"
echo "React App: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $VITE_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
