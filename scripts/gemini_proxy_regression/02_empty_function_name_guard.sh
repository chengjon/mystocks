#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT_DIR}/.gemini/.env"

read_env() {
  local key="$1"
  if [[ -f "$ENV_FILE" ]]; then
    awk -F= -v k="$key" '$1==k {sub(/^[^=]*=/, ""); print; exit}' "$ENV_FILE"
  fi
}

API_KEY="${API_KEY:-$(read_env GEMINI_API_KEY)}"
BASE_URL="${BASE_URL:-$(read_env GOOGLE_GEMINI_BASE_URL)}"
MODEL="${MODEL:-gemini-3.1-pro}"

if [[ -z "$API_KEY" || -z "$BASE_URL" ]]; then
  echo "FAIL: missing API_KEY/BASE_URL. Set env or .gemini/.env"
  exit 2
fi

REQ="$(mktemp)"
RESP="$(mktemp)"

jq -n '{
  contents: [
    {role: "user", parts: [{text: "测试空函数名防御"}]},
    {role: "model", parts: [{functionCall: {name: "grep_search", args: {pattern: "TODO"}}}]},
    {role: "user", parts: [{functionResponse: {name: "", response: {result: "x"}}}]}
  ],
  tools: [
    {
      functionDeclarations: [
        {
          name: "grep_search",
          description: "Search text",
          parameters: {
            type: "object",
            properties: {pattern: {type: "string"}},
            required: ["pattern"]
          }
        }
      ]
    }
  ]
}' > "$REQ"

curl -sS "${BASE_URL}/v1beta/models/${MODEL}:generateContent" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"$REQ" > "$RESP"

MSG="$(jq -r '.error.message // ""' "$RESP")"

if [[ -n "$MSG" && "$MSG" =~ functionResponse && "$MSG" =~ name ]]; then
  echo "PASS: empty function name is rejected"
  echo "$MSG"
  exit 0
fi

echo "FAIL: expected explicit functionResponse.name validation error"
jq -c '.' "$RESP"
exit 1
