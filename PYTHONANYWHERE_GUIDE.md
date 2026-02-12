# PythonAnywhere Deployment Guide

This guide will help you deploy your Satellite Imagery Detection Project on PythonAnywhere.

## Why PythonAnywhere?

✅ **Easy Setup**: No complex configuration required  
✅ **Free Tier Available**: Perfect for testing and small projects  
✅ **Web App Support**: Native support for web applications  
✅ **Database Support**: Built-in SQLite and MySQL support  
✅ **Cron Jobs**: Schedule tasks easily  
✅ **No Dependency Issues**: Clean Python environment  

## Prerequisites

1. **PythonAnywhere Account**: Sign up at [pythonanywhere.com](https://www.pythonanywhere.com/)
2. **GitHub Repository**: Your project should be uploaded to GitHub
3. **Basic Python Knowledge**: Understanding of virtual environments and pip

## Step-by-Step Deployment

### Step 1: Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Sign up for a free account (or paid if you need more features)
3. Verify your email address
4. Log in to your dashboard

### Step 2: Upload Your Project

#### Option A: Clone from GitHub (Recommended)

1. In PythonAnywhere, go to **Consoles** → **Bash**
2. Navigate to your home directory:
   ```bash
   cd /home/aditya2909rb
   ```
3. Clone your repository:
   ```bash
   git clone https://github.com/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-.git
   ```
4. Navigate to your project:
   ```bash
   cd Satellite-Imagery-for-Global-Change-Remote-Sensing-
   ```

#### Option B: Upload Files Manually

1. Go to **Files** → **Upload file**
2. Upload your project files one by one or as a ZIP
3. Extract if uploaded as ZIP

### Step 3: Set Up Virtual Environment

1. In the Bash console, create a virtual environment:
   ```bash
   cd /home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-
   python3 -m venv venv
   ```
2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Install dependencies using our lightweight setup script (recommended for free accounts):
   ```bash
   python setup_lightweight.py
   ```
   
   **OR** use the full setup script (may exceed disk quota on free accounts):
   ```bash
   python setup_pythonanywhere.py
   ```

### Step 4: Configure Web App

1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Flask** (we'll modify it for FastAPI)
4. Select Python version (3.10 or 3.11 recommended)
5. When asked for a location, use: `/home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-`

### Step 5: Configure WSGI File

1. In the **Web** tab, find your app and click **WSGI configuration file**
2. Replace the content with the path to our WSGI file:
   ```
   /home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-/pythonanywhere_wsgi.py
   ```
3. Save the file

**Note**: The WSGI file will automatically try to use `app_simple.py` first (which has simpler imports), and fall back to `app.py` if needed.

### Step 6: Set Virtual Environment

1. In the **Web** tab, find **Virtualenv**
2. Set the path to your virtual environment:
   ```
   /home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-/venv
   ```

### Step 7: Configure Static Files

1. In the **Web** tab, add static file mappings:
   - URL: `/static/`
   - Path: `/home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-/static/`

### Step 8: Restart and Test

1. Click **Reload** in the **Web** tab
2. Visit your app URL (usually `username.pythonanywhere.com`)
3. Your application should now be running!

## Alternative: Manual WSGI Configuration

If the automatic setup doesn't work, you can manually configure the WSGI file:

1. Edit the WSGI file in **Web** → **Edit WSGI file**
2. Replace with this content:

```python
import sys
import os

# Add your project directory to the Python path
project_home = '/home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'Satellite-Imagery-for-Global-Change-Remote-Sensing-.settings'

# Import your FastAPI app
from app import app

# Use Mangum to convert FastAPI to WSGI
from mangum import Mangum
application = Mangum(app)
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install missing packages
pip install package_name
```

#### 2. Permission Errors
```bash
# Solution: Check file permissions
chmod 755 your_script.py
```

#### 3. Database Issues
```bash
# Solution: Create database directory
mkdir data
touch data/fire_history.db
```

#### 4. Static Files Not Loading
- Check static file mapping in **Web** tab
- Ensure static files exist in the correct directory

#### 5. Application Won't Start
- Check error logs in **Web** tab
- Verify all dependencies are installed
- Test locally first with `python test_app_import.py`

### Debugging Steps

1. **Check Logs**: Go to **Web** → **Error log** and **Access log**
2. **Test Locally**: Run `python test_app_import.py` in Bash console
3. **Check Dependencies**: Run `pip list` to see installed packages
4. **Verify Paths**: Ensure all file paths are correct

## Performance Optimization

### Free Account Limitations
- **CPU**: Limited processing time
- **Memory**: 1GB RAM limit
- **Storage**: 100MB for free accounts

### Optimization Tips

1. **Use Efficient Libraries**: Pillow for image processing
2. **Cache Results**: Store processed images
3. **Limit Concurrent Requests**: Use rate limiting
4. **Optimize Database**: Use indexes for SQLite

## Advanced Features

### Scheduled Tasks (Cron Jobs)

1. Go to **Tasks** tab
2. Add scheduled task for data updates:
   ```bash
   0 2 * * * /home/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-/venv/bin/python update_data.py
   ```

### Email Notifications

Configure email alerts in your application settings for fire detection notifications.

### Database Backups

Set up automatic database backups using PythonAnywhere's built-in features.

## Monitoring and Maintenance

### Regular Tasks

1. **Monitor Logs**: Check error logs weekly
2. **Update Dependencies**: Keep packages updated
3. **Backup Data**: Regular database backups
4. **Performance Check**: Monitor response times

### Scaling Up

When your app grows:

1. **Upgrade Account**: Move to paid plans for more resources
2. **Optimize Code**: Review performance bottlenecks
3. **Use CDN**: For static file delivery
4. **Database Upgrade**: Consider MySQL for larger datasets

## Support and Resources

### PythonAnywhere Documentation
- [Official Docs](https://help.pythonanywhere.com/)
- [Web App Setup](https://help.pythonanywhere.com/pages/Flask/)
- [Troubleshooting](https://help.pythonanywhere.com/pages/DebuggingImportError/)

### FastAPI on PythonAnywhere
- [Mangum Documentation](https://mangum.io/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Project-Specific Help
- Check `README.md` for project details
- Review `requirements.txt` for dependencies
- Use `test_app_import.py` for testing

## Next Steps

1. **Test Thoroughly**: Ensure all features work
2. **Monitor Performance**: Watch for any issues
3. **Gather Feedback**: Get user feedback
4. **Iterate and Improve**: Make enhancements based on usage

🎉 **Congratulations!** Your satellite imagery detection project is now live on PythonAnywhere!