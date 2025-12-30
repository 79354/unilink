@echo off
REM UniLink Backend - Windows Startup Script
REM Starts all three services: Main API, Chat Service, and Notification Service

title UniLink Backend

color 0B
echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║                                                      ║
echo ║           UniLink Backend Startup                    ║
echo ║                                                      ║
echo ╚══════════════════════════════════════════════════════╝
echo.

REM Set directories
set MAIN_DIR=%cd%\app
set CHAT_DIR=%cd%\chat-service
set NOTIF_DIR=%cd%\notification-service
set LOG_DIR=%cd%\logs

REM Create log directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Check MongoDB
echo [1/5] Checking MongoDB...
mongosh --eval "db.adminCommand('ping')" --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] MongoDB is not running!
    echo Please start MongoDB first.
    pause
    exit /b 1
)
echo [OK] MongoDB is running

REM Check Redis
echo [2/5] Checking Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Redis is not running!
    echo Please start Redis first.
    pause
    exit /b 1
)
echo [OK] Redis is running

REM Build Notification Service
echo [3/5] Building Notification Service...
cd "%NOTIF_DIR%"
go mod download
go build -o notification-service.exe cmd\server\main.go
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build notification service!
    pause
    exit /b 1
)
echo [OK] Notification service built
cd "%cd%\.."

REM Start Main API
echo [4/5] Starting Main API (Port 3001)...
cd "%MAIN_DIR%"
start "Main API" cmd /k "python -m venv .venv && .venv\Scripts\activate && pip install -q -r ..\requirements.txt && uvicorn main:app --host 0.0.0.0 --port 3001"
timeout /t 3 >nul
echo [OK] Main API started

REM Start Chat Service
echo [5/5] Starting Chat Service (Port 4000)...
cd "%CHAT_DIR%"
start "Chat Service" cmd /k "python -m venv .venv && .venv\Scripts\activate && pip install -q -e . && uvicorn main:app --host 0.0.0.0 --port 4000"
timeout /t 3 >nul
echo [OK] Chat Service started

REM Start Notification Service
echo [6/5] Starting Notification Service (Port 8080)...
cd "%NOTIF_DIR%"
start "Notification Service" cmd /k "notification-service.exe"
timeout /t 3 >nul
echo [OK] Notification Service started

cd "%cd%\.."

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║                                                      ║
echo ║            All Services Started!                     ║
echo ║                                                      ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo Main API:              http://localhost:3001
echo Chat Service:          http://localhost:4000
echo Notification Service:  http://localhost:8080
echo.
echo Press any key to stop all services...
pause >nul

REM Stop services
taskkill /FI "WINDOWTITLE eq Main API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Chat Service*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Notification Service*" /F >nul 2>&1

echo.
echo All services stopped.
pause