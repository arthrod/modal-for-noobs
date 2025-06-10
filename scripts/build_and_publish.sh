#!/bin/bash
# 🚀💚 Modal-for-noobs Build and Publish Script

set -e  # Exit on any error

echo "🚀💚 Modal-for-noobs Build and Publish Script"
echo "=============================================="

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: pyproject.toml not found. Please run from project root."
    exit 1
fi

# Parse command line arguments
PUBLISH_TO=""
DRY_RUN=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            PUBLISH_TO="test"
            shift
            ;;
        --prod|--pypi)
            PUBLISH_TO="pypi"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --test      Publish to Test PyPI"
            echo "  --prod      Publish to PyPI (production)"
            echo "  --pypi      Alias for --prod"
            echo "  --dry-run   Build and check only, don't publish"
            echo "  --force     Skip confirmation prompts"
            echo "  -h, --help  Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 --dry-run           # Build and check only"
            echo "  $0 --test              # Publish to Test PyPI"
            echo "  $0 --prod --force      # Publish to PyPI without confirmation"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Get version from pyproject.toml
VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "unknown")
echo "📦 Package version: $VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Install/update build tools
echo "🔧 Installing build tools..."
uv tool install --upgrade build twine

# Build the package
echo "🏗️ Building package..."
uv build

# Verify the build
echo "🔍 Verifying build..."
uv tool run twine check dist/*

if [[ $? -ne 0 ]]; then
    echo "❌ Package verification failed!"
    exit 1
fi

echo "✅ Package built and verified successfully!"
echo ""
echo "📦 Built artifacts:"
ls -la dist/

# If dry run, stop here
if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo "🏃 Dry run completed. Package is ready for publishing."
    echo ""
    echo "To publish manually:"
    echo "  Test PyPI: uv tool run twine upload --repository testpypi dist/*"
    echo "  PyPI:      uv tool run twine upload dist/*"
    exit 0
fi

# If no publish target specified, show options
if [[ -z "$PUBLISH_TO" ]]; then
    echo ""
    echo "🤔 Where would you like to publish?"
    echo "1) Test PyPI (recommended for testing)"
    echo "2) PyPI (production)"
    echo "3) Just build (no publishing)"
    echo ""
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1) PUBLISH_TO="test" ;;
        2) PUBLISH_TO="pypi" ;;
        3) exit 0 ;;
        *) echo "❌ Invalid choice"; exit 1 ;;
    esac
fi

# Confirm publishing
if [[ "$FORCE" != true ]]; then
    echo ""
    if [[ "$PUBLISH_TO" == "test" ]]; then
        echo "🧪 About to publish to Test PyPI"
        echo "URL: https://test.pypi.org/project/modal-for-noobs/$VERSION/"
    else
        echo "🚀 About to publish to PyPI (PRODUCTION)"
        echo "URL: https://pypi.org/project/modal-for-noobs/$VERSION/"
        echo ""
        echo "⚠️  This will make the package publicly available!"
    fi
    
    read -p "Continue? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "❌ Publishing cancelled"
        exit 1
    fi
fi

# Publish
echo ""
if [[ "$PUBLISH_TO" == "test" ]]; then
    echo "🧪 Publishing to Test PyPI..."
    uv tool run twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Published to Test PyPI!"
    echo "🔗 View at: https://test.pypi.org/project/modal-for-noobs/$VERSION/"
    echo ""
    echo "🧪 To test installation:"
    echo "pip install --index-url https://test.pypi.org/simple/ modal-for-noobs"
else
    echo "🚀 Publishing to PyPI..."
    uv tool run twine upload dist/*
    echo ""
    echo "🎉 Published to PyPI!"
    echo "🔗 View at: https://pypi.org/project/modal-for-noobs/$VERSION/"
    echo ""
    echo "📦 To install:"
    echo "pip install modal-for-noobs"
fi

echo ""
echo "🎉 Build and publish completed successfully! 💚🚀"