# Dockerfile — OpenBrain Agent Team
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    rsync \
    docker-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
# We use volumes in compose for development, but copy for the base image
COPY . .

# Expose the application port
EXPOSE 8769

# Run the webhook server
CMD ["python", "execution/telegram_webhook.py"]
