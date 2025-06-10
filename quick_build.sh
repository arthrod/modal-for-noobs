#!/bin/bash

# Quick build and publish script for modal-for-noobs
# Fixes the f-string syntax error and publishes to PyPI

set -e

echo "🚀 Quick Build & Publish for modal-for-noobs v0.2.3"
echo "=================================================="

# Verify we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this from the project root directory"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info/

# Test syntax
echo "🔍 Testing Python syntax..."
python -m py_compile src/modal_for_noobs/cli.py || {
    echo "❌ Syntax error in cli.py!"
    exit 1
}

# Test import
echo "🧪 Testing imports..."
PYTHONPATH="src:$PYTHONPATH" python -c "from modal_for_noobs.cli import main; print('✅ CLI import OK')" || {
    echo "❌ Import error!"
    exit 1
}

# Build
echo "🔨 Building package..."
uv build || {
    echo "❌ Build failed! Trying alternative method..."
    python -m build --break-system-packages || {
        echo "Installing build tools..."
        uv add --dev build twine
        uv build
    }
}

# Check package
echo "🔍 Checking package..."
uv tool run twine check dist/* || {
    echo "❌ Package check failed!"
    exit 1
}

echo "✅ Package built successfully!"
echo "📦 Files created:"
ls -la dist/

# Ask for publishing preference
echo ""
echo "🚀 Ready to publish! Choose option:"
echo "1) Test PyPI (recommended first)"
echo "2) Production PyPI"
echo "3) Skip publishing"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "📤 Publishing to Test PyPI..."
        uv tool run twine upload --repository testpypi dist/*
        echo "✅ Published to Test PyPI!"
        echo "🔗 https://test.pypi.org/project/modal-for-noobs/"
        echo "📥 Test: pip install --index-url https://test.pypi.org/simple/ modal-for-noobs"
        ;;
    2)
        echo "⚠️  Publishing to PRODUCTION PyPI..."
        read -p "Are you absolutely sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            uv tool run twine upload dist/*
            echo "✅ Published to PyPI!"
            echo "🔗 https://pypi.org/project/modal-for-noobs/"
            echo "📥 Install: pip install modal-for-noobs"
        else
            echo "❌ Cancelled"
        fi
        ;;
    3)
        echo "📦 Build complete. Files ready in dist/"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Done! F-string syntax error has been fixed and packaged."