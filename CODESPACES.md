# Running Satellite Imagery Detection Project in GitHub Codespaces

This guide will help you run the Satellite Imagery Detection Project in GitHub Codespaces.

## What is GitHub Codespaces?

GitHub Codespaces provides a complete cloud-based development environment that runs directly in your browser. You can develop, build, and test your application without needing to set up a local development environment.

## How to Use Codespaces with This Project

### Option 1: Using the "Code" Button (Recommended)

1. Go to your repository: https://github.com/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-.git
2. Click the green **Code** button
3. Select **Open with Codespaces**
4. Click **New codespace** (or select an existing one)
5. Wait for the environment to be created (this may take 2-5 minutes)

### Option 2: Direct Link

You can also use this direct link to create a codespace:
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/aditya2909rb/Satellite-Imagery-for-Global-Change-Remote-Sensing-.git)

## What Happens When You Open a Codespace

When you open a codespace, the following will happen automatically:

1. **Environment Setup**: A cloud-based development environment will be created
2. **Dependencies Installation**: All required Python packages will be installed automatically
3. **VS Code Interface**: You'll get a full VS Code interface in your browser
4. **Port Forwarding**: Port 5000 will be automatically forwarded for the web application

## Running the Application

Once your codespace is ready:

### Method 1: Using the Terminal (Recommended)

1. Open the terminal in VS Code (Ctrl + `)
2. Run the application:
   ```bash
   python app.py
   ```
3. The application will start on port 5000
4. Click the **"Open in Browser"** button that appears in the terminal or notification area

### Method 2: Using Batch Files

You can also use the provided batch files:

```bash
# Start the server
./run_server.bat

# Or run examples
./run_examples.bat

# Or validate the setup
./run_validation.bat
```

### Method 3: Using the VS Code Run Button

1. Open `app.py` in VS Code
2. Click the **Run** button in the top-right corner
3. The application will start automatically

## Application Features

Once running, the application provides:

- **Satellite Imagery Processing**: Upload and analyze satellite images
- **Fire Detection**: Detect and analyze fire patterns in satellite imagery
- **Data Visualization**: Interactive maps and charts
- **API Endpoints**: RESTful API for programmatic access

## Accessing the Web Interface

After starting the application:

1. Look for a notification in VS Code saying "A service is available on port 5000"
2. Click **"Open in Browser"** or **"Make Public"**
3. The web interface will open in a new browser tab
4. You can now interact with the satellite imagery detection application

## File Structure in Codespaces

The project structure in your codespace:

```
Satellite-Imagery-for-Global-Change-Remote-Sensing-/
├── app.py                    # Main application file
├── start_server.py          # Server startup script
├── requirements.txt         # Python dependencies
├── src/                     # Source code
│   ├── api/                 # API modules
│   ├── models/              # Machine learning models
│   ├── utils/               # Utility functions
│   └── visualization/       # Visualization tools
├── static/                  # Web interface files
├── data/                    # Sample data
└── .devcontainer/           # Codespaces configuration
```

## Troubleshooting

### Application Won't Start

If the application doesn't start:

1. Check the terminal for error messages
2. Ensure all dependencies are installed:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. If pip is not found, try:
   ```bash
   python -m pip install fastapi uvicorn aiohttp pillow opencv-python numpy psutil beautifulsoup4 requests
   ```
4. Check if port 5000 is available:
   ```bash
   lsof -i :5000
   ```

### Port Not Forwarding

If you can't access the web interface:

1. Check the VS Code notification area for port forwarding messages
2. Manually forward the port in the VS Code terminal
3. Try refreshing the browser page

### Missing Dependencies

If you get import errors:

1. Reinstall dependencies:
   ```bash
   pip install --upgrade -r requirements.txt
   ```
2. Check Python version:
   ```bash
   python --version
   ```

## Development in Codespaces

You can develop and modify the application directly in Codespaces:

1. **Edit Files**: Use the full VS Code editor
2. **Run Tests**: Execute test files to verify changes
3. **Debug**: Use VS Code's debugging tools
4. **Commit Changes**: Use Git commands to commit and push changes

## Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [VS Code in the Browser](https://code.visualstudio.com/docs/editor/vscode-web)
- [Python Development in Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-devcontainer.json-file)

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the project's [README.md](./README.md) for additional setup instructions
3. Create an issue in the repository if problems persist