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

REQ1="$(mktemp)"
RESP1="$(mktemp)"
REQ2="$(mktemp)"
RESP2="$(mktemp)"

jq -n '{
  contents: [
    {role: "user", parts: [{text: "请调用 grep_search 工具查找 TODO，pattern 填写 TODO。"}]}
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
}' > "$REQ1"

curl -sS "${BASE_URL}/v1beta/models/${MODEL}:generateContent" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"$REQ1" > "$RESP1"

if ! jq -e '.error == null' "$RESP1" >/dev/null; then
  echo "FAIL: first turn error"
  jq -c '.error' "$RESP1"
  exit 1
fi

CALL_NAME="$(jq -r '.candidates[0].content.parts[0].functionCall.name // empty' "$RESP1")"
CALL_ARGS="$(jq -c '.candidates[0].content.parts[0].functionCall.args // {}' "$RESP1")"

if [[ "$CALL_NAME" != "grep_search" ]]; then
  echo "FAIL: expected grep_search functionCall, got '${CALL_NAME}'"
  jq -c '.candidates[0].content.parts[0]' "$RESP1"
  exit 1
fi

jq -n --arg call_name "$CALL_NAME" --argjson call_args "$CALL_ARGS" '{
  contents: [
    {role: "user", parts: [{text: "请调用 grep_search 工具查找 TODO，pattern 填写 TODO。"}]},
    {role: "model", parts: [{functionCall: {name: $call_name, args: $call_args}}]},
    {role: "user", parts: [{functionResponse: {name: $call_name, response: {result: "found TODO in 3 files"}}}]}
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
}' > "$REQ2"

curl -sS "${BASE_URL}/v1beta/models/${MODEL}:generateContent" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"$REQ2" > "$RESP2"

if jq -e '.error == null and (.candidates | length > 0)' "$RESP2" >/dev/null; then
  echo "PASS: single tool roundtrip"
  jq -r '.candidates[0].content.parts[0].text // "response has no text part"' "$RESP2"
  exit 0
fi

echo "FAIL: tool roundtrip did not complete"
jq -c '.error // .candidates[0].content.parts[0]' "$RESP2"
exit 1
