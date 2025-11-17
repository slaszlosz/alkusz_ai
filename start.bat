@echo off
echo ========================================
echo  AlkuszAI Inditas
echo ========================================
echo.

echo Ellenorzes: Python es Node.js telepitve van-e...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [HIBA] Python nincs telepitve!
    echo Telepitsd innen: https://www.python.org/downloads/
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [HIBA] Node.js nincs telepitve!
    echo Telepitsd innen: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python es Node.js megtalalhato
echo.

echo Ellenorzes: OpenAI API kulcs beallitva...
findstr /C:"your-openai-api-key-here" .env >nul
if %errorlevel% equ 0 (
    echo [FIGYELEM] OpenAI API kulcs nincs beallitva!
    echo Szerkeszd a .env fajlt es add meg az API kulcsodat.
    echo.
    pause
)

echo ========================================
echo  Backend inditasa...
echo ========================================
start "AlkuszAI Backend" cmd /k "cd backend && (venv\Scripts\activate.bat 2>nul || python -m venv venv && venv\Scripts\activate.bat) && pip install -q -r requirements.txt && cd .. && python -m uvicorn app.main:app --reload --app-dir backend"

timeout /t 5 /nobreak >nul

echo ========================================
echo  Frontend inditasa...
echo ========================================
start "AlkuszAI Frontend" cmd /k "cd frontend && (if not exist node_modules npm install) && npm run dev"

echo.
echo ========================================
echo  Inditva!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo A bongeszo automatikusan megnyilik 10 masodperc mulva...
echo.

timeout /t 10 /nobreak
start http://localhost:5173

echo Bezarhatod ezt az ablakot.
pause
