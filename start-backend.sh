@echo off
echo Stopping any running backend processes...

:: Find and kill any running uvicorn processes
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8081"') do (
    taskkill /F /PID %%a 2>nul
)

:: Find and kill any running Python processes that might be the tagging script
for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
    taskkill /F /PID %%a 2>nul
)

echo Starting backend...
:: Activate virtual environment and run the start script
call .venv\Scripts\activate

:: Start the backend server in the background
start /B uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8081

:: Wait for the backend to be ready
echo Waiting for backend to start...
:wait_loop
timeout /t 1 /nobreak > nul
curl -s http://localhost:8081/health > nul 2>&1
if errorlevel 1 goto wait_loop
echo Backend is ready!

:menu
cls
echo Backend is running!
echo.
echo Please select an option:
echo 0. Run all
echo 1. Run RSS scraping
echo 2. Run Tagging service
echo 3. Exit
echo.
set /p choice="Enter your choice (0-3): "

if "%choice%"=="0" (
    echo Running RSS scraping...
    curl -X POST http://localhost:8081/api/scrape/rss/import-all
    echo Starting post tagging process...
    start /B python backend/app/scripts/tag_posts.py
    goto menu
)
if "%choice%"=="1" (
    echo Running RSS scraping...
    curl -X POST http://localhost:8081/api/scrape/rss/import-all
    goto menu
)
if "%choice%"=="2" (
    echo Starting post tagging process...
    start /B python backend/app/scripts/tag_posts.py
    goto menu
)
if "%choice%"=="3" (
    echo Exiting...
    exit
)
goto menu