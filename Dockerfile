FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/ ./apps/
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Expose Gradio default port
EXPOSE 7860

# Start command
CMD ["bash", "start.sh"]
