Set-Location "$PSScriptRoot/.."

& $PSScriptRoot/setup.ps1
Clear-Host

& python src/app/main.py $args