FROM python:3.12-slim

WORKDIR /app/OpenManus

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    # hadolint ignore=DL3013
    && (command -v uv >/dev/null 2>&1 || pip install --no-cache-dir "uv>=0.4.0,<1.0")

COPY . .

RUN uv pip install --system -r requirements.txt

CMD ["bash"]
