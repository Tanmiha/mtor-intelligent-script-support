FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face port
EXPOSE 7860

# Run the FastAPI app instead of Streamlit
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]