#!/bin/bash
# Quick test script for MVLT AI Service

PORT=${1:-8001}

echo "🚀 Starting MVLT AI Service on port $PORT..."
echo ""

cd "$(dirname "$0")"
source venv/bin/activate

# Start server in background
python -m uvicorn app.main:app --port $PORT > server.log 2>&1 &
SERVER_PID=$!

echo "Server PID: $SERVER_PID"
echo "Waiting for server to start..."
sleep 3

# Test health endpoint
echo ""
echo "📡 Testing health endpoint..."
curl -s http://localhost:$PORT/health | python3 -m json.tool

echo ""
echo ""
echo "✅ Server is running!"
echo ""
echo "📚 View API docs: http://localhost:$PORT/docs"
echo "🔍 Health check: http://localhost:$PORT/health"
echo ""
echo "To stop the server:"
echo "  kill $SERVER_PID"
echo ""
echo "Server logs in: server.log"
