FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies  
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy the application files
COPY app/ ./app/
COPY app.py ./

# Expose port 7860 for Hugging Face Spaces
EXPOSE 7860

# Health check for Gradio
HEALTHCHECK CMD curl --fail http://localhost:7860/ || exit 1

# Start the application
CMD ["python", "app.py"]