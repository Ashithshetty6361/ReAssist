@echo off
setlocal
echo ========================================
echo   ReAssist - Backend Server (FastAPI)
echo ========================================
echo.

:: Check if .env exists
if not exist ".env" (
    echo [!] .env file not found. Copying from .env.example...
    copy .env.example .env
    echo [!] Please edit .env with your configuration, then run this script again.
    pause
    exit /b 1
)

:: Check Ollama if provider is ollama
findstr /i "LLM_PROVIDER=ollama" .env >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Checking Ollama status...
    ollama list >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Ollama is not running. Please start Ollama first (ollama serve).
        echo     Download from: https://ollama.ai
        pause
        exit /b 1
    )
    echo [+] Ollama is active.
)

:: Check port 8000 / 8001
set "BACKEND_PORT=8000"
netstat -ano | findstr /r ":8000 .*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] Port 8000 is occupied. Falling back to port 8001...
    set "BACKEND_PORT=8001"
)

echo [*] Launching Uvicorn server on port %BACKEND_PORT%...
echo [*] Interactive Swagger Docs: http://localhost:%BACKEND_PORT%/docs
echo.
python -m uvicorn src.api.app:app --reload --port %BACKEND_PORT%

