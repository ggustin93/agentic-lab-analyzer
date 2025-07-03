# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the environment variable to ensure `apt-get` runs non-interactively
ENV DEBIAN_FRONTEND=noninteractive

# Install system-level dependencies required for the application.
# --no-install-recommends prevents installation of optional packages, reducing image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libmagic-dev \
    # Clean up the apt-get cache to reduce layer size
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching.
# This layer only gets rebuilt if requirements.txt changes.
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir disables the pip cache, resulting in a smaller image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create directories needed by the application at runtime
RUN mkdir -p uploads data/documents logs

# Add the application directory to the Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Set up a health check to ensure the container is running properly before accepting traffic
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Define the command to run the application using uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]