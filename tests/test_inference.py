from fastapi.testclient import TestClient
from services.inference.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_predict():
    r = client.post('/predict', json={"text": "teste rapido"})
    assert r.status_code == 200
    data = r.json()
    assert 'label' in data and 'score' in data
