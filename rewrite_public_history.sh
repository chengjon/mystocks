#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}" && pwd)"
SOURCE_REPO="${1:-$REPO_ROOT}"
TARGET_REPO="${2:-/tmp/$(basename "$REPO_ROOT")-public-sanitized.git}"
REPLACE_FILE="${3:-$REPO_ROOT/filter-repo-replacements.txt}"
REMOVE_PATHS_FILE="${4:-$REPO_ROOT/filter-repo-remove-paths.txt}"
TMP_REPLACE_FILE=""
TMP_GITCONFIG_FILE=""

usage() {
    cat <<'EOF'
Usage:
  rewrite_public_history.sh [source_repo] [target_mirror_repo] [replace_file] [remove_paths_file]

Behavior:
  1. Create a fresh mirror clone from source_repo
  2. Rewrite history with git-filter-repo
  3. Verify that known leaked literals are absent from rewritten HEAD

Notes:
  - The source repository must already contain the sanitized content you want in the final history.
  - This script clones committed git history only; uncommitted working-tree changes are not included.
  - Run it against a clean branch tip or after committing your current sanitization work.
  - Provide the old leaked values via environment variables instead of storing them in git.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if ! command -v git-filter-repo >/dev/null 2>&1; then
    echo "git-filter-repo is required but not installed." >&2
    exit 1
fi

if [[ ! -d "$SOURCE_REPO/.git" && ! -f "$SOURCE_REPO/HEAD" ]]; then
    echo "Source repository not found: $SOURCE_REPO" >&2
    exit 1
fi

if [[ ! -f "$REPLACE_FILE" ]]; then
    echo "Replacement file not found: $REPLACE_FILE" >&2
    exit 1
fi

if [[ ! -f "$REMOVE_PATHS_FILE" ]]; then
    echo "Path filter file not found: $REMOVE_PATHS_FILE" >&2
    exit 1
fi

required_env_vars=(
    OLD_PROVIDER_API_KEY
    OLD_FUCAI_API_KEY
    OLD_MODEL_CATALOG_API_KEY
    OLD_WEB_READER_TOKEN
    OLD_JWT_TOKEN
    OLD_POSTGRES_PASSWORD
    OLD_INTERNAL_HOST
)

for env_var in "${required_env_vars[@]}"; do
    if [[ -z "${!env_var:-}" ]]; then
        echo "Missing required environment variable: $env_var" >&2
        exit 1
    fi
done

if [[ -e "$TARGET_REPO" ]]; then
    echo "Target already exists: $TARGET_REPO" >&2
    echo "Remove it first or pass a different target path." >&2
    exit 1
fi

TMP_REPLACE_FILE="$(mktemp /tmp/git-filter-repo-replacements.XXXXXX.txt)"
TMP_GITCONFIG_FILE="$(mktemp /tmp/git-filter-repo-config.XXXXXX)"
trap 'rm -f "$TMP_REPLACE_FILE" "$TMP_GITCONFIG_FILE"' EXIT

git config --file "$TMP_GITCONFIG_FILE" --add safe.directory "$SOURCE_REPO"
git config --file "$TMP_GITCONFIG_FILE" --add safe.directory "$SOURCE_REPO/.git"

sed \
    -e "s|__OLD_PROVIDER_API_KEY__|$OLD_PROVIDER_API_KEY|g" \
    -e "s|__OLD_FUCAI_API_KEY__|$OLD_FUCAI_API_KEY|g" \
    -e "s|__OLD_MODEL_CATALOG_API_KEY__|$OLD_MODEL_CATALOG_API_KEY|g" \
    -e "s|__OLD_WEB_READER_TOKEN__|$OLD_WEB_READER_TOKEN|g" \
    -e "s|__OLD_JWT_TOKEN__|$OLD_JWT_TOKEN|g" \
    -e "s|__OLD_POSTGRES_PASSWORD__|$OLD_POSTGRES_PASSWORD|g" \
    -e "s|__OLD_INTERNAL_HOST__|$OLD_INTERNAL_HOST|g" \
    "$REPLACE_FILE" > "$TMP_REPLACE_FILE"

echo "[1/4] Creating mirror clone: $TARGET_REPO"
GIT_CONFIG_GLOBAL="$TMP_GITCONFIG_FILE" git clone --mirror "$SOURCE_REPO" "$TARGET_REPO"

echo "[2/4] Rewriting history"
git -C "$TARGET_REPO" filter-repo \
    --force \
    --sensitive-data-removal \
    --no-fetch \
    --replace-text "$TMP_REPLACE_FILE" \
    --paths-from-file "$REMOVE_PATHS_FILE" \
    --invert-paths

echo "[3/4] Verifying known leaked literals are gone from HEAD"
declare -a banned_literals=(
    "$OLD_PROVIDER_API_KEY"
    "$OLD_FUCAI_API_KEY"
    "$OLD_MODEL_CATALOG_API_KEY"
    "$OLD_WEB_READER_TOKEN"
    "$OLD_POSTGRES_PASSWORD"
    "$OLD_INTERNAL_HOST"
    "$OLD_JWT_TOKEN"
)

for literal in "${banned_literals[@]}"; do
    if git --git-dir="$TARGET_REPO" grep -nI -F "$literal" HEAD -- . >/tmp/git-filter-repo-check.out; then
        echo "Found banned literal after rewrite: $literal" >&2
        cat /tmp/git-filter-repo-check.out >&2
        exit 1
    fi
done

echo "[4/4] Done"
cat <<EOF
Sanitized mirror repository created at:
  $TARGET_REPO

Suggested next commands:
  git -C "$TARGET_REPO" log --stat -n 3
  git -C "$TARGET_REPO" remote -v
  git -C "$TARGET_REPO" push --force --mirror origin

After force-pushing:
  1. Rotate all exposed credentials if not already done
  2. Ask collaborators to re-clone
  3. Invalidate CI caches/artifacts if they may contain old data
EOF
