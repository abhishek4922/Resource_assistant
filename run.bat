@echo off
echo ========================================
echo AI Operations Assistant - Setup
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your GROQ_API_KEY
    echo Get your free API key from: https://console.groq.com/
    echo.
    pause
    exit /b 1
)

REM Check if GROQ_API_KEY is set
findstr /C:"GROQ_API_KEY=" .env | findstr /V /C:"GROQ_API_KEY=$" >nul
if errorlevel 1 (
    echo ERROR: GROQ_API_KEY not found in .env file
    echo Please edit .env and add your API key
    echo.
    pause
    exit /b 1
)

echo Starting AI Operations Assistant...
echo.
streamlit run main.py

pause
