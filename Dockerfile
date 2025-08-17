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

# Copy the entire reddit-llm application
COPY reddit-llm/ ./reddit-llm/

# Create startup script that runs both backend and frontend
RUN echo '#!/bin/bash\n\
# Start FastAPI backend in background\n\
cd /app/reddit-llm && python -m app.main &\n\
\n\
# Wait for backend to start\n\
sleep 5\n\
\n\
# Start Streamlit frontend\n\
cd /app/reddit-llm && streamlit run ui.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose Streamlit port
EXPOSE 8501

# Health check for Streamlit
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Start both services
ENTRYPOINT ["/app/start.sh"]