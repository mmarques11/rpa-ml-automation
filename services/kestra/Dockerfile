FROM kestra/kestra:latest

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io docker-compose curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir "requests<2.32" "urllib3<2"

RUN mkdir -p /usr/local/lib/docker/cli-plugins \
    && curl -SL "https://github.com/docker/compose/releases/download/v2.33.1/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose \
    && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose