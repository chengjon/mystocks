import test from "node:test"
import assert from "node:assert/strict"

import { createCSRFTokenResolver } from "../csrfTokenResolver.ts"

test("csrf token resolver fetches a fresh token for sequential calls", async () => {
  let calls = 0
  const resolver = createCSRFTokenResolver(async () => {
    calls += 1
    return `token-${calls}`
  })

  const first = await resolver()
  const second = await resolver()

  assert.equal(first, "token-1")
  assert.equal(second, "token-2")
  assert.equal(calls, 2)
})

test("csrf token resolver returns empty string on fetch failure", async () => {
  const resolver = createCSRFTokenResolver(async () => {
    throw new Error("boom")
  })

  assert.equal(await resolver(), "")
})
