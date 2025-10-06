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

# Global variables for models and scaler
models = []
scaler = None
feature_columns = None
device_categories = [
    'baby_monitor', 'lights', 'motion_sensor', 'security_camera', 
    'smoke_detector', 'socket', 'thermostat', 'TV', 'watch'
]

def load_model():
    """Load trained models (ensemble) and prepare feature columns"""
    global models, scaler, feature_columns, device_categories
    try:
        models = []

        # Prefer models from "trained model final" directory if present
        trained_dir = os.path.join(os.getcwd(), 'trained model final')

        loaded_from_trained_dir = False
        if os.path.isdir(trained_dir):
            # Load label encoder if available to get class names
            label_path = os.path.join(trained_dir, 'label_encoder.pkl')
            if os.path.exists(label_path):
                try:
                    with open(label_path, 'rb') as f:
                        le = pickle.load(f)
                    if hasattr(le, 'classes_'):
                        device_categories = [str(c) for c in le.classes_]
                except Exception:
                    pass

            # Load any sklearn-compatible models in directory (exclude label encoder)
            for fname in os.listdir(trained_dir):
                if not fname.lower().endswith('.pkl'):
                    continue
                if 'label' in fname.lower():
                    continue
                fpath = os.path.join(trained_dir, fname)
                try:
                    with open(fpath, 'rb') as f:
                        m = pickle.load(f)
                    # Must have predict_proba
                    if hasattr(m, 'predict_proba'):
                        models.append(m)
                        loaded_from_trained_dir = True
                except Exception:
                    continue

        # Fallback: load legacy XGBoost booster JSON as a wrapper
        if not models:
            booster_path = os.path.join(os.getcwd(), 'best_xgb_model.json')
            if os.path.exists(booster_path):
                booster = xgb.Booster()
                booster.load_model(booster_path)

                class BoosterWrapper:
                    def __init__(self, booster):
                        self.booster = booster
                    def predict_proba(self, X):
                        dmat = xgb.DMatrix(X)
                        proba = self.booster.predict(dmat, output_margin=False)
                        return proba

                models.append(BoosterWrapper(booster))

        if not models:
            raise RuntimeError('No models could be loaded.')

        # Load the dataset to get feature columns
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        feature_columns = [col for col in df.columns if col != 'device_category']

        # Create a scaler (fit on dataset features)
        scaler = StandardScaler()
        scaler.fit(df[feature_columns])

        src = 'trained model final' if loaded_from_trained_dir else 'best_xgb_model.json'
        print(f"Loaded {len(models)} model(s) from {src} with {len(feature_columns)} features")
        print(f"Classes: {device_categories}")
        return True
    except Exception as e:
        print(f"Error loading model(s): {str(e)}")
        return False

def predict_device_category(features):
    """Predict device category from input features using ensemble average"""
    try:
        # Convert features to numpy array and reshape
        features_array = np.array(features).reshape(1, -1)

        # Scale the features
        features_scaled = scaler.transform(features_array)

        # Aggregate probabilities across models
        proba_sum = None
        for m in models:
            proba = m.predict_proba(features_scaled)
            # Ensure shape (1, n_classes)
            proba = np.array(proba)
            if proba.ndim == 1:
                proba = proba.reshape(1, -1)
            if proba_sum is None:
                proba_sum = np.zeros_like(proba, dtype=float)
            proba_sum += proba

        avg_proba = proba_sum / max(len(models), 1)

        # Align number of classes if needed
        n_classes = len(device_categories)
        if avg_proba.shape[1] != n_classes:
            # If mismatch, truncate/pad
            if avg_proba.shape[1] > n_classes:
                avg_proba = avg_proba[:, :n_classes]
            else:
                pad = np.zeros((avg_proba.shape[0], n_classes - avg_proba.shape[1]))
                avg_proba = np.concatenate([avg_proba, pad], axis=1)

        # Normalize to probabilities
        row_sum = avg_proba.sum(axis=1, keepdims=True)
        row_sum[row_sum == 0] = 1.0
        avg_proba = avg_proba / row_sum

        # Get the predicted class
        predicted_class_idx = int(np.argmax(avg_proba[0]))
        predicted_class = device_categories[predicted_class_idx]

        # Build confidence dict
        confidence_scores = {device_categories[i]: float(avg_proba[0][i]) for i in range(n_classes)}
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
