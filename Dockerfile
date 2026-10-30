# Production Cloud Container for Autonomous AI Viral Reels & YouTube Shorts Engine
FROM python:3.11-slim

# Install system dependencies including FFmpeg for video compositing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-liberation \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ ./backend/
COPY .env.example .env

# Expose FastAPI port
EXPOSE 8000

# Start production server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
