# RPA + ML Project - Local Setup

## Estrutura de Containers

```
ingestor-1     → busca dados (Open-Meteo) → /data/
               ↓
processor-1    → treina ML + gera gráfico + envia e-mail
               ↓
inference-1    → API de previsão (FastAPI)
               ↓
minio-1        → armazena arquivos
```

## Como rodar localmente

### 1. Subir todos os containers

```bash
cd c:\Users\mateu\Documents\Projetos\Python\RPA
docker-compose up --build
```

### 2. Disparar o pipeline completo (escolha um gatilho)

**Opção A: Rodar ingestor + processor manualmente**

```bash
# Terminal 1: rodar ingestor
docker-compose run --rm ingestor

# Terminal 2 (aguarde o ingestor terminar): rodar processor
docker-compose run --rm processor
```

**Opção B: Usar docker-compose exec (containers já rodando)**

```bash
# Se os containers já estão up -d:
docker-compose exec ingestor python ingest.py
docker-compose exec processor python processor.py
```

### 3. Verificar resultado

- Logs: `docker-compose logs -f ingestor` / `docker-compose logs -f processor`
- Arquivos gerados: pasta `data/` (JSON + PNG)
- MinIO: http://localhost:9000 (minioadmin / minioadmin)
- Inference API: `curl http://localhost:8000/health`

## Configurar e-mail (para processor)

O `processor` pode enviar gráficos por e-mail. Configure as variáveis:

```bash
# No PowerShell (Windows):
$env:SENDER_EMAIL = "seu-email@gmail.com"
$env:SENDER_PASSWORD = "sua-senha-app"  # use App Password do Gmail
$env:RECIPIENT_EMAIL = "destinatario@example.com"

docker-compose up --build
```

Ou edite `.env` local:

```env
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=sua-senha-app
RECIPIENT_EMAIL=destinatario@example.com
```

## Próximos passos

- [ ] Criar workflow Kestra para agendar pipeline
- [ ] Adicionar testes e CI/CD
- [ ] Deploy em Kubernetes
