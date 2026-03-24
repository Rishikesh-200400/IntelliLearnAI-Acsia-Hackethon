@echo off
echo ================================================
echo   IntelliLearn AI - Starting Application
echo ================================================
echo.

echo Starting Flask API Backend...
start "IntelliLearn API" cmd /k "python api.py"

timeout /t 3

echo Starting React Frontend...
cd frontend
start "IntelliLearn Frontend" cmd /k "npm run dev"

echo.
echo ================================================
echo   Both servers are starting!
echo ================================================
echo   API:      http://localhost:5000
echo   Frontend: http://localhost:3000
echo ================================================
echo.
echo Press any key to exit this window...
pause > nul
