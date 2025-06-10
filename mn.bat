@echo off
:: 🚀💚 NEUROTIC CODER'S MODAL-FOR-NOOBS INSTANT LAUNCHER 💚🚀
:: Made with <3 by Neurotic Coder (https://github.com/arthrod) and assisted by Beloved Claude ✨
:: Usage: mn.bat [app_file] [options] OR mn.bat --install-alias

setlocal enabledelayedexpansion

:: Check for install-alias flag
if "%1"=="--install-alias" (
    call :install_alias
    exit /b 0
)

echo.
echo 🚀💚 MODAL-FOR-NOOBS INSTANT LAUNCHER 💚🚀
echo ==========================================
echo Made with ^<3 by Neurotic Coder and assisted by Beloved Claude ✨
echo 💡 Tip: Run 'mn.bat --install-alias' to create permanent 'mn' command!
echo.

:: Function to check if command exists
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python not found! Please install Python 3.11+ first.
        exit /b 1
    )
)

:: Check for uv (preferred) or pip
where uv >nul 2>&1
if %errorlevel% equ 0 (
    set PACKAGE_MGR=uv
    set RUN_CMD=uv run
    set SYNC_CMD=uv sync
) else (
    where pip >nul 2>&1
    if %errorlevel% equ 0 (
        set PACKAGE_MGR=pip
        set RUN_CMD=%PYTHON_CMD%
        set SYNC_CMD=pip install -e .
    ) else (
        echo ❌ No package manager found! Please install uv or pip.
        exit /b 1
    )
)

:: Check if in correct directory
if not exist "pyproject.toml" (
    echo ❌ Not in modal-for-noobs directory! Please cd to the project root.
    exit /b 1
)

:: Install dependencies if needed
if not exist ".venv" if "%PACKAGE_MGR%"=="uv" (
    echo 🏗️ Installing dependencies...
    %SYNC_CMD%
)

:: Default behavior: Start wizard if no arguments
if "%1"=="" (
    echo 🧙‍♂️ Starting deployment wizard (default mode)...
    echo 💡 Pro tip: mn.bat app.py for quick deploy!
    echo.

    :: Check for examples in the current directory
    if exist "src\modal_for_noobs\examples\ultimate_voice_green_app.py" (
        set APP_FILE=src\modal_for_noobs\examples\ultimate_voice_green_app.py
        echo ✨ Using example voice app: !APP_FILE!
    ) else (
        set /p APP_INPUT="Enter path to your Gradio app (or press Enter for example): "
        if "!APP_INPUT!"=="" (
            set APP_FILE=src\modal_for_noobs\examples\test_gradio_app.py
        ) else (
            set APP_FILE=!APP_INPUT!
        )
    )

    echo 🧙‍♂️ Launching wizard for: !APP_FILE!
    %RUN_CMD% python -m modal_for_noobs.cli deploy "!APP_FILE!" --wizard

) else (
    :: Quick deploy mode with provided app file
    set APP_FILE=%1

    echo ⚡ QUICK DEPLOY MODE ⚡
    echo 🚀 Deploying: %APP_FILE%

    :: Pass all arguments except the first one
    set ARGS=
    :loop
    shift
    if "%1"=="" goto :continue
    set ARGS=%ARGS% %1
    goto :loop
    :continue

    %RUN_CMD% python -m modal_for_noobs.cli mn "%APP_FILE%" %ARGS%
)

echo.
echo 💚 Thanks for using Modal-for-noobs! 💚
echo Made with ^<3 by Neurotic Coder and assisted by Beloved Claude ✨
exit /b 0

:install_alias
echo.
echo 🔧 INSTALLING PERMANENT 'mn' ALIAS 🔧
echo This will allow you to just type 'mn' from anywhere!
echo.

:: Get the current script path
set SCRIPT_PATH=%~dp0mn.bat

:: Create doskey macro in a batch file
set ALIAS_BAT=%USERPROFILE%\mn_alias.bat
echo @echo off > "%ALIAS_BAT%"
echo doskey mn="%SCRIPT_PATH%" $* >> "%ALIAS_BAT%"

:: Add to registry for persistent doskey
echo 📝 Creating persistent alias...
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%ALIAS_BAT%" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Alias installed successfully!
    echo 🔄 Restart your Command Prompt or PowerShell
    echo 🚀 Then you can use 'mn' from anywhere!
    echo.
    echo Examples:
    echo   mn app.py           # Quick deploy
    echo   mn app.py --wizard  # Wizard mode
    echo   mn --milk-logs      # View logs
) else (
    echo ⚠️ Could not install persistent alias automatically.
    echo 💡 Manual setup: Add this to your startup:
    echo   doskey mn="%SCRIPT_PATH%" $*
)
echo.
exit /b 0
