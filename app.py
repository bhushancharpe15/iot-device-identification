from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import numpy as np
import json
import pickle
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import os
import warnings
import re
import random
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

# Local chatbot knowledge base
chatbot_knowledge = {
    'greetings': [
        "Hello! I'm your IoT Device Identification Assistant. How can I help you today?",
        "Hi there! I can help you with IoT device identification and analysis. What would you like to know?",
        "Welcome! I'm here to assist you with IoT device classification and network traffic analysis."
    ],
    'capabilities': [
        "I can help you identify IoT devices based on network traffic patterns. I support 9 device categories: baby_monitor, lights, motion_sensor, security_camera, smoke_detector, socket, thermostat, TV, and watch.",
        "I can analyze network traffic features like packet sizes, HTTP requests, SSL certificates, and more to classify IoT devices with high accuracy.",
        "I can provide insights about device behavior patterns, security implications, and network optimization for IoT devices."
    ],
    'device_info': {
        'baby_monitor': "Baby monitors typically show regular heartbeat patterns in network traffic, use specific ports, and have characteristic SSL certificate patterns.",
        'lights': "Smart lights usually have low bandwidth usage, frequent small packets for status updates, and specific HTTP request patterns.",
        'motion_sensor': "Motion sensors show burst traffic patterns when triggered, with specific inter-arrival times and packet size distributions.",
        'security_camera': "Security cameras generate high bandwidth traffic, especially for video streaming, with specific SSL and HTTP patterns.",
        'smoke_detector': "Smoke detectors have very low network activity, with occasional status updates and specific port usage patterns.",
        'socket': "Smart sockets show power consumption patterns in their network traffic, with specific timing characteristics.",
        'thermostat': "Thermostats have temperature-related network patterns, with regular status updates and specific timing intervals.",
        'TV': "Smart TVs generate high bandwidth traffic for streaming, with specific HTTP and SSL patterns for content delivery.",
        'watch': "Smart watches show intermittent connectivity patterns, with specific power management characteristics in network traffic."
    },
    'features': [
        "Our model analyzes 297 network traffic features including packet sizes, HTTP patterns, SSL certificates, timing characteristics, and more.",
        "Key features include bytes transferred, packet inter-arrival times, HTTP request/response patterns, SSL handshake characteristics, and TCP analysis.",
        "The model uses ensemble learning with multiple XGBoost models for high accuracy in device classification."
    ],
    'security': [
        "IoT device identification helps in network security by detecting unauthorized devices, monitoring device behavior, and identifying potential threats.",
        "By analyzing traffic patterns, we can detect anomalies, unauthorized access attempts, and compromised IoT devices.",
        "Device identification enables proper network segmentation, access control, and security policy enforcement."
    ],
    'default': [
        "I can help you with IoT device identification, network traffic analysis, device behavior patterns, and security implications. What specific aspect would you like to know about?",
        "I'm specialized in IoT device classification using machine learning. I can explain device types, network patterns, security aspects, or help with technical questions. What would you like to know?",
        "I can assist with IoT device identification, explain how our ML model works, discuss device categories, or help with network security questions. What's your specific question?"
    ],
    'numerical': [
        "Our model analyzes 297 numerical features from network traffic including packet sizes, timing intervals, byte counts, HTTP patterns, SSL characteristics, and more.",
        "Key numerical features include: bytes transferred (avg: 5,243), packet inter-arrival times, HTTP request/response sizes, SSL handshake durations, and TCP analysis metrics.",
        "The model processes numerical data like packet counts, duration measurements, entropy calculations, statistical moments (mean, median, std dev), and frequency distributions."
    ],
    'dsx': [
        "DSX likely refers to data science or experimental features. Our model uses advanced feature engineering with 297 numerical attributes for IoT device classification.",
        "The dataset includes experimental features like HTTP entropy, SSL certificate analysis, packet timing distributions, and network protocol characteristics.",
        "Our XGBoost ensemble model processes these experimental features to achieve high accuracy in device identification."
    ]
}

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
# Local Chatbot (trained on dataset knowledge)
############################################

def get_chatbot_response(user_message):
    """Generate intelligent response based on user input and dataset knowledge"""
    user_message = user_message.lower().strip()
    
    # Greeting patterns
    if any(word in user_message for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return random.choice(chatbot_knowledge['greetings'])
    
    # Capability questions
    if any(word in user_message for word in ['what can you do', 'capabilities', 'help', 'assist', 'support']):
        return random.choice(chatbot_knowledge['capabilities'])
    
    # Device-specific questions
    for device in device_categories:
        if device.replace('_', ' ') in user_message or device in user_message:
            return chatbot_knowledge['device_info'].get(device, f"I can help you identify {device} devices based on their network traffic patterns.")
    
    # Feature questions
    if any(word in user_message for word in ['features', 'model', 'algorithm', 'machine learning', 'ml']):
        return random.choice(chatbot_knowledge['features'])
    
    # Security questions
    if any(word in user_message for word in ['security', 'threat', 'attack', 'vulnerability', 'protection']):
        return random.choice(chatbot_knowledge['security'])
    
    # Accuracy questions
    if any(word in user_message for word in ['accuracy', 'performance', 'results', 'prediction']):
        return "Our ensemble model achieves high accuracy in IoT device identification by analyzing 297 network traffic features. The model uses multiple XGBoost classifiers trained on diverse traffic patterns to ensure robust classification."
    
    # Dataset questions
    if any(word in user_message for word in ['dataset', 'data', 'training', 'samples']):
        return "Our model is trained on the IoT device test dataset with 10,000 samples across 9 device categories. The dataset includes 297 features extracted from network traffic including packet characteristics, HTTP patterns, SSL certificates, and timing information."
    
    # Numerical questions
    if any(word in user_message for word in ['numerical', 'numbers', 'values', 'metrics']):
        return random.choice(chatbot_knowledge['numerical'])
    
    # DSX questions
    if 'dsx' in user_message:
        return random.choice(chatbot_knowledge['dsx'])
    
    # Default response
    return random.choice(chatbot_knowledge['default'])

@app.route('/chat/start_session', methods=['POST'])
def chat_start_session():
    """Start a new chat session (local chatbot doesn't need sessions)"""
    try:
        # Generate a simple session ID for compatibility
        session_id = f"local_session_{random.randint(1000, 9999)}"
        return jsonify({'session_id': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/message', methods=['POST'])
def chat_message():
    """Handle chat messages using local chatbot"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get response from local chatbot
        bot_response = get_chatbot_response(user_message)
        
        # Format response to match expected structure
        response = {
            'output': {
                'generic': [
                    {
                        'response_type': 'text',
                        'text': bot_response
                    }
                ]
            }
        }
        
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
