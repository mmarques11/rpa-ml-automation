FROM python:3.11-slim
WORKDIR /app
COPY services/ingestor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/ingestor /app
VOLUME ["/data"]
CMD ["python", "ingest.py"]
