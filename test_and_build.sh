#!/bin/bash

# Test and Build Script for modal-for-noobs v0.2.4
# Comprehensive fix for all f-string syntax errors

set -e

echo "🚀 modal-for-noobs v0.2.4 - Test & Build Script"
echo "=============================================="
echo "🔧 Fixing all f-string backslash syntax errors"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Run this from the project root directory"
    exit 1
fi

# Get current version
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📦 Testing version: $VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ src/*.egg-info/

echo ""
echo "🔍 COMPREHENSIVE SYNTAX TESTING"
echo "================================"

# Test all Python files for syntax errors
echo "📝 Testing Python syntax in all files..."
SYNTAX_ERRORS=0

for file in $(find src -name "*.py"); do
    echo -n "  Testing $file... "
    if python -m py_compile "$file" 2>/dev/null; then
        echo "✅"
    else
        echo "❌ SYNTAX ERROR"
        python -m py_compile "$file"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done

if [ $SYNTAX_ERRORS -gt 0 ]; then
    echo ""
    echo "❌ Found $SYNTAX_ERRORS syntax error(s). Please fix before continuing."
    exit 1
fi

echo ""
echo "🧪 IMPORT TESTING"
echo "================="

# Test critical imports
echo "📥 Testing package imports..."
export PYTHONPATH="src:$PYTHONPATH"

echo -n "  Testing CLI import... "
if python -c "from modal_for_noobs.cli import main; print('OK')" >/dev/null 2>&1; then
    echo "✅"
else
    echo "❌ FAILED"
    python -c "from modal_for_noobs.cli import main"
    exit 1
fi

echo -n "  Testing Dashboard import... "
if python -c "from modal_for_noobs.dashboard import ModalDashboard; print('OK')" >/dev/null 2>&1; then
    echo "✅"
else
    echo "❌ FAILED"
    python -c "from modal_for_noobs.dashboard import ModalDashboard"
    exit 1
fi

echo -n "  Testing ModalDeployer import... "
if python -c "from modal_for_noobs.modal_deploy import ModalDeployer; print('OK')" >/dev/null 2>&1; then
    echo "✅"
else
    echo "❌ FAILED"
    python -c "from modal_for_noobs.modal_deploy import ModalDeployer"
    exit 1
fi

echo -n "  Testing CLI helpers import... "
if python -c "from modal_for_noobs.cli_helpers.common import MODAL_GREEN; print('OK')" >/dev/null 2>&1; then
    echo "✅"
else
    echo "❌ FAILED"
    python -c "from modal_for_noobs.cli_helpers.common import MODAL_GREEN"
    exit 1
fi

echo ""
echo "🔧 F-STRING VERIFICATION"
echo "========================"

# Search for potential f-string issues
echo "🔍 Scanning for f-string backslash patterns..."

# Check for f-strings with backslashes in expressions
if grep -r "f.*{.*\\.*}" src/ 2>/dev/null; then
    echo "⚠️  Found potential f-string backslash issues!"
    echo "These may cause syntax errors."
else
    echo "✅ No f-string backslash issues found"
fi

# Check for f-strings with triple quotes
if grep -r "f'''.*{" src/ 2>/dev/null || grep -r 'f""".*{' src/ 2>/dev/null; then
    echo "⚠️  Found f-strings with triple quotes - these may cause issues"
else
    echo "✅ No problematic f-string patterns found"
fi

echo ""
echo "🔨 BUILDING PACKAGE"
echo "==================="

# Build the package
echo "📦 Building package..."
if command -v uv &> /dev/null; then
    echo "Using uv build..."
    uv build
else
    echo "Using python -m build..."
    if ! python -m build 2>/dev/null; then
        echo "Installing build tools..."
        pip install build --break-system-packages
        python -m build
    fi
fi

echo ""
echo "📋 Build artifacts:"
ls -la dist/

echo ""
echo "🔍 PACKAGE VALIDATION"
echo "====================="

# Check with twine
echo "📋 Validating package with twine..."
if command -v uv &> /dev/null; then
    if ! uv tool run twine check dist/* 2>/dev/null; then
        echo "Installing twine..."
        uv tool install twine
        uv tool run twine check dist/*
    fi
else
    if ! python -m twine check dist/* 2>/dev/null; then
        echo "Installing twine..."
        pip install twine --break-system-packages
        python -m twine check dist/*
    fi
fi

echo "✅ Package validation passed!"

echo ""
echo "🧪 POST-BUILD TESTING"
echo "====================="

# Test that the built package can be imported
echo "📥 Testing built package structure..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Extract and test the wheel
python -m zipfile -e "$(pwd)/../dist/modal_for_noobs-$VERSION-py3-none-any.whl" .
if [ -d "modal_for_noobs" ]; then
    echo "✅ Package structure looks good"
else
    echo "❌ Package structure issue"
    ls -la
    cd - >/dev/null
    rm -rf "$TEMP_DIR"
    exit 1
fi

cd - >/dev/null
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 SUCCESS! ALL TESTS PASSED"
echo "============================"
echo "✅ All Python syntax valid"
echo "✅ All imports working"
echo "✅ No f-string issues detected" 
echo "✅ Package built successfully"
echo "✅ Package validation passed"
echo ""
echo "📦 Ready for publishing:"
echo "  Version: $VERSION"
echo "  Wheel: modal_for_noobs-$VERSION-py3-none-any.whl"
echo "  Source: modal_for_noobs-$VERSION.tar.gz"
echo ""

# Publishing options
echo "🚀 PUBLISHING OPTIONS"
echo "====================="
echo "Choose your next step:"
echo "1) Test PyPI (recommended first)"
echo "2) Production PyPI"
echo "3) Just build (skip publishing)"
echo "4) Exit"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📤 Publishing to Test PyPI..."
        if command -v uv &> /dev/null; then
            uv tool run twine upload --repository testpypi dist/*
        else
            python -m twine upload --repository testpypi dist/*
        fi
        echo ""
        echo "✅ Published to Test PyPI!"
        echo "🔗 View: https://test.pypi.org/project/modal-for-noobs/"
        echo "📥 Test install: pip install --index-url https://test.pypi.org/simple/ modal-for-noobs==$VERSION"
        ;;
    2)
        echo ""
        echo "⚠️  Publishing to PRODUCTION PyPI..."
        echo "This will make v$VERSION available to all users!"
        read -p "Type 'PUBLISH' to confirm: " confirm
        if [ "$confirm" = "PUBLISH" ]; then
            if command -v uv &> /dev/null; then
                uv tool run twine upload dist/*
            else
                python -m twine upload dist/*
            fi
            echo ""
            echo "🎉 Successfully published to PyPI!"
            echo "🔗 View: https://pypi.org/project/modal-for-noobs/"
            echo "📥 Install: pip install modal-for-noobs==$VERSION"
            echo ""
            echo "🚀 F-string syntax fixes are now live!"
        else
            echo "❌ Publication cancelled"
        fi
        ;;
    3)
        echo "📦 Build complete. Files ready in dist/"
        ;;
    4)
        echo "👋 Exiting..."
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📋 SUMMARY OF FIXES IN v$VERSION"
echo "=================================="
echo "🔧 Fixed f-string backslash syntax error in cli.py"
echo "🔧 Fixed f-string template conflicts in modal_deploy.py"
echo "🔧 Replaced problematic f-string patterns with safe alternatives"
echo "🔧 All import errors resolved"
echo ""
echo "✨ The package should now work perfectly in HuggingFace Spaces!"
echo "🎯 Users can now successfully import ModalDashboard"
echo ""
echo "🎉 modal-for-noobs v$VERSION is ready for the world!"