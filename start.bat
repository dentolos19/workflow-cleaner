@echo off
cd /d %~dp0
call setup.bat
cls
python src/main.py %*