#!/bin/bash

echo "🚀 Starting AI Civilization Simulator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your ANTHROPIC_API_KEY!"
    echo "   Then run this script again."
    exit 1
fi

# Start backend server in background
echo "🌐 Starting FastAPI server..."
python server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Start simulation in background
echo "🌍 Starting simulation..."
python main.py &
SIM_PID=$!

# Frontend setup
echo "🎨 Setting up frontend..."
cd ../frontend

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    kill $SERVER_PID $SIM_PID
    exit 1
fi

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend dev server
echo "💻 Starting frontend dev server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ All systems started!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "🖥️  Frontend: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for Ctrl+C
trap "echo 'Stopping servers...'; kill $SERVER_PID $SIM_PID $FRONTEND_PID; exit" INT

wait