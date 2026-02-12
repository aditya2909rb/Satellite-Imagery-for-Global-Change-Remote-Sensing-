# Use the official Python dev container base image
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install additional system dependencies for data science and image processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*