from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path("/opt/claude/mystocks_spec")


def test_web_compose_references_existing_frontend_dev_dockerfile() -> None:
    compose_text = (REPO_ROOT / "web" / "docker-compose.yml").read_text(encoding="utf-8")

    assert "dockerfile: Dockerfile.dev" in compose_text
    assert "npm run dev:no-types" in compose_text
    assert "image: ${REDIS_IMAGE:-redis:7-alpine}" in compose_text
    assert '${POSTGRES_PUBLISHED_PORT:-5432}:5432' in compose_text
    assert '${REDIS_PUBLISHED_PORT:-6379}:6379' in compose_text
    assert "REDIS_HOST: redis" in compose_text
    assert "PYTHONPATH: /workspace:/app" in compose_text
    assert "- ..:/workspace:ro" in compose_text
    assert "- ../config:/app/config:ro" in compose_text
    assert "- ../src:/app/src:ro" in compose_text
    assert "depends_on:\n      - postgresql\n      - redis" in compose_text
    assert (REPO_ROOT / "web" / "frontend" / "Dockerfile.dev").exists()


def test_production_compose_references_existing_frontend_dockerfile() -> None:
    compose_text = (REPO_ROOT / "docker" / "docker-compose.prod.yml").read_text(encoding="utf-8")

    assert "context: ./web/frontend" in compose_text
    assert "dockerfile: Dockerfile" in compose_text
    assert (REPO_ROOT / "web" / "frontend" / "Dockerfile").exists()


def test_backend_dockerfile_exposes_production_target_for_compose() -> None:
    dockerfile_text = (REPO_ROOT / "web" / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM base AS production" in dockerfile_text
    assert "FROM base AS development" in dockerfile_text
    assert "build-essential" in dockerfile_text
    assert "ta-lib-0.6.4-src.tar.gz" in dockerfile_text
    assert "./configure --prefix=/usr" in dockerfile_text
    assert "make install" in dockerfile_text
    assert "grep -v '^TA-Lib==' requirements.txt" in dockerfile_text
    assert "pip install TA-Lib==0.6.7" in dockerfile_text
    assert 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]' in dockerfile_text


def test_frontend_runtime_container_assets_include_nginx_spa_fallback() -> None:
    nginx_text = (REPO_ROOT / "web" / "frontend" / "config" / "nginx" / "default.conf").read_text(encoding="utf-8")
    dockerfile_text = (REPO_ROOT / "web" / "frontend" / "Dockerfile").read_text(encoding="utf-8")
    dockerfile_dev_text = (REPO_ROOT / "web" / "frontend" / "Dockerfile.dev").read_text(encoding="utf-8")

    assert "FROM node:20-alpine" in dockerfile_text
    assert "FROM node:20-alpine" in dockerfile_dev_text
    assert "try_files $uri $uri/ /index.html;" in nginx_text
    assert "location /healthz" in nginx_text
