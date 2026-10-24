@echo off
title Wellora - Health Journey Server
echo ========================================================
echo   Starting Wellora Health Journey Server...
echo ========================================================
echo.
echo Opening http://localhost:8080 in your default browser...
start "" "http://localhost:8080"
echo.
echo Server running on http://localhost:8080
echo Press Ctrl+C to stop the server anytime.
echo.
python server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python command failed, trying 'py server.py'...
    py server.py
)
pause
