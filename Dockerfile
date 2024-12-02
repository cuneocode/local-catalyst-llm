FROM python:3.9-slim

# Install curl for Ollama installation
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY device_state_analyzer.py .

# Expose Ollama port
EXPOSE 11434

# Create startup script
COPY <<EOF /app/start.sh
#!/bin/bash
# Wait for Ollama to be ready
sleep 5
# Run the Python script
python device_state_analyzer.py
EOF

RUN ollama serve
RUN ollama pull llama3.2
RUN chmod +x /app/start.sh

# Set the entry point
ENTRYPOINT ["/app/start.sh"]