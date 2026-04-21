import test from "node:test"
import assert from "node:assert/strict"

import {
  ARTDECO_PAGE_ERROR_MESSAGE,
  extractArtDecoRequestIdFromHeaders,
  hasArtDecoPagePermission,
  isArtDecoPageDataEmpty,
  normalizeArtDecoApiResult,
  shouldUseArtDecoRequestCache,
  toArtDecoPageMessage,
} from "../artDecoPageTemplateHelpers.ts"

test("normalizeArtDecoApiResult unwraps nested response payload and prefers nested request id", () => {
  const normalized = normalizeArtDecoApiResult({
    success: true,
    request_id: "req-root-001",
    message: "root-message",
    data: {
      success: false,
      request_id: "req-nested-001",
      message: "nested-message",
      data: {
        positions: 8,
      },
    },
  })

  assert.deepEqual(normalized, {
    payload: { positions: 8 },
    requestId: "req-nested-001",
    success: false,
    message: "nested-message",
  })
})

test("normalizeArtDecoApiResult falls back to response headers and raw payload shapes", () => {
  const normalized = normalizeArtDecoApiResult({
    headers: {
      "x-request-id": "req-header-001",
    },
    data: {
      rows: 5,
    },
  })

  assert.deepEqual(normalized, {
    payload: { rows: 5 },
    requestId: "req-header-001",
    success: true,
    message: "",
  })

  assert.deepEqual(normalizeArtDecoApiResult(["row"]), {
    payload: ["row"],
    requestId: "",
    success: true,
    message: "",
  })
})

test("request id extraction and message fallback preserve page contract defaults", () => {
  assert.equal(extractArtDecoRequestIdFromHeaders({ "x-request-id": "req-123" }), "req-123")
  assert.equal(extractArtDecoRequestIdFromHeaders({ traceId: "req-456" }), "")

  assert.equal(toArtDecoPageMessage("上游失败"), "上游失败")
  assert.equal(toArtDecoPageMessage(""), ARTDECO_PAGE_ERROR_MESSAGE)
  assert.equal(toArtDecoPageMessage(null), ARTDECO_PAGE_ERROR_MESSAGE)
})

test("empty-state helper distinguishes disabled evaluation, empty payloads and populated objects", () => {
  assert.equal(isArtDecoPageDataEmpty(null, false), false)
  assert.equal(isArtDecoPageDataEmpty(null, true), true)
  assert.equal(isArtDecoPageDataEmpty([], true), true)
  assert.equal(isArtDecoPageDataEmpty({}, true), true)
  assert.equal(isArtDecoPageDataEmpty({ rows: [] }, true), false)
})

test("permission helper tolerates malformed storage and supports wildcard authorization", () => {
  assert.equal(hasArtDecoPagePermission("", null), true)
  assert.equal(hasArtDecoPagePermission("risk:admin", null), true)
  assert.equal(hasArtDecoPagePermission("risk:admin", "{broken-json"), true)
  assert.equal(
    hasArtDecoPagePermission("risk:admin", JSON.stringify({ permissions: ["*"] })),
    true,
  )
  assert.equal(
    hasArtDecoPagePermission("risk:admin", JSON.stringify({ permissions: ["risk:view-basic"] })),
    false,
  )
})

test("cache helper allows no-cache mode and blocks duplicate requests inside cache window", () => {
  assert.equal(shouldUseArtDecoRequestCache(0, 0, 1000), true)
  assert.equal(shouldUseArtDecoRequestCache(1000, 10000, 5000), false)
  assert.equal(shouldUseArtDecoRequestCache(1000, 10000, 12001), true)
})
