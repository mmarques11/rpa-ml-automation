# RPA + ML Project - Local Setup

## Estrutura de Containers

```
ingestor        → busca dados (Open-Meteo) e salva em /data/
                ↓
processor       → treina ML + gera gráfico + chama inferência
                ↓
rpa-runner      → executa automação RPA consumindo inferência

inference       → API de previsão (FastAPI)
minio           → armazenamento de objetos
kestra          → orquestra pipeline ponta a ponta
```

## Como rodar localmente

### 1. Subir todos os containers

```bash
cd c:\Users\mateu\Documents\Projetos\Python\RPA
docker compose up --build
```

### 2. Disparar o pipeline completo (escolha um gatilho)

**Opção A: Rodar ingestor + processor manualmente**

```bash
# Terminal 1: rodar ingestor
docker compose run --rm ingestor

# Terminal 2 (aguarde o ingestor terminar): rodar processor
docker compose run --rm processor

# Terminal 3: rodar RPA runner
docker compose run --rm rpa-runner
```

**Opção B: Usar docker compose exec (containers já rodando)**

```bash
# Se os containers já estão up -d:
docker compose exec ingestor python ingest.py
docker compose exec processor python processor.py
```

### 3. Verificar resultado

- Logs: `docker compose logs -f ingestor` / `docker compose logs -f processor`
- Arquivos gerados: pasta `data/` (JSON + PNG)
- MinIO: http://localhost:9000 (minioadmin / minioadmin)
- Inference API: `curl http://localhost:8000/health`

## Rodar testes

```bash
# Host
pytest -q

# Docker (recomendado para paridade com CI)
docker compose run --rm tests
```

## Rodar orquestração com Kestra

```bash
docker compose up -d kestra
```

- Acesse: http://localhost:8080
- Workflow: `kestra/workflows/rpa_workflow.yml`
- Etapas: health-check da inferência → ingestão → processamento ML → runner RPA

## Configurar e-mail (para processor)

O `processor` pode enviar gráficos por e-mail. Configure as variáveis:

```bash
# No PowerShell (Windows):
$env:SENDER_EMAIL = "seu-email@gmail.com"
$env:SENDER_PASSWORD = "sua-senha-app"  # use App Password do Gmail
$env:RECIPIENT_EMAIL = "destinatario@example.com"

docker compose up --build
```

Ou edite `.env` local:

```env
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=sua-senha-app
RECIPIENT_EMAIL=destinatario@example.com
```

## Próximos passos

- [ ] Agendar execução recorrente no Kestra (cron)
- [ ] Publicar imagens em registry para deploy automático
- [ ] Adicionar testes de integração do pipeline completo
