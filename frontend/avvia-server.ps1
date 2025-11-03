# Script per avviare il server dev frontend
Write-Host "🚀 Avvio server Vite..." -ForegroundColor Green
Write-Host ""

# Imposta variabile ambiente
$env:VITE_API_URL = "http://localhost:8000"

# Cambia directory
Set-Location $PSScriptRoot

# Avvia server
Write-Host "Avvio su http://localhost:5173" -ForegroundColor Cyan
Write-Host "Premi CTRL+C per fermare il server" -ForegroundColor Yellow
Write-Host ""

npm run dev

