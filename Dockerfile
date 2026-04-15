FROM python:3.11-slim

WORKDIR /app

# Install all necessary system dependencies manually
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libatspi2.0-0 \
    libxfixes3 \
    libpango-1.0-0 \
    libcairo2 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxcursor1 \
    libxi6 \
    libxrender1 \
    libglib2.0-0 \
    libexpat1 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libfreetype6 \
    libfontconfig1 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and browsers
RUN pip install --no-cache-dir playwright==1.42.0 && \
    playwright install chromium && \
    playwright install firefox

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
