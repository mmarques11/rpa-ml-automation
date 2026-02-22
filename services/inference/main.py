from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Inference Service")


class PredictRequest(BaseModel):
    text: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(req: PredictRequest):
    # Modelo dummy: responde com comprimento e uma label simples
    text = req.text or ""
    score = len(text) / 100.0
    label = "positive" if score > 0.3 else "negative"
    return {"label": label, "score": score}
