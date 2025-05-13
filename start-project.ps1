param(
    [string]$BackendScript = ".\start-backend.sh",
    [string]$FrontendPath = ".",
    [string]$FrontendCommand = "npm run dev"
)

Set-Location -Path $PSScriptRoot

Write-Host "Starting backend using $BackendScript ..."
Start-Process powershell -ArgumentList "-Command", $BackendScript

Write-Host "Starting frontend in $FrontendPath ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $FrontendPath; $FrontendCommand"

Write-Host "Both backend and frontend are starting!"

# Open the RSS feed page in the default browser
Start-Process "http://localhost:5173/rss-feed"
