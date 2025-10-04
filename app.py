from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import numpy as np
import json
import pickle
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'iot_device_identification_secret_key_2024'

# Global variables for model and scaler
model = None
scaler = None
feature_columns = None
device_categories = [
    'baby_monitor', 'lights', 'motion_sensor', 'security_camera', 
    'smoke_detector', 'socket', 'thermostat', 'TV', 'watch'
]

def load_model():
    """Load the trained XGBoost model and prepare feature columns"""
    global model, scaler, feature_columns
    
    try:
        # Load the XGBoost model
        model = xgb.Booster()
        model.load_model('best_xgb_model.json')
        
        # Load the dataset to get feature columns
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        feature_columns = [col for col in df.columns if col != 'device_category']
        
        # Create a scaler (we'll fit it on the training data)
        scaler = StandardScaler()
        scaler.fit(df[feature_columns])
        
        print(f"Model loaded successfully with {len(feature_columns)} features")
        return True
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return False

def predict_device_category(features):
    """Predict device category from input features"""
    try:
        # Convert features to numpy array and reshape
        features_array = np.array(features).reshape(1, -1)
        
        # Scale the features
        features_scaled = scaler.transform(features_array)
        
        # Convert to DMatrix for XGBoost
        dmatrix = xgb.DMatrix(features_scaled)
        
        # Get prediction probabilities (this gives us probabilities for all classes)
        prediction_proba = model.predict(dmatrix, output_margin=False)
        
        # Get the predicted class (index of highest probability)
        predicted_class_idx = np.argmax(prediction_proba[0])  # [0] because we have one sample
        predicted_class = device_categories[predicted_class_idx]
        
        # Get confidence scores for all classes
        confidence_scores = {}
        for i, category in enumerate(device_categories):
            confidence_scores[category] = float(prediction_proba[0][i])  # [0] because we have one sample
        
        return predicted_class, confidence_scores
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return None, None

@app.route('/')
def index():
    """Main page with device identification form"""
    return render_template('index.html', 
                         feature_columns=feature_columns,
                         device_categories=device_categories)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Convert form data to feature array
        features = []
        for col in feature_columns:
            value = form_data.get(col, '0')
            try:
                features.append(float(value))
            except ValueError:
                features.append(0.0)
        
        # Make prediction
        predicted_class, confidence_scores = predict_device_category(features)
        
        if predicted_class is None:
            return jsonify({'error': 'Prediction failed'}), 500
        
        # Sort confidence scores by probability
        sorted_confidence = sorted(confidence_scores.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        return jsonify({
            'predicted_class': predicted_class,
            'confidence_scores': confidence_scores,
            'sorted_confidence': sorted_confidence,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample_data')
def sample_data():
    """Get sample data from the dataset"""
    try:
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        # Get a random sample
        sample = df.sample(n=1).iloc[0]
        
        sample_data = {}
        for col in feature_columns:
            sample_data[col] = float(sample[col])
        
        sample_data['actual_category'] = sample['device_category']
        
        return jsonify(sample_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dataset_info')
def dataset_info():
    """Get information about the dataset"""
    try:
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        
        # Count device categories
        category_counts = df['device_category'].value_counts().to_dict()
        
        # Get basic statistics
        stats = {
            'total_samples': len(df),
            'total_features': len(feature_columns),
            'device_categories': list(category_counts.keys()),
            'category_counts': category_counts
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        print("Starting IoT Device Identification Web Application...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to load model. Please check the model file.")
