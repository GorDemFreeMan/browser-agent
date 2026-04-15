# Use Playwright official base image (Ubuntu Jammy - has all browser deps)
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Install all system deps explicitly
RUN apt-get update && apt-get install -y \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxfixes3 \
    libpango-1.0-0 \
    libcairo2 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxrandr2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/* \
    && playwright install-deps

# Install browsers
RUN playwright install chromium firefox

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
