@echo off
REM Quick setup script for backend with Supabase (Windows)

echo 🚀 AI Help Desk Backend Setup
echo ==============================
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please create .env file from .env.example and configure:
    echo   - DATABASE_URL (Supabase connection string^)
    echo   - OPENAI_API_KEY or ANTHROPIC_API_KEY
    echo.
    echo Run: copy .env.example .env
    echo Then edit .env with your credentials
    exit /b 1
)

echo ✅ .env file found
echo.

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment exists
)

echo.

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements.txt
pip install -q python-frontmatter

echo ✅ Dependencies installed
echo.

REM Create database tables
echo 🗄️  Creating database tables...
python init_db.py --create

if errorlevel 1 (
    echo ❌ Failed to create database tables
    exit /b 1
)

echo.

REM Verify database setup
echo 🔍 Verifying database setup...
python init_db.py --verify

if errorlevel 1 (
    echo ❌ Database verification failed
    exit /b 1
)

echo.

REM Ingest KB documents
echo 📚 Ingesting knowledge base documents...
python -m app.kb.ingestion --ingest

if errorlevel 1 (
    echo ❌ KB ingestion failed
    exit /b 1
)

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start the server, run:
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo    python -m app.kb.ingestion --ingest
echo 📖 API documentation will be available at:
echo    http://localhost:8000/docs
