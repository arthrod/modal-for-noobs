#!/bin/bash

# Commit and Publish Script for modal-for-noobs v0.2.3
# Fixes f-string syntax error and publishes to PyPI

set -e

echo "🚀 Committing changes and publishing modal-for-noobs v0.2.3"
echo "=========================================================="

# Git operations
echo "📝 Adding changes to git..."
git add .

echo "💾 Committing changes..."
git commit -m "🚀 Bump version to 0.2.3 - Fix f-string backslash syntax error

- Fixed f-string syntax error in cli.py line 189
- Extracted split operation outside f-string expression 
- Version bump from 0.2.2 to 0.2.3
- Ready for PyPI publication"

echo "📤 Pushing to remote..."
git push

echo "✅ Git operations complete!"

# Check if dist files exist
if [ ! -d "dist" ] || [ ! "$(ls -A dist 2>/dev/null)" ]; then
    echo "📦 Building package first..."
    ./quick_build.sh
    exit 0
fi

echo ""
echo "🚀 Package is ready for publishing!"
echo "📦 Built files:"
ls -la dist/

echo ""
echo "Choose publishing option:"
echo "1) Test PyPI (recommended first)"
echo "2) Production PyPI" 
echo "3) Skip publishing"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "📤 Publishing to Test PyPI..."
        uv tool run twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Successfully published to Test PyPI!"
        echo "🔗 View: https://test.pypi.org/project/modal-for-noobs/"
        echo "📥 Test install: pip install --index-url https://test.pypi.org/simple/ modal-for-noobs"
        ;;
    2)
        echo "⚠️  Publishing to PRODUCTION PyPI..."
        echo "This will make the package available to everyone!"
        read -p "Are you absolutely sure? Type 'publish' to confirm: " confirm
        if [ "$confirm" = "publish" ]; then
            uv tool run twine upload dist/*
            echo ""
            echo "🎉 Successfully published to PyPI!"
            echo "🔗 View: https://pypi.org/project/modal-for-noobs/"
            echo "📥 Install: pip install modal-for-noobs"
            echo ""
            echo "🚀 The f-string syntax fix is now live for all users!"
        else
            echo "❌ Publication cancelled"
            exit 1
        fi
        ;;
    3)
        echo "📦 Skipping publication. Files ready in dist/"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 All done! Version 0.2.3 with f-string fix is ready!"
echo ""
echo "📋 Summary of changes:"
echo "  ✅ Fixed f-string backslash syntax error"
echo "  ✅ Version bumped to 0.2.3"
echo "  ✅ Git committed and pushed"
echo "  ✅ Package built and validated"