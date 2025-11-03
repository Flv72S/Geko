# Script PowerShell per avviare il server dev con output visibile
Write-Host "🚀 Avvio server Vite per Geko Frontend..." -ForegroundColor Green
Write-Host ""

Set-Location $PSScriptRoot
npm run dev

