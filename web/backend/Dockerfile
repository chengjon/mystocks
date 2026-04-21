FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    tar \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/ta-lib/ta-lib/releases/download/v0.6.4/ta-lib-0.6.4-src.tar.gz -O /tmp/ta-lib.tar.gz \
    && mkdir -p /tmp/ta-lib-src \
    && tar -xzf /tmp/ta-lib.tar.gz -C /tmp/ta-lib-src --strip-components=1 \
    && cd /tmp/ta-lib-src \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && rm -rf /tmp/ta-lib-src /tmp/ta-lib.tar.gz

COPY requirements.txt .
RUN pip install --upgrade pip \
    && grep -v '^TA-Lib==' requirements.txt > /tmp/requirements.docker.txt \
    && pip install -r /tmp/requirements.docker.txt \
    && pip install TA-Lib==0.6.7 \
    && rm -f /tmp/requirements.docker.txt

COPY . .

RUN mkdir -p logs


FROM base AS development

EXPOSE 8020

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]


FROM base AS production

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
