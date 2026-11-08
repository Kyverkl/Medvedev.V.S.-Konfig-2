@echo off
cd /d "%~dp0"
set PYTHONPATH=src
py -3.15 -m depvis %*
