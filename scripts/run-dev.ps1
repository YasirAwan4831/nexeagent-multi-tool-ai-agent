# Start NEXEAGENT backend and frontend (Windows PowerShell)
# Usage: .\scripts\run-dev.ps1

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

if (-not (Test-Path (Join-Path $Backend "venv"))) {
    Write-Host "Creating Python venv..."
    Set-Location $Backend
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
}

if (-not (Test-Path (Join-Path $Backend ".env"))) {
    Copy-Item (Join-Path $Backend ".env.example") (Join-Path $Backend ".env")
    Write-Host "Created backend/.env — add GEMINI_API_KEY before using AI chat."
}

Write-Host "Starting backend on http://127.0.0.1:5000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Backend'; .\venv\Scripts\python app.py"

Start-Sleep -Seconds 2

Write-Host "Starting frontend on http://localhost:5173"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Frontend'; npm run dev"

Write-Host "Done. Open http://localhost:5173 in your browser."
