@echo off
set "PATH=C:\Program Files\nodejs;%PATH%"
echo ========================================
echo   ReAssist - Research Intelligence Engine
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
    echo [*] Checking Ollama...
    ollama list >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Ollama is not running. Please start Ollama first.
        echo     Download from: https://ollama.ai
        pause
        exit /b 1
    )
    echo [+] Ollama is running.
)

:: Check if port 8000 is in use
set "BACKEND_PORT=8000"
netstat -ano | findstr /r ":8000 .*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] Port 8000 is in use. Using port 8001 for Backend...
    set "BACKEND_PORT=8001"
)

:: Set frontend env
echo NEXT_PUBLIC_API_URL=http://localhost:%BACKEND_PORT% > frontend\.env.local

:: Start Backend
echo.
echo [*] Starting FastAPI Backend on port %BACKEND_PORT%...
start "ReAssist Backend" cmd /k "python -m uvicorn src.api.app:app --reload --port %BACKEND_PORT%"

:: Wait for backend to be ready
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [*] Starting Next.js Frontend on port 3000...
cd frontend
if not exist "node_modules" (
    echo [*] Installing frontend dependencies...
    call npm install
)
start "ReAssist Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   ReAssist is starting up!
echo   Backend:  http://localhost:%BACKEND_PORT%
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:%BACKEND_PORT%/docs
echo ========================================
echo.
echo Press any key to stop all servers...
pause >nul

:: Cleanup
taskkill /fi "WINDOWTITLE eq ReAssist Backend" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq ReAssist Frontend" /f >nul 2>&1
echo [*] All servers stopped.
