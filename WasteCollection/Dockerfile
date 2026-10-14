# Use official lightweight Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables for clean container output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set container working directory
WORKDIR /app

# Copy dependency definition and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets
COPY . .

# Ensure data directory exists inside container for SQLite volume mounting
RUN mkdir -p /app/data

# Expose Flask application port
EXPOSE 5000

# Run the Flask application on 0.0.0.0:5000
CMD ["python", "app.py"]
