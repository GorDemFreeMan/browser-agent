FROM python:3.11-slim

WORKDIR /app

# Install Playwright and dependencies
RUN pip install --no-cache-dir playwright==1.42.0 && \
    playwright install chromium && \
    playwright install firefox && \
    playwright install-deps chromium

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
