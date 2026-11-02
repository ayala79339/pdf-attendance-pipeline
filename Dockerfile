FROM python:3.11-slim

# Install system dependencies (Tesseract OCR, Hebrew language data, Poppler for pdf2image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-heb \
    poppler-utils \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command runs the main pipeline
ENTRYPOINT ["python", "main.py"]