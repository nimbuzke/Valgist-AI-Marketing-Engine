@echo off
setlocal EnableDelayedExpansion
rem Valgist launcher - usage:  Valgist Dashboard
set "PROJECT_DIR=C:\Users\user\AI Engines\AI Marketing Engine (Community)"
set "WEBUI_URL=http://localhost:8787"
set "ADMIN_URL=http://localhost:8321"

if /I "%~1"=="dashboard" goto :dashboard
if /I "%~1"=="stop" goto :stop
echo.
echo   Valgist - AI Marketing Engine
echo   ----------------------------
echo   Valgist Dashboard   Launch Valgist WebUI (front end) + Admin Dashboard (Docker)
echo   Valgist Stop        Stop the Valgist containers
echo.
exit /b 0

:stop
cd /d "%PROJECT_DIR%"
docker compose down
exit /b 0

:dashboard
cd /d "%PROJECT_DIR%"
echo [Valgist] Checking Docker...
docker info >nul 2>&1
if not errorlevel 1 goto :dockerup

echo [Valgist] Docker daemon not running - starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
set /a tries=0
:waitdocker
timeout /t 3 /nobreak >nul
docker info >nul 2>&1
if not errorlevel 1 goto :dockerup
set /a tries+=1
if !tries! lss 40 goto :waitdocker
echo [Valgist] Docker did not start in time - falling back to local Node (admin only)...
goto :localnode

:dockerup
echo [Valgist] Building and starting the Valgist containers (admin + WebUI)...
docker compose up -d --build
if errorlevel 1 goto :localnode
echo [Valgist] Valgist is running in Docker.
echo [Valgist] WebUI (front end):  %WEBUI_URL%
echo [Valgist] Admin Dashboard:    %ADMIN_URL%
start "" "%WEBUI_URL%"
start "" "%ADMIN_URL%"
exit /b 0

:localnode
echo [Valgist] Fallback: running the Admin server with local Node.js...
echo [Valgist] Note: the Valgist WebUI (front end) needs Docker - only the
echo [Valgist] Admin Dashboard is available in this fallback mode.
start "Valgist Admin" /min cmd /c "node server.js"
timeout /t 2 /nobreak >nul
start "" "%ADMIN_URL%"
exit /b 0
