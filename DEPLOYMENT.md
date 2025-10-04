# 🚀 Deployment Guide - IoT Device Identification System

This guide will help you deploy your IoT Device Identification System to various cloud platforms.

## 📋 Prerequisites

- GitHub account
- Python 3.8+ knowledge
- Basic command line skills

## 🌐 Deployment Options

### Option 1: Heroku (Recommended) ⭐

**Why Heroku?**
- Easy setup and deployment
- Free tier available
- Automatic deployments from GitHub
- Built-in monitoring

**Steps:**

1. **Prepare your repository:**
   ```bash
   # Run the setup script
   ./setup_github.sh
   
   # Push to GitHub
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Heroku account:**
   - Go to [heroku.com](https://heroku.com)
   - Sign up for a free account

3. **Install Heroku CLI:**
   ```bash
   # On Ubuntu/Debian
   curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
   
   # On macOS
   brew install heroku/brew/heroku
   
   # On Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

4. **Login and create app:**
   ```bash
   heroku login
   heroku create your-iot-app-name
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   heroku open
   ```

**Heroku Configuration:**
- The `Procfile` is already configured
- `runtime.txt` specifies Python 3.8
- `requirements.txt` includes all dependencies

---

### Option 2: Railway 🚄

**Why Railway?**
- Modern platform
- Easy GitHub integration
- Good free tier
- Automatic HTTPS

**Steps:**

1. **Push to GitHub:**
   ```bash
   ./setup_github.sh
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project"
   - Select your repository
   - Railway auto-detects Python and deploys

3. **Configure (if needed):**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

---

### Option 3: Render 🌟

**Why Render?**
- Free tier with good limits
- Easy setup
- Good performance
- Automatic deployments

**Steps:**

1. **Push to GitHub:**
   ```bash
   ./setup_github.sh
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New Web Service"
   - Connect your repository

3. **Configure:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Python Version:** 3.8

---

### Option 4: PythonAnywhere 🐍

**Why PythonAnywhere?**
- Python-focused platform
- Free tier available
- Easy file management
- Good for learning

**Steps:**

1. **Create account:**
   - Go to [pythonanywhere.com](https://pythonanywhere.com)
   - Sign up for free account

2. **Upload files:**
   - Use the file manager to upload all project files
   - Or use Git: `git clone https://github.com/YOUR_USERNAME/iot-device-identification.git`

3. **Configure web app:**
   - Go to "Web" tab
   - Create new web app
   - Choose "Flask"
   - Set source code directory
   - Set WSGI file to `app.py`

---

## 🔧 Configuration Files

Your project includes these deployment-ready files:

- **`Procfile`**: Tells Heroku how to run your app
- **`runtime.txt`**: Specifies Python version
- **`requirements.txt`**: Lists all dependencies
- **`.gitignore`**: Excludes unnecessary files from Git
- **`.github/workflows/deploy.yml`**: GitHub Actions for CI/CD

## 🐛 Troubleshooting

### Common Issues:

1. **Build fails:**
   - Check Python version compatibility
   - Ensure all dependencies are in `requirements.txt`
   - Check for missing files

2. **App crashes:**
   - Check logs: `heroku logs --tail`
   - Verify model files are included
   - Check file paths

3. **Static files not loading:**
   - Ensure `static/` folder is in repository
   - Check Flask static file configuration

### Getting Help:

- Check platform-specific documentation
- Review application logs
- Test locally first: `python app.py`

## 📊 Monitoring

After deployment, monitor your app:

- **Heroku**: `heroku logs --tail`
- **Railway**: Dashboard shows logs
- **Render**: Logs tab in dashboard
- **PythonAnywhere**: Error logs in web app settings

## 🎉 Success!

Once deployed, your IoT Device Identification System will be live and accessible worldwide!

**Share your deployed app:**
- Add the URL to your README
- Share on social media
- Add to your portfolio

---

**Need help?** Check the main README.md or create an issue in your GitHub repository.

