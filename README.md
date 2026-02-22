# RPA + ML Project

Projeto de automacao RPA integrado com pipeline de ML, com servicos desacoplados em Docker e orquestracao via Kestra.

## Arquitetura

- `services/inference/`: API FastAPI com endpoints de saude e inferencia
- `services/ingestor/`: coleta de dados (Open-Meteo) e persistencia local/MinIO
- `services/processor/`: ML (treino, predicao, grafico e envio opcional de e-mail)
- `services/rpa/`: runner RPA integrando com a API de inferencia
- `kestra/workflows/`: orquestracao do fluxo ponta a ponta
- `.github/workflows/`: pipeline CI/CD

Fluxo principal:

1. `ingestor` coleta e salva dados em `data/`
2. `processor` treina modelo e gera artefatos
3. `rpa-runner` consome inferencia para automacao
4. Kestra coordena a sequencia e observabilidade

## Requisitos

- Docker Desktop (com Compose v2)
- Python 3.10+ (opcional, apenas para testes locais)

## Como executar localmente

Subir servicos base:

```bash
docker compose up --build -d inference minio
```

Executar o pipeline manualmente:

```bash
docker compose run --rm --no-deps ingestor
docker compose run --rm --no-deps processor
docker compose run --rm --no-deps rpa-runner
```

## Testes

Executar testes no host:

```bash
pytest -q
```

Executar testes em Docker:

```bash
docker compose run --rm tests
```

## Orquestracao com Kestra

Subir Kestra:

```bash
docker compose up -d kestra
```

Interface web:

- `http://localhost:8080`

Workflow:

- `kestra/workflows/rpa_workflow.yml`
- sequencia: health-check → ingestor → processor → rpa-runner

## Variaveis de ambiente

Crie um arquivo `.env` local para envio de email:

```env
SENDER_EMAIL=seu-email@gmail.com
SENDER_PASSWORD=sua-senha-app
RECIPIENT_EMAIL=destinatario@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

Notas:

- O MinIO usa credenciais default por desenvolvimento. Troque para uso publico/prod.
- A senha do Kestra esta em texto puro no compose; altere antes de abrir o repo ao publico.

## CI/CD

O workflow de CI em `.github/workflows/ci.yml` executa:

1. instalacao de dependencias
2. validacao de formatacao (`black`, `isort`)
3. testes unitarios (`pytest`)
4. build das imagens Docker
5. testes em container (`docker compose run --rm tests`)

## Qualidade de Codigo

- formatacao: `black`
- organizacao de imports: `isort`
- ganchos locais: `pre-commit`

Instalacao sugerida:

```bash
pip install pre-commit
pre-commit install
```
