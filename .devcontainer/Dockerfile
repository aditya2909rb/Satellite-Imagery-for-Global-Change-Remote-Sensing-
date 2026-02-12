# Use the official Python runtime as the base image
FROM mcr.microsoft.com/devcontainers/python:3.11

# Set the working directory in the container
WORKDIR /workspaces/Satellite-Imagery-for-Global-Change-Remote-Sensing-

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Install additional system dependencies if needed
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set the default command to run when the container starts
CMD ["python", "app.py"]