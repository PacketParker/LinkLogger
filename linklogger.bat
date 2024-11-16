@echo off
setlocal enabledelayedexpansion

@REM Check for Python (at least 3.10)
@echo Checking for Python installation...

set PYTHON_CMD=
for %%P in (python python3) do (
    %%P --version 2>nul >nul
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%P
        goto CheckPythonVersion
    )
)

@echo Error: Neither Python nor Python3 is installed. Please install Python 3.10 or higher.
exit /b 1

:CheckPythonVersion
for /f "tokens=2 delims= " %%V in ('%PYTHON_CMD% --version') do set PYTHON_VERSION=%%V
@echo Detected Python version: %PYTHON_VERSION%

for /f "tokens=1,2 delims=." %%M in ("%PYTHON_VERSION%") do (
    set MAJOR=%%M
    set MINOR=%%N
)

if %MAJOR% lss 3 (
    @echo Error: Python version is too old. Please install Python 3.10 or higher.
    exit /b 1
)
if %MAJOR% equ 3 if %MINOR% lss 10 (
    @echo Error: Python version is too old. Please install Python 3.10 or higher.
    exit /b 1
)

@echo Python version is compatible.

@REM Check for Node.js
@echo Checking if Node.js is installed...
node -v >nul 2>nul
if errorlevel 1 (
    @echo Error: Node.js is not installed. Please install it and try again.
    exit /b 1
)

@REM Check for pip
@echo Checking if pip is installed...
pip --version >nul 2>nul
if errorlevel 1 (
    @echo Error: pip is not installed. Please install it and try again.
    exit /b 1
)

@REM @REM Check for Yarn
@REM @echo Checking if Yarn is installed...
@REM yarn -v >nul 2>nul
@REM if errorlevel 1 (
@REM     @echo Error: Yarn is not installed. Please install it and try again.
@REM     exit /b 1
@REM )

@REM All dependencies are verified
@echo All dependencies are installed and compatible.

@REM Install UI dependencies and start the UI
@echo Install UI dependencies and starting UI in new window...
start cmd /k "cd app && yarn install && start cmd /c yarn add vite && yarn dev"

@REM Run linklogger.py concurrently in a new window
@echo Installing API dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
@echo Starting API...
%PYTHON_CMD% linklogger.py

@REM Prevent the script from closing immediately after both commands complete
pause
