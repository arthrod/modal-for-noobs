#!/bin/bash

# 🚀💚 MODAL-FOR-NOOBS UNIFIED LAUNCHER 💚🚀
# Made with <3 by Neurotic Coder (https://github.com/arthrod) and assisted by Beloved Claude ✨
# Usage: ./mn.sh [command] [options] OR ./mn.sh --install-alias

# Colors for epic output! 💚
MODAL_GREEN='\033[38;2;0;210;106m'
MODAL_LIGHT_GREEN='\033[38;2;74;232;138m'
RED='\033[31m'
RESET='\033[0m'
BOLD='\033[1m'

# Function to install permanent alias
install_alias() {
    echo -e "${MODAL_GREEN}${BOLD}🔧 INSTALLING PERMANENT 'mn' ALIAS 🔧${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}This will allow you to just type 'mn' from anywhere!${RESET}"
    echo ""

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_PATH="$SCRIPT_DIR/mn.sh"

    # Detect shell and config file
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
        SHELL_NAME="zsh"
    elif [[ "$SHELL" == *"bash"* ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        else
            SHELL_CONFIG="$HOME/.bashrc"
        fi
        SHELL_NAME="bash"
    else
        SHELL_CONFIG="$HOME/.bashrc"
        SHELL_NAME="unknown"
    fi

    # Create alias command
    ALIAS_COMMAND="alias mn='$SCRIPT_PATH'"

    echo -e "${MODAL_GREEN}📝 Adding alias to $SHELL_CONFIG...${RESET}"

    # Check if alias already exists
    if grep -q "alias mn=" "$SHELL_CONFIG" 2>/dev/null; then
        echo -e "${MODAL_LIGHT_GREEN}⚠️ 'mn' alias already exists! Updating...${RESET}"
        # Remove existing alias
        sed -i.bak '/alias mn=/d' "$SHELL_CONFIG"
    fi

    # Add new alias
    echo "# Modal-for-noobs permanent alias - Added by mn.sh" >> "$SHELL_CONFIG"
    echo "$ALIAS_COMMAND" >> "$SHELL_CONFIG"

    echo -e "${MODAL_GREEN}✅ Alias installed successfully!${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}🔄 Restart your terminal or run: source $SHELL_CONFIG${RESET}"
    echo -e "${MODAL_GREEN}🚀 Then you can use 'mn' from anywhere!${RESET}"
    echo ""
    echo -e "${MODAL_LIGHT_GREEN}Examples:${RESET}"
    echo -e "${MODAL_GREEN}  mn app.py           ${RESET}# Quick deploy"
    echo -e "${MODAL_GREEN}  mn app.py --wizard  ${RESET}# Wizard mode"
    echo -e "${MODAL_GREEN}  mn --milk-logs      ${RESET}# View logs"
    echo ""
    exit 0
}

# Check for install-alias flag
if [[ "$1" == "--install-alias" ]]; then
    install_alias
fi

echo -e "${MODAL_GREEN}${BOLD}"
echo "🚀💚 MODAL-FOR-NOOBS INSTANT LAUNCHER 💚🚀"
echo "=========================================="
echo -e "${RESET}"
echo -e "${MODAL_LIGHT_GREEN}Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨${RESET}"
echo -e "${MODAL_GREEN}💡 Tip: Run './mn.sh --install-alias' to create permanent 'mn' command!${RESET}"
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

# Unified command handling
if [ $# -eq 0 ]; then
    # No arguments - show available examples
    echo -e "${MODAL_GREEN}🎯 MODAL-FOR-NOOBS UNIFIED INTERFACE 🎯${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}💡 Use --run-examples to see available examples!${RESET}"
    echo ""
    echo -e "${MODAL_GREEN}Examples:${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}  ./mn.sh --run-examples              ${RESET}# List all examples"
    echo -e "${MODAL_LIGHT_GREEN}  ./mn.sh --run-examples simple_hello ${RESET}# Run simple hello example"
    echo -e "${MODAL_LIGHT_GREEN}  ./mn.sh deploy app.py --wizard      ${RESET}# Deploy with wizard"
    echo -e "${MODAL_LIGHT_GREEN}  ./mn.sh milk-logs                   ${RESET}# View deployment logs"
    echo ""

    # Show examples
    $RUN_CMD python -m modal_for_noobs.cli run-examples

elif [[ "$1" == "--run-examples" ]]; then
    # Handle --run-examples flag
    shift # Remove --run-examples
    if [ $# -eq 0 ]; then
        # List examples
        $RUN_CMD python -m modal_for_noobs.cli run-examples
    else
        # Run specific example
        EXAMPLE_NAME="$1"
        shift
        echo -e "${MODAL_GREEN}🎯 Running example: ${BOLD}$EXAMPLE_NAME${RESET}"
        $RUN_CMD python -m modal_for_noobs.cli run-examples "$EXAMPLE_NAME" "$@"
    fi

elif [[ "$1" == "--"* ]]; then
    # Handle other flags (like --milk-logs, --install-alias)
    FLAG="$1"
    shift

    case "$FLAG" in
        "--milk-logs")
            $RUN_CMD python -m modal_for_noobs.cli milk-logs "$@"
            ;;
        "--sanity-check")
            $RUN_CMD python -m modal_for_noobs.cli sanity-check "$@"
            ;;
        "--kill-deployment")
            $RUN_CMD python -m modal_for_noobs.cli kill-a-deployment "$@"
            ;;
        "--config")
            $RUN_CMD python -m modal_for_noobs.cli config "$@"
            ;;
        "--auth")
            $RUN_CMD python -m modal_for_noobs.cli auth "$@"
            ;;
        *)
            echo -e "${RED}❌ Unknown flag: $FLAG${RESET}"
            echo -e "${MODAL_GREEN}💡 Available flags:${RESET}"
            echo -e "${MODAL_LIGHT_GREEN}  --run-examples, --milk-logs, --sanity-check, --kill-deployment, --config, --auth${RESET}"
            exit 1
            ;;
    esac

elif [[ "$1" == "deploy" ]] || [[ "$1" == "mn" ]] || [[ "$1" == "run-examples" ]] || [[ "$1" == "milk-logs" ]] || [[ "$1" == "sanity-check" ]] || [[ "$1" == "kill-a-deployment" ]] || [[ "$1" == "config" ]] || [[ "$1" == "auth" ]] || [[ "$1" == "time-to-get-serious" ]]; then
    # Direct CLI command
    echo -e "${MODAL_GREEN}⚡ EXECUTING COMMAND: ${BOLD}$1${RESET}"
    $RUN_CMD python -m modal_for_noobs.cli "$@"

else
    # Legacy mode: treat first argument as app file
    APP_FILE="$1"
    shift # Remove first argument

    echo -e "${MODAL_GREEN}⚡ LEGACY MODE - QUICK DEPLOY ⚡${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}🚀 Deploying: ${BOLD}$APP_FILE${RESET}"
    echo -e "${MODAL_LIGHT_GREEN}💡 Consider using: ./mn.sh deploy $APP_FILE${RESET}"

    $RUN_CMD python -m modal_for_noobs.cli deploy "$APP_FILE" "$@"
fi

echo ""
echo -e "${MODAL_GREEN}💚 Thanks for using Modal-for-noobs! 💚${RESET}"
echo -e "${MODAL_LIGHT_GREEN}Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨${RESET}"
