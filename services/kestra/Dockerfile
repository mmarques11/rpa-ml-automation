FROM kestra/kestra:latest

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io docker-compose curl \
    && rm -rf /var/lib/apt/lists/*