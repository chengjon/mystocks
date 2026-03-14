import test from "node:test"
import assert from "node:assert/strict"

import {
  buildDataSourceConfigBatchRequest,
  supportsDataSourceConfigWrite,
} from "../dataManagementCapabilities.ts"

test("data source config write is enabled when backend batch contract is available", () => {
  assert.equal(supportsDataSourceConfigWrite(), true)
})

test("buildDataSourceConfigBatchRequest converts enable toggle into status updates", () => {
  const payload = buildDataSourceConfigBatchRequest(
    [
      {
        endpointName: "akshare.stock_zh_a_hist",
        name: "akshare",
        enabled: false,
        endpoint: "https://ak.example/api",
        status: "active",
      },
      {
        endpointName: "tushare.stock_basic",
        name: "tushare",
        enabled: true,
        endpoint: "https://ts.example/api",
        status: "maintenance",
      },
    ],
    [
      {
        endpointName: "akshare.stock_zh_a_hist",
        name: "akshare",
        enabled: true,
        endpoint: "https://ak.example/api",
        status: "active",
      },
      {
        endpointName: "tushare.stock_basic",
        name: "tushare",
        enabled: false,
        endpoint: "https://ts.example/api",
        status: "maintenance",
      },
    ],
  )

  assert.deepEqual(payload, {
    operations: [
      {
        action: "update",
        endpoint_name: "akshare.stock_zh_a_hist",
        updates: {
          status: "maintenance",
        },
      },
      {
        action: "update",
        endpoint_name: "tushare.stock_basic",
        updates: {
          status: "active",
        },
      },
    ],
  })
})
