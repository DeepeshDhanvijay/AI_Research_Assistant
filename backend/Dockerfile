FROM python:3.12-slim

WORKDIR /app

# Copy only requirements first — this is a deliberate layer-caching optimization,
# explained below
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Create data directories the app expects (mirrors what config.py does locally)
RUN mkdir -p data/papers data/vector_store

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]