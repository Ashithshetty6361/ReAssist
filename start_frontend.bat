@echo off
setlocal
set "PATH=C:\Program Files\nodejs;%PATH%"
echo ========================================
echo   ReAssist - Frontend Server (Next.js)
echo ========================================
echo.

cd frontend

:: Ensure dependencies exist
if not exist "node_modules" (
    echo [*] Node modules not found. Running npm install...
    call npm install
)

:: Set default backend target if not set
if not exist ".env.local" (
    echo [*] Creating .env.local targeting http://localhost:8000...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
)

echo [*] Starting Next.js Dev Server (Turbopack) on port 3000...
echo [*] Open browser to: http://localhost:3000
echo.
npm run dev

