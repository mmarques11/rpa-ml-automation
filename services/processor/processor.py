import glob
import json
import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib.pyplot as plt
import numpy as np
import requests
from sklearn.linear_model import LinearRegression

DATA_DIR = os.environ.get("DATA_DIR", "/data")
INFERENCE_URL = os.environ.get("INFERENCE_URL", "http://inference:8000/predict")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp-mail.outlook.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")


def load_ingested_data(pattern="ingest_*.json"):
    """Load latest ingested JSON files."""
    files = sorted(glob.glob(os.path.join(DATA_DIR, pattern)), reverse=True)
    if not files:
        raise FileNotFoundError(f"No files matching {pattern} in {DATA_DIR}")
    latest = files[0]
    print(f"Loading {latest}")
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_data(payload):
    """Extract daily data and prepare for ML."""
    daily = payload.get("daily", {})
    dates = daily.get("time", [])
    temps_max = daily.get("temperature_2m_max", [])
    temps_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])

    if not dates or not temps_max:
        raise ValueError("Insufficient data in payload")

    X = np.arange(len(dates)).reshape(-1, 1)  # day index
    y = np.array(temps_max)
    return X, y, dates, temps_min, precip


def train_model(X, y):
    """Train simple linear regression."""
    model = LinearRegression()
    model.fit(X, y)
    return model


def generate_graph(dates, y_actual, y_pred, temps_min, output_path):
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.style.use("seaborn-v0_8")
    x_idx = np.arange(len(dates))

    ax.plot(
        x_idx,
        y_actual,
        "o-",
        label="Temperatura Máxima (Real)",
        linewidth=2.5,
        markersize=6,
        color="#1f77b4",
    )
    ax.plot(
        x_idx,
        y_pred,
        "s--",
        label="Temperatura Máxima (Prevista)",
        linewidth=2.5,
        markersize=6,
        color="#ff7f0e",
    )
    ax.fill_between(
        x_idx, temps_min, y_actual, alpha=0.25, label="Faixa Min–Máx", color="#2ca02c"
    )

    ax.set_xlabel("Data")
    ax.set_ylabel("Temperatura (°C)")
    ax.set_title("Previsão do Tempo: Real vs Previsto")
    ax.set_xticks(x_idx)
    ax.set_xticklabels(dates, rotation=30, ha="right")
    ax.grid(True, alpha=0.25, linestyle=":")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_path, dpi=120, bbox_inches="tight")
    print(f"Graph saved to {output_path}")
    plt.close()


def send_email(subject, body, attachment_path):
    """Send email with attachment."""
    if not SENDER_EMAIL or not RECIPIENT_EMAIL or not SENDER_PASSWORD:
        print("Email credentials not configured; skipping send")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )
                msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False


def call_inference(text):
    """Call inference endpoint."""
    try:
        r = requests.post(INFERENCE_URL, json={"text": text}, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"Inference returned {r.status_code}")
            return None
    except Exception as e:
        print(f"Inference call failed: {e}")
        return None


def run_pipeline():
    """Main pipeline: ingest -> train -> predict -> graph -> email."""
    print("Starting processor pipeline...")

    # Load data
    payload = load_ingested_data()
    X, y, dates, temps_min, precip = prepare_data(payload)
    print(f"Loaded {len(dates)} days of data")

    # Train model
    model = train_model(X, y)
    print(
        f"Model trained (slope={model.coef_[0]:.3f}, intercept={model.intercept_:.3f})"
    )

    # Predict
    y_pred = model.predict(X)
    rmse = np.sqrt(np.mean((y - y_pred) ** 2))
    print(f"RMSE: {rmse:.3f}")

    # Call inference service for text-based prediction
    inference_summary = call_inference(
        f"Temperature trend: max={y.max():.1f}C, min={y.min():.1f}C, avg={y.mean():.1f}C"
    )
    print(f"Inference result: {inference_summary}")

    # Generate graph
    graph_path = os.path.join(
        DATA_DIR, f"forecast_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.png"
    )
    generate_graph(dates, y, y_pred, temps_min, graph_path)

    # Send email
    subject = (
        f"Relatório de Previsão do Tempo - {datetime.utcnow().strftime('%Y-%m-%d')}"
    )
    body = f"""
Relatório de Previsão do Tempo

Detalhes da previsão:
- Dias analisados: {len(dates)}
- Temperatura máxima: {y.max():.2f}°C
- Temperatura mínima: {y.min():.2f}°C
- Temperatura média: {y.mean():.2f}°C
- RMSE do modelo: {rmse:.3f}°C
- Resultado de inferência: {inference_summary}

O gráfico está anexado.
    """.strip()

    send_email(subject, body, graph_path)
    print("Pipeline complete!")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise
