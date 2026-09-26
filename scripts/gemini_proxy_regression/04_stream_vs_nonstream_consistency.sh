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
RESP_NONSTREAM="$(mktemp)"
RESP_STREAM_RAW="$(mktemp)"
RESP_STREAM_JSON="$(mktemp)"

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
}' > "$REQ"

curl -sS "${BASE_URL}/v1beta/models/${MODEL}:generateContent" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"$REQ" > "$RESP_NONSTREAM"

if ! jq -e '.error == null' "$RESP_NONSTREAM" >/dev/null; then
  echo "FAIL: non-stream call failed"
  jq -c '.error' "$RESP_NONSTREAM"
  exit 1
fi

NONSTREAM_CALL="$(jq -r '.candidates[0].content.parts[0].functionCall.name // empty' "$RESP_NONSTREAM")"

curl -sS -N "${BASE_URL}/v1beta/models/${MODEL}:streamGenerateContent?alt=sse" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"$REQ" > "$RESP_STREAM_RAW"

sed -n 's/^data: //p' "$RESP_STREAM_RAW" | sed '/^\[DONE\]$/d;/^$/d' > "$RESP_STREAM_JSON"

STREAM_CALL="$(
  jq -r '.candidates[0].content.parts[0].functionCall.name // empty' "$RESP_STREAM_JSON" \
    2>/dev/null | awk 'NF {print; exit}'
)"

if [[ -n "$NONSTREAM_CALL" && -n "$STREAM_CALL" && "$NONSTREAM_CALL" == "$STREAM_CALL" ]]; then
  echo "PASS: stream/non-stream functionCall is consistent (${NONSTREAM_CALL})"
  exit 0
fi

echo "FAIL: stream/non-stream mismatch"
echo "non-stream functionCall: ${NONSTREAM_CALL:-<empty>}"
echo "stream functionCall: ${STREAM_CALL:-<empty>}"
echo "--- stream raw tail ---"
tail -n 30 "$RESP_STREAM_RAW"
exit 1
