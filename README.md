# IoT Device Identification System

A comprehensive web application for identifying IoT devices based on their network traffic patterns using machine learning. This system uses XGBoost to analyze network traffic features and accurately classify different types of IoT devices.

## 🚀 Features

- **Advanced ML Model**: Powered by XGBoost for high-accuracy device identification
- **Interactive Web Interface**: Modern, responsive design with real-time predictions
- **Manual Data Entry**: Easy-to-use form for inputting network traffic features
- **Sample Data Loading**: Load sample data from the training dataset
- **Visual Results**: Interactive charts and confidence scores for predictions
- **Device Categories**: Supports 9 different IoT device types:
  - Baby Monitor
  - Lights
  - Motion Sensor
  - Security Camera
  - Smoke Detector
  - Socket
  - Thermostat
  - TV
  - Watch

## 📊 Dataset Information

- **Total Samples**: 10,000 augmented IoT device traffic patterns
- **Features**: 256 network traffic features including:
  - Packet statistics (bytes, packets, duration)
  - HTTP/HTTPS traffic patterns
  - SSL/TLS characteristics
  - Network protocol analysis
  - Domain and subdomain patterns
- **Device Categories**: 9 different IoT device types
- **Model**: XGBoost classifier trained on the augmented dataset

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for GitHub deployment)

### Local Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/bhushancharpe15/iot-device-identification.git
   cd iot-device-identification
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv iot_env
   source iot_env/bin/activate  # On Windows: iot_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   # or
   python run.py
   ```

5. **Access the web interface**
   Open your browser and navigate to: `http://localhost:5000`

### 🚀 GitHub Deployment

#### Option 1: Deploy to Heroku (Recommended)

1. **Fork this repository** to your GitHub account: https://github.com/bhushancharpe15/iot-device-identification
2. **Create a Heroku account** at [heroku.com](https://heroku.com)
3. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```
4. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```
5. **Deploy to Heroku**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```
6. **Open your deployed app**:
   ```bash
   heroku open
   ```

#### Option 2: Deploy to Railway

1. **Fork this repository** to your GitHub account: https://github.com/bhushancharpe15/iot-device-identification
2. **Go to [Railway.app](https://railway.app)** and sign up
3. **Connect your GitHub account**
4. **Create a new project** and select your forked repository
5. **Railway will automatically deploy** your application

#### Option 3: Deploy to Render

1. **Fork this repository** to your GitHub account: https://github.com/bhushancharpe15/iot-device-identification
2. **Go to [Render.com](https://render.com)** and sign up
3. **Create a new Web Service**
4. **Connect your GitHub repository**
5. **Use these settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. **Deploy** your application

## 🎯 Usage

### Manual Device Identification

1. **Navigate to the Prediction Form**
   - Click "Start Prediction" or scroll to the prediction section
   - Fill in the network traffic features

2. **Key Features to Enter**
   - **Total Bytes**: Total data transferred
   - **Total Packets**: Number of network packets
   - **Duration**: Connection duration in seconds
   - **HTTP Transactions**: Number of HTTP requests
   - **SSL Transactions**: Number of SSL/TLS connections
   - **Bytes A/B**: Directional byte counts
   - **Packets A/B**: Directional packet counts
   - **TTL Average**: Time-to-live average

3. **Load Sample Data**
   - Click "Load Sample Data" to populate the form with real data from the dataset
   - This helps understand the expected input format

4. **Submit and View Results**
   - Click "Identify Device" to get predictions
   - View the predicted device type with confidence scores
   - Analyze the confidence breakdown for all device categories

### Understanding Results

- **Predicted Device**: The most likely device type based on the input features
- **Confidence Score**: Probability percentage for the predicted device
- **Confidence Breakdown**: Detailed confidence scores for all device categories
- **Visual Chart**: Interactive bar chart showing confidence distribution

## 🔧 Technical Details

### Model Architecture
- **Algorithm**: XGBoost (eXtreme Gradient Boosting)
- **Features**: 256 engineered network traffic features
- **Preprocessing**: StandardScaler for feature normalization
- **Output**: Multi-class classification with probability scores

### Web Framework
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome

### File Structure
```
iot-device-identification/
├── app.py                          # Main Flask application
├── best_xgb_model.json            # Trained XGBoost model
├── iot_device_test_augmented_10k.csv  # Training dataset
├── requirements.txt               # Python dependencies
├── README.md                     # This file
├── templates/
│   └── index.html                # Main HTML template
└── static/
    ├── css/
    │   └── style.css             # Custom CSS styles
    └── js/
        └── app.js                # JavaScript functionality
```

## 🎨 Customization

### Adding New Device Categories
1. Update the `device_categories` list in `app.py`
2. Add corresponding icons in `static/js/app.js`
3. Retrain the model with the new categories

### Modifying Features
1. Update the feature list in the HTML form
2. Modify the feature processing in `app.py`
3. Ensure the model is retrained with the new feature set

### Styling Changes
- Modify `static/css/style.css` for visual customizations
- Update Bootstrap classes in `templates/index.html`
- Customize colors, fonts, and layouts as needed

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Error**
   - Ensure `best_xgb_model.json` is in the project root
   - Check file permissions and path

2. **Dependencies Error**
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility

3. **Port Already in Use**
   - Change the port in `app.py`: `app.run(port=5001)`
   - Kill existing processes using port 5000

4. **CSV File Not Found**
   - Ensure `iot_device_test_augmented_10k.csv` is in the project root
   - Check file name spelling

### Performance Optimization

- For production deployment, consider using Gunicorn or uWSGI
- Implement caching for model predictions
- Use a production database for storing results
- Add input validation and error handling

## 📈 Future Enhancements

- **Real-time Monitoring**: Live network traffic analysis
- **Batch Processing**: Upload CSV files for bulk predictions
- **Model Retraining**: Web interface for model updates
- **API Endpoints**: RESTful API for integration
- **User Authentication**: Multi-user support
- **Historical Data**: Prediction history and analytics
- **Export Features**: Download results as PDF/CSV

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For questions, issues, or contributions, please contact the development team or create an issue in the project repository.

---

**Built with ❤️ using Flask, XGBoost, and modern web technologies**
