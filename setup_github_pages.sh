#!/bin/bash

echo "🚀 Setting up GitHub Pages for IoT Device Identification System"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📁 Creating static site directory..."
mkdir -p static_site

echo "✅ Static site files created successfully!"
echo ""

echo "🔧 Next Steps to Enable GitHub Pages:"
echo "====================================="
echo ""
echo "1. Push the changes to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add GitHub Pages static site'"
echo "   git push origin main"
echo ""
echo "2. Enable GitHub Pages in your repository:"
echo "   - Go to: https://github.com/bhushancharpe15/iot-device-identification/settings/pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main"
echo "   - Folder: /static_site"
echo "   - Click 'Save'"
echo ""
echo "3. Wait for deployment (2-3 minutes)"
echo ""
echo "4. Your site will be live at:"
echo "   https://bhushancharpe15.github.io/iot-device-identification/"
echo ""
echo "🎉 Your IoT Device Identification System will be live on GitHub Pages!"
echo ""
echo "📋 What's included in the static site:"
echo "   ✅ Beautiful, responsive design"
echo "   ✅ Interactive demo interface"
echo "   ✅ Sample predictions display"
echo "   ✅ Confidence visualization"
echo "   ✅ Device categories showcase"
echo "   ✅ Technical features overview"
echo "   ✅ Links to full project"
echo ""
echo "🔗 The static site provides a great showcase of your project"
echo "   while the full interactive version is available in the repository!"

