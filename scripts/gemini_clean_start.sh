#!/usr/bin/env bash
set -euo pipefail

# Always run from project root so project-level .gemini/.env and settings.json apply.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Remove process-level overrides that take precedence over project settings.
exec env \
  -u GEMINI_MODEL \
  -u GEMINI_API_KEY \
  -u GOOGLE_GEMINI_BASE_URL \
  gemini -m gemini-3.1-pro "$@"
