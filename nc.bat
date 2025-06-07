@echo off
REM 🚀💚 NEUROTIC CODER'S MODAL-FOR-NOOBS LAUNCHER (WINDOWS) 💚🚀
REM Made with <3 by Neurotic Coder (https://github.com/arthrod) and assisted by Beloved Claude ✨

setlocal enabledelayedexpansion

echo.
echo 🚀💚 NEUROTIC CODER'S MODAL-FOR-NOOBS LAUNCHER 💚🚀
echo ======================================================
echo.
echo 💚 Made with ^<3 by Neurotic Coder and assisted by Beloved Claude ✨
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo ❌ Python not found! Please install Python 3.11+ first.
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo 🐍 Python command: %PYTHON_CMD%

REM Check for uv or pip
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    set PACKAGE_MGR=uv
    set RUN_CMD=uv run
    set SYNC_CMD=uv sync
) else (
    pip --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PACKAGE_MGR=pip
        set RUN_CMD=%PYTHON_CMD%
        set SYNC_CMD=pip install -e .
    ) else (
        echo ❌ No package manager found! Please install uv or pip.
        pause
        exit /b 1
    )
)

echo 📦 Package manager: %PACKAGE_MGR%
echo.

REM Check if in correct directory
if not exist "pyproject.toml" (
    echo ❌ Not in modal-for-noobs directory! Please cd to the project root.
    pause
    exit /b 1
)

:menu
echo 🎯 What would you like to do?
echo.
echo 1. 🚀 Quick deploy a Gradio app
echo 2. 🧙‍♂️ Use the deployment wizard
echo 3. 💪 Time to get serious (HF Spaces migration)
echo 4. 🔐 Setup Modal authentication
echo 5. 📋 Show configuration
echo 6. 🎤 Launch voice app example
echo 7. 🏗️  Install/Update dependencies
echo 8. 🔍 Show help
echo 9. 🚪 Exit
echo.

set /p choice="Enter your choice (1-9): "
echo.

if "%choice%"=="1" goto quick_deploy
if "%choice%"=="2" goto wizard_deploy
if "%choice%"=="3" goto serious_mode
if "%choice%"=="4" goto setup_auth
if "%choice%"=="5" goto show_config
if "%choice%"=="6" goto launch_voice
if "%choice%"=="7" goto install_deps
if "%choice%"=="8" goto show_help
if "%choice%"=="9" goto exit_script

echo ❌ Invalid choice! Please try again.
echo.
pause
goto menu

:quick_deploy
echo 🚀 Quick Deploy Mode
echo.
echo 📱 Available example apps:
echo 1. 🎤 Ultimate Voice Green App (microphone + speaker)
echo 2. 🎭 Ultimate Green Creative Studio
echo 3. 🎯 Simple Test Gradio App
echo.

set /p app_choice="Choose an app (1-3) or enter path to your own app: "

if "%app_choice%"=="1" (
    set APP_PATH=src/modal_for_noobs/examples/ultimate_voice_green_app.py
) else if "%app_choice%"=="2" (
    set APP_PATH=src/modal_for_noobs/examples/ultimate_green_app.py
) else if "%app_choice%"=="3" (
    set APP_PATH=src/modal_for_noobs/examples/test_gradio_app.py
) else (
    set APP_PATH=%app_choice%
)

echo 🚀 Deploying: %APP_PATH%
%RUN_CMD% python -m modal_for_noobs.cli mn "%APP_PATH%" --optimized
goto menu_continue

:wizard_deploy
echo 🧙‍♂️ Deployment Wizard Mode
echo.
set /p APP_PATH="Enter path to your Gradio app: "
echo 🧙‍♂️ Starting wizard for: %APP_PATH%
%RUN_CMD% python -m modal_for_noobs.cli deploy "%APP_PATH%" --wizard
goto menu_continue

:serious_mode
echo 💪 Time to get serious!
set /p HF_URL="Enter HuggingFace Spaces URL: "
%RUN_CMD% python -m modal_for_noobs.cli time-to-get-serious "%HF_URL%"
goto menu_continue

:setup_auth
echo 🔐 Setting up Modal authentication...
%RUN_CMD% python -m modal_for_noobs.cli auth
goto menu_continue

:show_config
echo 📋 Configuration:
%RUN_CMD% python -m modal_for_noobs.cli config
goto menu_continue

:launch_voice
echo 🎤 Launching Voice App Locally
%RUN_CMD% python src/modal_for_noobs/examples/ultimate_voice_green_app.py
goto menu_continue

:install_deps
echo 🏗️  Installing/Updating dependencies...
if "%PACKAGE_MGR%"=="uv" (
    echo Using uv for lightning-fast installation! ⚡
) else (
    echo Using pip for installation...
)
%SYNC_CMD%
echo ✅ Dependencies ready!
goto menu_continue

:show_help
echo 🔍 Help:
%RUN_CMD% python -m modal_for_noobs.cli --help
goto menu_continue

:menu_continue
echo.
pause
echo.
goto menu

:exit_script
echo 🚪 Thanks for using Neurotic Coder's Modal CLI! 💚
echo 💚 Made with ^<3 by Neurotic Coder and assisted by Beloved Claude ✨
pause
exit /b 0