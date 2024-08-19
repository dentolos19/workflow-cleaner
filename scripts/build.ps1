Set-Location "$PSScriptRoot/.."

& $PSScriptRoot/setup.ps1
Clear-Host

Write-Host "Building the project..."
Write-Host

& pyinstaller src/app/main.py --onefile --icon src/icon.ico
Remove-Item "main.spec"