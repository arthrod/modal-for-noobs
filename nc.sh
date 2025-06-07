#!/bin/bash

# 🚀💚 NEUROTIC CODER'S MODAL-FOR-NOOBS LAUNCHER 💚🚀
# Made with <3 by Neurotic Coder (https://github.com/arthrod) and assisted by Beloved Claude ✨

# Colors for epic output! 💚
MODAL_GREEN='\033[38;2;0;210;106m'
MODAL_LIGHT_GREEN='\033[38;2;74;232;138m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${MODAL_GREEN}${BOLD}"
echo "🚀💚 NEUROTIC CODER'S MODAL-FOR-NOOBS LAUNCHER 💚🚀"
echo "======================================================"
echo -e "${RESET}"
echo -e "${MODAL_LIGHT_GREEN}Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨${RESET}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display epic banner
show_banner() {
    echo -e "${MODAL_GREEN}${BOLD}"
    echo "   ███╗   ██╗ ██████╗"
    echo "   ████╗  ██║██╔════╝"
    echo "   ██╔██╗ ██║██║     "
    echo "   ██║╚██╗██║██║     "
    echo "   ██║ ╚████║╚██████╗"
    echo "   ╚═╝  ╚═══╝ ╚═════╝"
    echo -e "${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}Neurotic Coder's Modal CLI${RESET}"
    echo ""
}

# Check OS and set appropriate commands
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    MSYS*)      MACHINE=Msys;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${MODAL_GREEN}🖥️  Detected OS: ${BOLD}${MACHINE}${RESET}"

# Check for Python and package manager
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found! Please install Python 3.11+ first.${RESET}"
    exit 1
fi

echo -e "${MODAL_GREEN}🐍 Python command: ${BOLD}${PYTHON_CMD}${RESET}"

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

echo -e "${MODAL_GREEN}📦 Package manager: ${BOLD}${PACKAGE_MGR}${RESET}"
echo ""

# Show menu
show_menu() {
    echo -e "${MODAL_GREEN}${BOLD}🎯 What would you like to do?${RESET}"
    echo ""
    echo -e "${MODAL_LIGHT_GREEN}1.${RESET} 🚀 Quick deploy a Gradio app"
    echo -e "${MODAL_LIGHT_GREEN}2.${RESET} 🧙‍♂️ Use the deployment wizard"
    echo -e "${MODAL_LIGHT_GREEN}3.${RESET} 💪 Time to get serious (HF Spaces migration)"
    echo -e "${MODAL_LIGHT_GREEN}4.${RESET} 🔐 Setup Modal authentication"
    echo -e "${MODAL_LIGHT_GREEN}5.${RESET} 📋 Show configuration"
    echo -e "${MODAL_LIGHT_GREEN}6.${RESET} 🎤 Launch voice app example"
    echo -e "${MODAL_LIGHT_GREEN}7.${RESET} 🏗️  Install/Update dependencies"
    echo -e "${MODAL_LIGHT_GREEN}8.${RESET} 🔍 Show help"
    echo -e "${MODAL_LIGHT_GREEN}9.${RESET} 🚪 Exit"
    echo ""
}

# Main installation function
install_deps() {
    echo -e "${MODAL_GREEN}🏗️  Installing/Updating dependencies...${RESET}"
    
    if [ "$PACKAGE_MGR" = "uv" ]; then
        echo -e "${MODAL_LIGHT_GREEN}Using uv for lightning-fast installation! ⚡${RESET}"
        $SYNC_CMD
    else
        echo -e "${MODAL_LIGHT_GREEN}Using pip for installation...${RESET}"
        $SYNC_CMD
    fi
    
    echo -e "${MODAL_GREEN}✅ Dependencies ready!${RESET}"
}

# Quick deploy function
quick_deploy() {
    echo -e "${MODAL_GREEN}🚀 Quick Deploy Mode${RESET}"
    echo ""
    
    # List available example apps
    echo -e "${MODAL_LIGHT_GREEN}📱 Available example apps:${RESET}"
    echo "1. 🎤 Ultimate Voice Green App (microphone + speaker)"
    echo "2. 🎭 Ultimate Green Creative Studio"
    echo "3. 🎯 Simple Test Gradio App"
    echo ""
    
    read -p "Choose an app (1-3) or enter path to your own app: " choice
    
    case $choice in
        1)
            APP_PATH="src/modal_for_noobs/examples/ultimate_voice_green_app.py"
            ;;
        2)
            APP_PATH="src/modal_for_noobs/examples/ultimate_green_app.py"
            ;;
        3)
            APP_PATH="src/modal_for_noobs/examples/test_gradio_app.py"
            ;;
        *)
            APP_PATH="$choice"
            ;;
    esac
    
    echo -e "${MODAL_GREEN}🚀 Deploying: ${BOLD}$APP_PATH${RESET}"
    $RUN_CMD python -m modal_for_noobs.cli mn "$APP_PATH" --optimized
}

# Wizard deploy function
wizard_deploy() {
    echo -e "${MODAL_GREEN}🧙‍♂️ Deployment Wizard Mode${RESET}"
    echo ""
    
    read -p "Enter path to your Gradio app: " APP_PATH
    
    echo -e "${MODAL_GREEN}🧙‍♂️ Starting wizard for: ${BOLD}$APP_PATH${RESET}"
    $RUN_CMD python -m modal_for_noobs.cli deploy "$APP_PATH" --wizard
}

# Launch voice app locally
launch_voice_app() {
    echo -e "${MODAL_GREEN}🎤 Launching Voice App Locally${RESET}"
    echo ""
    
    $RUN_CMD python src/modal_for_noobs/examples/ultimate_voice_green_app.py
}

# Main script execution
show_banner

# Check if dependencies are installed
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Not in modal-for-noobs directory! Please cd to the project root.${RESET}"
    exit 1
fi

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice (1-9): " choice
    echo ""
    
    case $choice in
        1)
            quick_deploy
            ;;
        2)
            wizard_deploy
            ;;
        3)
            echo -e "${MODAL_GREEN}💪 Time to get serious!${RESET}"
            read -p "Enter HuggingFace Spaces URL: " HF_URL
            $RUN_CMD python -m modal_for_noobs.cli time-to-get-serious "$HF_URL"
            ;;
        4)
            echo -e "${MODAL_GREEN}🔐 Setting up Modal authentication...${RESET}"
            $RUN_CMD python -m modal_for_noobs.cli auth
            ;;
        5)
            echo -e "${MODAL_GREEN}📋 Configuration:${RESET}"
            $RUN_CMD python -m modal_for_noobs.cli config
            ;;
        6)
            launch_voice_app
            ;;
        7)
            install_deps
            ;;
        8)
            echo -e "${MODAL_GREEN}🔍 Help:${RESET}"
            $RUN_CMD python -m modal_for_noobs.cli --help
            ;;
        9)
            echo -e "${MODAL_GREEN}🚪 Thanks for using Neurotic Coder's Modal CLI! 💚${RESET}"
            echo -e "${MODAL_LIGHT_GREEN}Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨${RESET}"
            break
            ;;
        *)
            echo -e "${RED}❌ Invalid choice! Please try again.${RESET}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    echo ""
done