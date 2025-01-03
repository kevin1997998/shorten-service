# Use a base image for Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Redis server
RUN apt-get update && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Configure Redis to run in the background
RUN sed -i 's/^daemonize no/daemonize yes/' /etc/redis/redis.conf

# Expose application and Redis ports
EXPOSE 8000 6379

# Define environment variables
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV POSTGRES_URL=postgresql+asyncpg://user:password@db/shortener

# Command to start Redis and your app
CMD redis-server /etc/redis/redis.conf && uvicorn main:app --host 0.0.0.0 --port 8000
