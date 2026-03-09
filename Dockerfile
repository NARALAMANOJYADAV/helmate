# Use a slim Python 3.10 image to keep the container size small
FROM python:3.10-slim

# Set environment variables for stable and predictable Python execution
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5001
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=10

# Install lightweight system dependencies for OpenCV and AI libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Upgrade pip and configure to handle slow networks gracefully
RUN pip install --no-cache-dir --upgrade pip

# CRITICAL FIX FOR PIP TIMEOUT: Install the CPU-only version of PyTorch FIRST.
# The default PyTorch version downloaded by YOLO is a massive ~1GB GPU version which causes timeouts. 
# This specific CPU version is much smaller, downloads fast, and is exactly what this container needs.
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --default-timeout=1000

# Copy the requirements file first to maximize Docker layer caching
COPY requirements.txt .

# Install remaining dependencies. 
# Pip will automatically skip PyTorch because we installed the CPU version above!
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=1000

# Copy the full application code into the container
COPY . .

# Create persistence directories explicitly to ensure host volume mounts don't throw permission errors
RUN mkdir -p /app/database /app/uploads/captured_images

# Open the port that the application runs on
EXPOSE 5001

# Execute the main application server
CMD ["python", "main.py"]
