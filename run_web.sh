#!/bin/bash

# Kill any existing processes on ports 8000 and 3000
fuser -k 8000/tcp
fuser -k 3000/tcp

echo "🚀 Starting Riko Web Backend..."
cd server
/home/nimuthu/elite-ai/bin/python api.py &
BACKEND_PID=$!

echo "🎨 Starting Riko Web Frontend..."
cd ../client
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✨ Riko is ready!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
