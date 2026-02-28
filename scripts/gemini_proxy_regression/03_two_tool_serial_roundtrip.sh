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
    {role: "user", parts: [{text: "请先搜索 TODO，再读取 README.md，然后总结。"}]},
    {role: "model", parts: [{functionCall: {name: "grep_search", args: {pattern: "TODO"}}}]},
    {role: "user", parts: [{functionResponse: {name: "grep_search", response: {result: "TODO found in README.md"}}}]},
    {role: "model", parts: [{functionCall: {name: "read_file", args: {file_path: "README.md"}}}]},
    {role: "user", parts: [{functionResponse: {name: "read_file", response: {content: "# Demo README"}}}]}
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
        },
        {
          name: "read_file",
          description: "Read file",
          parameters: {
            type: "object",
            properties: {file_path: {type: "string"}},
            required: ["file_path"]
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

if jq -e '.error == null and (.candidates | length > 0)' "$RESP" >/dev/null; then
  echo "PASS: two-tool serial roundtrip"
  jq -r '.candidates[0].content.parts[0].text // "response has no text part"' "$RESP"
  exit 0
fi

echo "FAIL: two-tool serial roundtrip failed"
jq -c '.error // .candidates[0].content.parts[0]' "$RESP"
exit 1
