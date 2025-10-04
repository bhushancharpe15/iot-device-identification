#!/usr/bin/env python3
"""
Test script for IoT Device Identification System
This script tests the model loading and basic functionality
"""

import sys
import os
import pandas as pd
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_loading():
    """Test if the model can be loaded successfully"""
    print("Testing model loading...")
    
    try:
        from app import load_model, predict_device_category
        
        # Test model loading
        success = load_model()
        if success:
            print("✅ Model loaded successfully!")
        else:
            print("❌ Model loading failed!")
            return False
            
        # Test prediction with sample data
        print("\nTesting prediction with sample data...")
        
        # Load a sample from the dataset
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        sample = df.iloc[0]
        
        # Extract features (exclude device_category)
        features = [sample[col] for col in df.columns if col != 'device_category']
        
        # Make prediction
        predicted_class, confidence_scores = predict_device_category(features)
        
        if predicted_class:
            print(f"✅ Prediction successful!")
            print(f"   Predicted: {predicted_class}")
            print(f"   Actual: {sample['device_category']}")
            print(f"   Confidence: {confidence_scores[predicted_class]:.4f}")
            
            # Show top 3 predictions
            sorted_scores = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
            print(f"\n   Top 3 predictions:")
            for i, (device, score) in enumerate(sorted_scores[:3]):
                print(f"   {i+1}. {device}: {score:.4f}")
        else:
            print("❌ Prediction failed!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def test_dataset_info():
    """Test dataset information"""
    print("\nTesting dataset information...")
    
    try:
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        
        print(f"✅ Dataset loaded successfully!")
        print(f"   Total samples: {len(df)}")
        print(f"   Total features: {len(df.columns) - 1}")  # Exclude target column
        
        # Check device categories
        categories = df['device_category'].value_counts()
        print(f"   Device categories: {len(categories)}")
        print(f"   Category distribution:")
        for category, count in categories.items():
            print(f"     - {category}: {count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error loading dataset: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("IoT Device Identification System - Test Suite")
    print("=" * 50)
    
    # Test dataset
    dataset_ok = test_dataset_info()
    
    # Test model
    model_ok = test_model_loading()
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    print(f"Dataset: {'✅ PASS' if dataset_ok else '❌ FAIL'}")
    print(f"Model:   {'✅ PASS' if model_ok else '❌ FAIL'}")
    
    if dataset_ok and model_ok:
        print("\n🎉 All tests passed! The application is ready to run.")
        print("\nTo start the web application, run:")
        print("   python app.py")
        print("\nThen open your browser to: http://localhost:5000")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

