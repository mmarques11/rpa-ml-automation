import os
import json
import time
from datetime import datetime, timedelta
import requests

# Optional MinIO upload
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except Exception:
    boto3 = None

DATA_DIR = os.environ.get("DATA_DIR", "/data")
LAT = os.environ.get("LAT", "52.52")
LON = os.environ.get("LON", "13.41")
DAYS = int(os.environ.get("DAYS", "7"))

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "ingest")

os.makedirs(DATA_DIR, exist_ok=True)


def fetch_open_meteo(lat, lon, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def save_local(payload, prefix="ingest"):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}_{ts}.json"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    print("Saved to", path)
    return path


def upload_minio(path, key=None):
    if not boto3:
        print("boto3 not installed; skipping MinIO upload")
        return False
    if not MINIO_ENDPOINT or not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
        print("MinIO credentials not provided; skipping upload")
        return False
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="us-east-1",
    )
    if not key:
        key = os.path.basename(path)
    try:
        # ensure bucket exists
        try:
            s3.head_bucket(Bucket=MINIO_BUCKET)
        except ClientError:
            s3.create_bucket(Bucket=MINIO_BUCKET)
        s3.upload_file(path, MINIO_BUCKET, key)
        print(f"Uploaded {path} to s3://{MINIO_BUCKET}/{key}")
        return True
    except (BotoCoreError, ClientError) as e:
        print("MinIO upload failed:", e)
        return False


def run_once():
    end = datetime.utcnow().date()
    start = end - timedelta(days=DAYS - 1)
    payload = fetch_open_meteo(LAT, LON, start.isoformat(), end.isoformat())
    path = save_local(payload)
    if MINIO_ENDPOINT:
        upload_minio(path)


if __name__ == "__main__":
    # Simple loop: run once and exit. Scheduling should be handled by Kestra or cron.
    try:
        run_once()
    except Exception as e:
        print("Ingestor failed:", e)
        raise
