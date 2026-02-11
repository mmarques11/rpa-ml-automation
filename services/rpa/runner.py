import requests
import time

INFERENCE_URL = 'http://inference:8000/predict'


def run_job(text: str):
    print(f"Starting RPA job for text: {text}")
    try:
        resp = requests.post(INFERENCE_URL, json={"text": text}, timeout=10)
        print("Inference response:", resp.json())
    except Exception as e:
        print("Inference call failed:", e)


if __name__ == '__main__':
    # Exemplo simples: roda periodicamente
    samples = [
        'Olá mundo',
        'Este é um texto de teste para avaliar o scorer do modelo dummy',
        'Curto'
    ]
    for t in samples:
        run_job(t)
        time.sleep(2)
