#!/bin/bash

# IoT Device Identification System - GitHub Setup Script
# This script helps you set up the project for GitHub hosting

echo "🚀 Setting up IoT Device Identification System for GitHub..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
fi

# Add all files to git
echo "📝 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: IoT Device Identification System

- Complete Flask web application
- XGBoost model integration
- Modern responsive UI
- Interactive device prediction
- Sample data loading
- Real-time confidence scoring
- Beautiful visualizations"

echo "✅ Git repository initialized successfully!"
echo ""
echo "🔗 Next steps to host on GitHub:"
echo "1. Go to https://github.com and create a new repository"
echo "2. Name it 'iot-device-identification' (or your preferred name)"
echo "3. Don't initialize with README (we already have one)"
echo "4. Copy the repository URL"
echo "5. Run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/iot-device-identification.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🎉 Your project will then be live on GitHub!"
echo ""
echo "📋 For deployment options, check the README.md file"
echo "   - Heroku (recommended)"
echo "   - Railway"
echo "   - Render"
echo ""
echo "Happy coding! 🚀"

