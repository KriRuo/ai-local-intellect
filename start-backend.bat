@echo off
echo Stopping any running backend processes...

:: Find and kill any running uvicorn processes
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8081"') do (
    taskkill /F /PID %%a 2>nul
)

:: Find and kill any running Python processes that might be the tagging script//
for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
    taskkill /F /PID %%a 2>nul
)

echo Starting backend...
:: Activate virtual environment and run the start script
call .venv\Scripts\activate
python -m backend.app.main

pause


::use this for running manually uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8081 