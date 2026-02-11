# RPA + ML Project (Complete Scaffold)

Este repositório contém um scaffold completo para um projeto RPA em Python com inferência ML, orquestração com Kestra e CI/CD com GitHub Actions.

Estrutura principal:

- `services/inference/`: FastAPI para inferência de modelo dummy
- `services/rpa/`: runner RPA de exemplo
- `kestra/`: workflows Kestra de exemplo
- `.github/workflows/`: CI/CD
- `docker-compose.yml`: ambiente local com os serviços

Como rodar localmente (exemplo):

```bash
# Build e subir (docker-compose precisa estar instalado)
cd c:/Users/mateu/Documents/Projetos/Python/RPA
docker-compose up --build

# inference: http://localhost:8000/health
# rpa runner escreve logs no terminal
```

Próximos passos: ajustar modelos, adicionar testes e configurar CI/CD com registry e deploy.
