#!/bin/bash

# Build and Publish Script for modal-for-noobs
# Fixes f-string syntax error and publishes to PyPI

set -e  # Exit on any error

echo "🚀 Modal-for-noobs Build & Publish Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Parse command line arguments
DRY_RUN=false
TEST_PYPI=false
PROD_PYPI=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --test)
            TEST_PYPI=true
            shift
            ;;
        --prod)
            PROD_PYPI=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--test] [--prod]"
            echo "  --dry-run: Build only, don't publish"
            echo "  --test:    Publish to Test PyPI"
            echo "  --prod:    Publish to production PyPI"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Show current version
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📦 Current version: $VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/
rm -rf build/
rm -rf src/*.egg-info/

# Verify syntax fix is in place
echo "🔍 Verifying f-string syntax fix..."
if grep -q "remaining_packages = len(req_lines) - 5" src/modal_for_noobs/cli.py; then
    echo "✅ F-string syntax fix confirmed"
else
    echo "❌ F-string syntax fix not found! Please check cli.py"
    exit 1
fi

# Test syntax compilation
echo "🧪 Testing Python syntax..."
python -m py_compile src/modal_for_noobs/cli.py
python -c "import ast; ast.parse(open('src/modal_for_noobs/cli.py').read())"
echo "✅ Syntax check passed"

# Test import
echo "🧪 Testing package imports..."
export PYTHONPATH="src:$PYTHONPATH"
python -c "from modal_for_noobs.cli import main; print('✅ CLI import successful')"
python -c "from modal_for_noobs.dashboard import ModalDashboard; print('✅ Dashboard import successful')"

# Build the package
echo "🔨 Building package..."
if command -v uv &> /dev/null; then
    echo "Using uv build..."
    uv build
else
    echo "Using python -m build..."
    python -m build
fi

# Verify build artifacts
echo "📋 Build artifacts:"
ls -la dist/

# Check with twine
echo "🔍 Checking package with twine..."
if command -v uv &> /dev/null; then
    uv tool run twine check dist/*
else
    twine check dist/*
fi
echo "✅ Package check passed"

if [ "$DRY_RUN" = true ]; then
    echo "🏁 Dry run complete! Package built successfully."
    echo "📦 Built files:"
    ls -la dist/
    exit 0
fi

# Publishing logic
if [ "$TEST_PYPI" = true ]; then
    echo "🧪 Publishing to Test PyPI..."
    if command -v uv &> /dev/null; then
        uv tool run twine upload --repository testpypi dist/*
    else
        twine upload --repository testpypi dist/*
    fi
    echo "✅ Published to Test PyPI!"
    echo "🔗 View at: https://test.pypi.org/project/modal-for-noobs/"
    echo "📥 Test install: pip install --index-url https://test.pypi.org/simple/ modal-for-noobs"
    
elif [ "$PROD_PYPI" = true ]; then
    echo "🚀 Publishing to production PyPI..."
    echo "⚠️  WARNING: This will publish to the live PyPI!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v uv &> /dev/null; then
            uv tool run twine upload dist/*
        else
            twine upload dist/*
        fi
        echo "✅ Published to PyPI!"
        echo "🔗 View at: https://pypi.org/project/modal-for-noobs/"
        echo "📥 Install: pip install modal-for-noobs"
    else
        echo "❌ Publication cancelled"
        exit 1
    fi
else
    echo "ℹ️  Build complete! Use --test or --prod to publish."
    echo "📦 Built files ready in dist/"
    echo ""
    echo "Next steps:"
    echo "  • Test PyPI: $0 --test"
    echo "  • Production: $0 --prod"
fi

echo ""
echo "🎉 Build script completed successfully!"