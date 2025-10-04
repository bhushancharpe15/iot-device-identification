#!/usr/bin/env python3
"""
Startup script for IoT Device Identification System
This script provides an easy way to start the application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 'xgboost'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_files():
    """Check if all required files are present"""
    print("\nChecking required files...")
    
    required_files = [
        'app.py',
        'best_xgb_model.json',
        'iot_device_test_augmented_10k.csv',
        'requirements.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present!")
    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("IoT Device Identification System - Startup")
    print("=" * 60)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check files
    files_ok = check_files()
    
    if not deps_ok or not files_ok:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        return 1
    
    print("\n🚀 Starting the application...")
    print("=" * 60)
    print("The web application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Import and run the app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user.")
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

