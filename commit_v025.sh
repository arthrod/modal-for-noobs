#!/bin/bash

# Commit and push v0.2.5 changes to GitHub
# This script handles the version bump and new dashboard improvements

echo "🚀 Committing modal-for-noobs v0.2.5 changes..."

# Add all changes
git add .

# Create commit with detailed message
git commit -m "🎉 v0.2.5: Simplified Modal authentication with web-based flow

✨ New Features:
- Replaced manual token input with secure web-based authentication
- One-click Modal login using 'modal token new' command
- Automatic token validation and verification
- Cleaner, more user-friendly interface

🔧 Improvements:
- Updated Python requirement from >=3.9 to >=3.10
- Fixed license from MIT to Apache-2.0
- Streamlined deployment flow (no manual token passing)
- Better error messages and status feedback
- Enhanced UX with clear authentication instructions

🐛 Bug Fixes:
- Fixed dashboard showing success without proper token validation
- Added proper enter key support for all inputs
- Improved token format handling and validation

💻 Technical Changes:
- Removed complex token ID/secret input fields
- Integrated Modal CLI web authentication flow
- Enhanced authentication status checking
- Updated all function signatures to remove token parameters"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin master

# Create and push tag
echo "🏷️ Creating version tag..."
git tag v0.2.5
git push origin v0.2.5

echo "✅ Successfully committed and pushed v0.2.5 to GitHub!"
echo "🌐 Changes are now live on: https://github.com/your-username/modal-for-noobs"