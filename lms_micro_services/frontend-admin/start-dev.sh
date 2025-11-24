#!/bin/bash

# Learnhub Frontend - Development Quick Start Script

echo "============================================"
echo "   Learnhub Frontend - Quick Start"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found."
    echo "Please run this script from the learnhub-frontend directory:"
    echo "cd /home/huynguyen/lms_mcsrv_runwell/lms_micro_services/learnhub-frontend"
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install failed. Please check the errors above."
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "🚀 Starting development server..."
echo ""
echo "Access the application at: http://localhost:5173"
echo "Admin login page: http://localhost:5173/login"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "============================================"
echo ""

npm run dev
