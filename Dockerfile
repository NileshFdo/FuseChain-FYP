# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if needed for pandas/numpy/gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
# We need backend code, models, and data pipeline results
COPY backend/ backend/
COPY models/ models/
COPY ml_pipeline/ ml_pipeline/

# Set PYTHONPATH so 'app' module can be found
ENV PYTHONPATH=/app/backend

# Expose the port (Hugging Face Spaces uses 7860 by default)
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]