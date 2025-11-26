#!/bin/bash

# Quick setup script for backend with Supabase

echo "🚀 AI Help Desk Backend Setup"
echo "=============================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file from .env.example and configure:"
    echo "  - DATABASE_URL (Supabase connection string)"
    echo "  - OPENAI_API_KEY or ANTHROPIC_API_KEY"
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your credentials"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q python-frontmatter

echo "✅ Dependencies installed"
echo ""

# Create database tables
echo "🗄️  Creating database tables..."
python init_db.py --create

if [ $? -ne 0 ]; then
    echo "❌ Failed to create database tables"
    exit 1
fi

echo ""

# Verify database setup
echo "🔍 Verifying database setup..."
python init_db.py --verify

if [ $? -ne 0 ]; then
    echo "❌ Database verification failed"
    exit 1
fi

echo ""

# Ingest KB documents
echo "📚 Ingesting knowledge base documents..."
python -m app.kb.ingestion --ingest

if [ $? -ne 0 ]; then
    echo "❌ KB ingestion failed"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server, run:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 API documentation will be available at:"
echo "   http://localhost:8000/docs"
