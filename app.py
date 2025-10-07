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
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv('.env.local')
# Also support IBM exported credentials file name if present
load_dotenv('ibm-credentials.env')
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
    """Load trained models (ensemble) from 'trained model final' ONLY and prepare feature columns"""
    global models, scaler, feature_columns, device_categories
    try:
        models = []

        # Enforce loading from the specific directory
        trained_dir = os.path.join(os.getcwd(), 'trained model final')
        if not os.path.isdir(trained_dir):
            raise RuntimeError("Required directory 'trained model final' not found")

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
            except Exception:
                continue

        if not models:
            raise RuntimeError("No sklearn-compatible models (.pkl with predict_proba) found in 'trained model final'")

        # Load the dataset to get feature columns
        df = pd.read_csv('iot_device_test_augmented_10k.csv')
        feature_columns = [col for col in df.columns if col != 'device_category']

        # Create a scaler (fit on dataset features)
        scaler = StandardScaler()
        scaler.fit(df[feature_columns])

        print(f"Loaded {len(models)} model(s) from 'trained model final' with {len(feature_columns)} features")
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

############################################
# IBM Watson Assistant proxy (backend)
############################################

def get_watson_client():
    api_key = os.getenv('ASSISTANT_APIKEY') or os.getenv('ASSISTANT_IAM_APIKEY')
    url = os.getenv('ASSISTANT_URL')
    if not api_key or not url:
        raise RuntimeError('Watson Assistant API credentials not set in environment.')
    authenticator = IAMAuthenticator(api_key)
    assistant = AssistantV2(version='2021-11-27', authenticator=authenticator)
    assistant.set_service_url(url)
    return assistant

@app.route('/chat/start_session', methods=['POST'])
def chat_start_session():
    try:
        assistant_id = os.getenv('ASSISTANT_ID')
        if not assistant_id:
            return jsonify({'error': 'ASSISTANT_ID not configured on server'}), 500
        assistant = get_watson_client()
        session = assistant.create_session(assistant_id=assistant_id).get_result()
        return jsonify(session)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/message', methods=['POST'])
def chat_message():
    try:
        data = request.get_json(force=True)
        assistant_id = os.getenv('ASSISTANT_ID')
        session_id = data.get('session_id')
        message = data.get('message', '')
        if not assistant_id or not session_id:
            return jsonify({'error': 'Missing assistant_id or session_id'}), 400
        assistant = get_watson_client()
        response = assistant.message(
            assistant_id=assistant_id,
            session_id=session_id,
            input={'message_type': 'text', 'text': message}
        ).get_result()
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
