@echo off
cd /d "%~dp0"

:: Get the local IP address (first non-loopback IPv4)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1" ^| findstr /v "169.254"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo.
echo   Starting LaunchPad on http://%IP%:3111
echo.

:: Small delay to let server start before opening browser
start "" cmd /c "timeout /t 2 >nul && start http://%IP%:3111"

python server.py