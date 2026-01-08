FROM python:3.11-slim

WORKDIR /app

# Install basic requirements
RUN pip install --no-cache-dir fastapi uvicorn httpx

# Copy your files into the container
COPY main.py .
COPY dist/ ./dist/

# Set the environment variable default
ENV DVR_IP=127.0.0.1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
