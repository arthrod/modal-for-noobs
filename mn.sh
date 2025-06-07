#!/bin/bash

# 🚀💚 NEUROTIC CODER'S MODAL-FOR-NOOBS INSTANT LAUNCHER 💚🚀
# Made with <3 by Neurotic Coder (https://github.com/arthrod) and assisted by Beloved Claude ✨
# Usage: ./mn.sh [app_file] [options]

# Colors for epic output! 💚
MODAL_GREEN='\033[38;2;0;210;106m'
MODAL_LIGHT_GREEN='\033[38;2;74;232;138m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${MODAL_GREEN}${BOLD}"
echo "🚀💚 MODAL-FOR-NOOBS INSTANT LAUNCHER 💚🚀"
echo "=========================================="
echo -e "${RESET}"
echo -e "${MODAL_LIGHT_GREEN}Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨${RESET}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python and package manager
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found! Please install Python 3.11+ first.${RESET}"
    exit 1
fi

# Check for uv (preferred) or pip
if command_exists uv; then
    PACKAGE_MGR="uv"
    RUN_CMD="uv run"
    SYNC_CMD="uv sync"
elif command_exists pip; then
    PACKAGE_MGR="pip"
    RUN_CMD="${PYTHON_CMD}"
    SYNC_CMD="pip install -e ."
else
    echo -e "${RED}❌ No package manager found! Please install uv or pip.${RESET}"
    exit 1
fi

# Check if in correct directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Not in modal-for-noobs directory! Please cd to the project root.${RESET}"
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ] && [ "$PACKAGE_MGR" = "uv" ]; then
    echo -e "${MODAL_GREEN}🏗️ Installing dependencies...${RESET}"
    $SYNC_CMD
fi

# Default behavior: Start wizard if no arguments
if [ $# -eq 0 ]; then
    echo -e "${MODAL_GREEN}🧙‍♂️ Starting deployment wizard (default mode)...${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}💡 Pro tip: ./mn.sh app.py for quick deploy!${RESET}"
    echo ""
    
    # Check for examples in the current directory
    if [ -f "src/modal_for_noobs/examples/ultimate_voice_green_app.py" ]; then
        APP_FILE="src/modal_for_noobs/examples/ultimate_voice_green_app.py"
        echo -e "${MODAL_GREEN}✨ Using example voice app: ${APP_FILE}${RESET}"
    else
        read -p "Enter path to your Gradio app (or press Enter for example): " APP_INPUT
        if [ -z "$APP_INPUT" ]; then
            APP_FILE="src/modal_for_noobs/examples/test_gradio_app.py"
        else
            APP_FILE="$APP_INPUT"
        fi
    fi
    
    echo -e "${MODAL_GREEN}🧙‍♂️ Launching wizard for: ${BOLD}$APP_FILE${RESET}"
    $RUN_CMD python -m modal_for_noobs.cli deploy "$APP_FILE" --wizard
    
else
    # Quick deploy mode with provided app file
    APP_FILE="$1"
    shift # Remove first argument
    
    echo -e "${MODAL_GREEN}⚡ QUICK DEPLOY MODE ⚡${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}🚀 Deploying: ${BOLD}$APP_FILE${RESET}"
    
    $RUN_CMD python -m modal_for_noobs.cli mn "$APP_FILE" "$@"
fi

echo ""
echo -e "${MODAL_GREEN}💚 Thanks for using Modal-for-noobs! 💚${RESET}"
echo -e "${MODAL_LIGHT_GREEN}Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨${RESET}"