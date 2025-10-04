#!/bin/bash

echo "🚀 Creating GitHub Repository for IoT Device Identification System"
echo "================================================================"

# Your GitHub username
GITHUB_USERNAME="bhushancharpe15"
REPO_NAME="iot-device-identification"

echo "📋 Repository Details:"
echo "   Username: $GITHUB_USERNAME"
echo "   Repository: $REPO_NAME"
echo "   URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

echo "🔗 Step 1: Create Repository on GitHub"
echo "======================================"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: Advanced IoT Device Identification System using XGBoost and Flask"
echo "4. Make it PUBLIC"
echo "5. DO NOT initialize with README (we already have one)"
echo "6. Click 'Create repository'"
echo ""

echo "⏳ Waiting for you to create the repository..."
echo "Press ENTER when you've created the repository on GitHub"
read -p ""

echo ""
echo "🚀 Step 2: Pushing Code to GitHub"
echo "================================="

# Add remote origin
echo "Adding GitHub as remote origin..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Rename branch to main
echo "Renaming branch to main..."
git branch -M main

# Push to GitHub
echo "Pushing code to GitHub..."
git push -u origin main

echo ""
echo "✅ SUCCESS! Your repository is now live on GitHub!"
echo "🌐 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "🎉 Next Steps:"
echo "1. Visit your repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "2. Check the DEPLOYMENT.md file for hosting options"
echo "3. Deploy to Heroku, Railway, or Render to make it live!"
echo ""
echo "📚 Documentation included:"
echo "   - README.md: Complete project documentation"
echo "   - DEPLOYMENT.md: How to deploy to cloud platforms"
echo "   - GITHUB_SETUP.md: Setup instructions"
echo ""
echo "🎯 Your IoT Device Identification System is ready to go live! 🚀"
