#!/bin/bash
set -e

echo "Starting Gradio Frontend..."
echo "API Backend: ${API_BASE_URL:-http://localhost:8000}"
echo "Port: ${PORT:-7860}"

# Start Gradio
python -m apps.ui.app
