FROM ghcr.io/prefix-dev/pixi:latest AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pixi.toml pixi.lock* ./
RUN pixi install --locked || pixi install
RUN pixi shell-hook -e default > /shell-hook && echo 'exec "$@"' >> /shell-hook

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=build /app/.pixi /app/.pixi
COPY --from=build /shell-hook /shell-hook
COPY app/ ./app/
COPY pixi.toml ./

ENV PATH="/app/.pixi/envs/default/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/shell-hook"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
