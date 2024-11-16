@echo off

@REM Check if node.js, python3, pip, and yarn are installed
@echo Checking if Node.js is installed...
node -v
@echo Checking if Python3 is installed...
python3 --version
@echo Checking if pip is installed...
pip --version
@echo Checking if Yarn is installed...
yarn -v

@REM Run linklogger.py concurrently
@echo Starting linklogger.py...
start python3 linklogger.py

@REM Run yarn dev concurrently
@echo Starting yarn dev...
cd app
start yarn dev

@REM Prevent the script from closing immediately
pause