# RPA + ML Project

Projeto de automação RPA integrado com pipeline de ML, padronizado com práticas de engenharia de software:

- serviços desacoplados em Docker
- testes automatizados locais e em container
- CI/CD com GitHub Actions
- orquestração de pipeline com Kestra

## Arquitetura

- `services/inference/`: API FastAPI com endpoints de saúde e inferência
- `services/ingestor/`: coleta de dados externos (Open-Meteo) e persistência local/MinIO
- `services/processor/`: etapa ML (treino, predição, gráfico e envio opcional de e-mail)
- `services/rpa/`: runner RPA de integração com a API de inferência
- `kestra/workflows/`: orquestração do fluxo ponta a ponta
- `.github/workflows/`: pipeline CI/CD

Fluxo principal:

1. `ingestor` coleta e salva dados em `data/`
2. `processor` treina modelo e gera artefatos
3. `rpa-runner` consome inferência para automação
4. Kestra coordena a sequência e observabilidade

## Como executar localmente

```bash
cd c:/Users/mateu/Documents/Projetos/Python/RPA
docker compose up --build -d inference minio
```

Executar o pipeline manual:

```bash
docker compose run --rm ingestor
docker compose run --rm processor
docker compose run --rm rpa-runner
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

## Orquestração com Kestra

Subir Kestra:

```bash
docker compose up -d kestra
```

Interface web:

- `http://localhost:8080`

Workflow:

- `kestra/workflows/rpa_workflow.yml`
- sequência: health-check → ingestor → processor → rpa-runner

## CI/CD

O workflow de CI em `.github/workflows/ci.yml` executa:

1. instalação de dependências
2. validação de formatação (`black`, `isort`)
3. testes unitários (`pytest`)
4. build das imagens Docker
5. testes em container (`docker compose run --rm tests`)

## Qualidade de Código

- formatação: `black`
- organização de imports: `isort`
- ganchos locais: `pre-commit`

Instalação sugerida:

```bash
pip install pre-commit
pre-commit install
```
