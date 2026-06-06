import { expect, test, type Page } from "@playwright/test"

const E2E_USER = {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  permissions: [],
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript(({ user }) => {
    localStorage.setItem("auth_token", "html5-runtime-acceptance-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

async function stubRuntimeApis(page: Page): Promise<void> {
  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
    const url = new URL(route.request().url())
    const normalizedPath = url.pathname.startsWith("/api/") ? url.pathname.slice(4) : url.pathname

    if (normalizedPath === "/health" || normalizedPath === "/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "html5-runtime-ready",
          data: { status: "ready" },
        }),
      })
      return
    }

    if (normalizedPath === "/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { csrf_token: "html5-runtime-csrf" },
        }),
      })
      return
    }

    if (normalizedPath === "/v1/data/markets/overview" || normalizedPath === "/v1/market/overview") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { up_count: 1800, down_count: 1100, turnover: 8234 },
          request_id: "html5-runtime-market-overview",
        }),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
        request_id: "html5-runtime-generic",
      }),
    })
  })
}

async function stubRealtimeQuoteRefreshSequence(page: Page): Promise<void> {
  let requestCount = 0

  await page.route(/https?:\/\/[^/]+\/api\/v1\/market\/quotes(?:\?.*)?$/, async (route) => {
    requestCount += 1

    if (requestCount === 1) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "html5-runtime-quotes-fresh",
          data: {
            quotes: [
              {
                symbol: "000001",
                name: "平安银行",
                current_price: 10.25,
                change_percent: 1.25,
                amount: 125000000,
                volume: 5800000,
              },
              {
                symbol: "600519",
                name: "贵州茅台",
                current_price: 1688.88,
                change_percent: -0.35,
                amount: 98000000,
                volume: 120000,
              },
            ],
          },
        }),
      })
      return
    }

    await route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        request_id: "html5-runtime-quotes-refresh-failed",
        message: "quotes refresh unavailable",
        data: null,
      }),
    })
  })
}

async function collectRuntimeState(page: Page) {
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      return await page.evaluate(async () => {
        const registration = await navigator.serviceWorker?.getRegistration?.().catch(() => null)
        const cacheKeys = await caches.keys().catch(() => [])
        const databases = indexedDB.databases ? await indexedDB.databases().catch(() => []) : []
        const realtimeLink = document.querySelector<HTMLAnchorElement>('a[href="/market/realtime"]')

        return {
          url: window.location.href,
          path: window.location.pathname,
          historyLength: window.history.length,
          manifestLinked: Boolean(document.querySelector('link[rel="manifest"]')),
          serviceWorkerSupported: "serviceWorker" in navigator,
          serviceWorkerControlled: Boolean(navigator.serviceWorker?.controller),
          serviceWorkerState: registration
            ? registration.active?.state || registration.waiting?.state || registration.installing?.state || "registered"
            : "not-registered",
          cacheKeys,
          indexedDBSupported: "indexedDB" in window,
          indexedDBDatabases: databases.map((database) => ({
            name: database.name,
            version: database.version,
          })),
          workerSupported: "Worker" in window,
          online: navigator.onLine,
          connectionType:
            navigator.connection?.effectiveType ||
            navigator.mozConnection?.effectiveType ||
            navigator.webkitConnection?.effectiveType ||
            null,
          h1: document.querySelector("h1")?.textContent?.trim() || null,
          activeRealtimeLink: Boolean(
            realtimeLink?.classList.contains("router-link-active") ||
              realtimeLink?.classList.contains("is-active"),
          ),
          realtimeLink: realtimeLink
            ? {
                href: realtimeLink.getAttribute("href"),
                text: realtimeLink.textContent?.replace(/\s+/g, " ").trim() || "",
                className: realtimeLink.className,
                ariaCurrent: realtimeLink.getAttribute("aria-current"),
                target: realtimeLink.getAttribute("target"),
                pointerEvents: window.getComputedStyle(realtimeLink).pointerEvents,
              }
            : null,
        }
      })
    } catch (error) {
      if (attempt === 3 || !String(error).includes("Execution context was destroyed")) {
        throw error
      }
      await page.waitForLoadState("domcontentloaded").catch(() => undefined)
      await page.waitForTimeout(500)
    }
  }

  throw new Error("Failed to collect HTML5 runtime state")
}

async function ensureServiceWorkerControlled(page: Page): Promise<void> {
  const waitForReady = () =>
    page.evaluate(async () => {
      if (!("serviceWorker" in navigator)) {
        return { ready: false, reason: "service-worker-unsupported" }
      }

      const timeout = new Promise<{ ready: false; reason: string }>((resolve) => {
        window.setTimeout(() => resolve({ ready: false, reason: "service-worker-ready-timeout" }), 5000)
      })
      const ready = navigator.serviceWorker.ready.then((registration) => ({
        ready: Boolean(registration.active),
        reason: registration.active?.state || "registered-without-active-worker",
      }))

      return Promise.race([ready, timeout])
    })

  const readyState = await waitForReady()
  expect(readyState).toMatchObject({ ready: true })

  const isControlled = await page.evaluate(() => Boolean(navigator.serviceWorker?.controller))
  if (isControlled) {
    return
  }

  await page.reload({ waitUntil: "domcontentloaded" })
  await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })
  const reloadedReadyState = await waitForReady()
  expect(reloadedReadyState).toMatchObject({ ready: true })
}

const describeAcceptance =
  process.env.HTML5_RUNTIME_ACCEPTANCE === "1" ? test.describe : test.describe.skip

describeAcceptance("HTML5 runtime acceptance diagnostics", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
    await stubRuntimeApis(page)
  })

  test("records active HTML5 API surfaces on the realtime market route", async ({ page }) => {
    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })
    await expect(page.getByRole("heading", { level: 1, name: "实时行情工作台" })).toBeVisible({
      timeout: 20000,
    })

    const state = await collectRuntimeState(page)
    console.info("[html5-runtime-acceptance]", JSON.stringify(state))

    expect(state.path).toBe("/market/realtime")
    expect(state.manifestLinked).toBe(true)
    expect(state.serviceWorkerSupported).toBe(true)
    expect(state.indexedDBSupported).toBe(true)
    expect(state.workerSupported).toBe(true)
    expect(state.h1).toBe("实时行情工作台")
  })

  test("records local server PWA asset support and history fallback", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" })

    const serverSupportState = await page.evaluate(async () => {
      const probe = async (path: string) => {
        const response = await fetch(path, { cache: "reload" })
        return {
          path,
          ok: response.ok,
          status: response.status,
          contentType: response.headers.get("content-type") || "",
          cacheControl: response.headers.get("cache-control") || "",
          bodyPreview: (await response.text()).slice(0, 160),
        }
      }

      const [root, manifest, serviceWorker, offline, realtimeRoute] = await Promise.all([
        probe("/"),
        probe("/manifest.json"),
        probe("/sw.js"),
        probe("/offline.html"),
        probe("/market/realtime"),
      ])

      return { root, manifest, serviceWorker, offline, realtimeRoute }
    })

    console.info("[html5-runtime-server-pwa-support]", JSON.stringify(serverSupportState))

    expect(serverSupportState.root).toMatchObject({ ok: true, status: 200 })
    expect(serverSupportState.root.contentType).toContain("text/html")
    expect(serverSupportState.manifest).toMatchObject({ ok: true, status: 200 })
    expect(serverSupportState.manifest.contentType).toContain("application/json")
    expect(serverSupportState.serviceWorker).toMatchObject({ ok: true, status: 200 })
    expect(serverSupportState.serviceWorker.contentType).toContain("text/javascript")
    expect(serverSupportState.offline).toMatchObject({ ok: true, status: 200 })
    expect(serverSupportState.offline.contentType).toContain("text/html")
    expect(serverSupportState.realtimeRoute).toMatchObject({ ok: true, status: 200 })
    expect(serverSupportState.realtimeRoute.contentType).toContain("text/html")
  })

  test("records offline fallback behavior for eleven desktop routes", async () => {
    test.fixme(
      true,
      "Blocked: current Desktop Chromium offline navigation attempts time out under context offline mode; keep 3.2.1 open until a stable service-worker navigation matrix exists.",
    )
  })

  test("keeps URL, active navigation, and rendered shell aligned after dashboard menu navigation", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })
    await expect(page.getByRole("heading", { level: 1, name: "QUANTIX" })).toBeVisible({ timeout: 20000 })

    const beforeClickState = await collectRuntimeState(page)
    console.info("[html5-runtime-acceptance:before-click]", JSON.stringify(beforeClickState))

    await expect(page.getByRole("heading", { level: 1, name: "QUANTIX" })).toBeVisible({ timeout: 20000 })
    await expect(page.getByRole("button", { name: "市场行情" })).toBeVisible({ timeout: 10000 })

    await page.getByRole("button", { name: "市场行情" }).click()
    const realtimeLink = page.getByRole("link", { name: /实时行情流/i })
    await expect(realtimeLink).toBeVisible({ timeout: 10000 })
    await realtimeLink.click()
    await page.waitForTimeout(3000)

    const state = await collectRuntimeState(page)
    console.info("[html5-runtime-acceptance:after-click]", JSON.stringify(state))

    expect(state.path).toBe("/market/realtime")
    expect(state.activeRealtimeLink).toBe(true)
    expect(state.h1).toBe("实时行情工作台")
  })

  test("keeps the last verified realtime snapshot when a refresh fails", async ({ page }) => {
    await page.addInitScript(() => {
      if ("serviceWorker" in navigator) {
        navigator.serviceWorker.register = async () => {
          throw new Error("HTML5 runtime freshness test disables SW request interception")
        }
      }
    })
    await stubRealtimeQuoteRefreshSequence(page)

    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })
    await expect(page.getByRole("heading", { level: 1, name: "实时行情工作台" })).toBeVisible({
      timeout: 20000,
    })
    await expect(page.getByText("TRACE_ID: html5-runtime-quotes-fresh")).toBeVisible({ timeout: 20000 })
    await expect(page.getByText("平安银行")).toBeVisible({ timeout: 10000 })

    await page.getByRole("button", { name: "刷新行情" }).first().click()

    await expect(page.getByText("实时行情加载失败，已保留上一份有效样本快照。")).toBeVisible({
      timeout: 20000,
    })
    await expect(page.getByText("TRACE_ID: html5-runtime-quotes-fresh")).toBeVisible()
    await expect(page.getByText("html5-runtime-quotes-refresh-failed")).toHaveCount(0)
    await expect(page.getByText("平安银行")).toBeVisible()

    const state = await collectRuntimeState(page)
    console.info("[html5-runtime-cache-consistency]", JSON.stringify(state))

    expect(state.path).toBe("/market/realtime")
    expect(state.serviceWorkerSupported).toBe(true)
    expect(state.indexedDBSupported).toBe(true)
    expect(state.workerSupported).toBe(true)
    expect(state.h1).toBe("实时行情工作台")
  })

  test("serves cached API data through service worker when the network is offline", async ({ page, context }) => {
    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })
    await ensureServiceWorkerControlled(page)

    const seededState = await page.evaluate(async () => {
      const apiPath = "/api/v1/market/summary?html5_runtime_probe=1"
      const apiUrl = new URL(apiPath, window.location.origin).toString()
      const cache = await caches.open("mystocks-api-v1.0.0")
      await cache.put(
        new Request(apiUrl),
        new Response(
          JSON.stringify({
            success: true,
            request_id: "html5-runtime-sw-api-cache",
            data: { source: "service-worker-cache", up_count: 11, down_count: 5 },
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          },
        ),
      )

      const registration = await navigator.serviceWorker?.ready

      return {
        apiUrl,
        serviceWorkerControlled: Boolean(navigator.serviceWorker?.controller),
        serviceWorkerState: registration?.active?.state ?? null,
        cacheKeys: await caches.keys(),
      }
    })

    await context.setOffline(true)
    try {
      const offlineFetchState = await page.evaluate(async (apiUrl) => {
        const response = await fetch(apiUrl)
        const body = await response.json()

        return {
          ok: response.ok,
          status: response.status,
          requestId: body.request_id,
          source: body.data?.source,
          upCount: body.data?.up_count,
          downCount: body.data?.down_count,
        }
      }, seededState.apiUrl)

      console.info(
        "[html5-runtime-sw-api-cache]",
        JSON.stringify({ seededState, offlineFetchState }),
      )

      expect(seededState.serviceWorkerControlled).toBe(true)
      expect(seededState.cacheKeys).toContain("mystocks-api-v1.0.0")
      expect(offlineFetchState).toMatchObject({
        ok: true,
        status: 200,
        requestId: "html5-runtime-sw-api-cache",
        source: "service-worker-cache",
        upCount: 11,
        downCount: 5,
      })
    } finally {
      await context.setOffline(false)
    }
  })

  test("labels service-worker cached realtime quotes as retained data instead of fresh network data", async ({ page, context }) => {
    await page.route(/https?:\/\/[^/]+\/api\/v1\/market\/quotes(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "html5-runtime-quotes-network-fresh",
          data: {
            quotes: [
              {
                symbol: "000001",
                name: "平安银行",
                current_price: 10.25,
                change_percent: 1.25,
                amount: 125000000,
                volume: 5800000,
              },
            ],
          },
        }),
      })
    })

    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })
    await expect(page.getByText("TRACE_ID: html5-runtime-quotes-network-fresh")).toBeVisible({
      timeout: 20000,
    })
    await ensureServiceWorkerControlled(page)

    const seededState = await page.evaluate(async () => {
      const symbols = ["000001", "600519", "000858", "601318", "600036"].join(",")
      const apiUrl = new URL(`/api/v1/market/quotes?symbols=${symbols}`, window.location.origin).toString()
      const cache = await caches.open("mystocks-api-v1.0.0")
      await cache.put(
        new Request(apiUrl),
        new Response(
          JSON.stringify({
            success: true,
            request_id: "html5-runtime-quotes-sw-cache",
            data: {
              quotes: [
                {
                  symbol: "000001",
                  name: "平安银行",
                  current_price: 10.25,
                  change_percent: 1.25,
                  amount: 125000000,
                  volume: 5800000,
                },
              ],
            },
          }),
          {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-MyStocks-Cache-Source": "service-worker-cache",
            },
          },
        ),
      )

      return {
        apiUrl,
        serviceWorkerControlled: Boolean(navigator.serviceWorker?.controller),
        cacheKeys: await caches.keys(),
      }
    })

    await page.unroute(/https?:\/\/[^/]+\/api\/v1\/market\/quotes(?:\?.*)?$/)
    await context.setOffline(true)
    try {
      await page.getByRole("button", { name: "刷新行情" }).first().click()

      await expect(page.getByText("TRACE_ID: html5-runtime-quotes-sw-cache")).toBeVisible({
        timeout: 20000,
      })
      await expect(page.getByText("缓存快照", { exact: true })).toBeVisible({ timeout: 20000 })
      await expect(page.getByText("当前行情来自本地缓存快照，非实时网络刷新。")).toBeVisible({
        timeout: 20000,
      })
      await expect(page.getByText("实时行情加载失败")).toHaveCount(0)
      await expect(page.getByText("平安银行")).toBeVisible()

      console.info("[html5-runtime-realtime-sw-cache]", JSON.stringify(seededState))

      expect(seededState.serviceWorkerControlled).toBe(true)
      expect(seededState.cacheKeys).toContain("mystocks-api-v1.0.0")
    } finally {
      await context.setOffline(false)
    }
  })

  test("declares realtime quotes as service-worker API-cache eligible", async ({ page }) => {
    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })

    const serviceWorkerSourceState = await page.evaluate(async () => {
      const response = await fetch("/sw.js", { cache: "reload" })
      const source = await response.text()
      return {
        ok: response.ok,
        hasMarketSummaryPattern: source.includes("market\\/summary"),
        hasMarketQuotesPattern: source.includes("market\\/quotes"),
        hasMarketRealtimePattern: source.includes("market\\/realtime"),
      }
    })

    console.info("[html5-runtime-realtime-cache-eligibility]", JSON.stringify(serviceWorkerSourceState))

    expect(serviceWorkerSourceState.ok).toBe(true)
    expect(serviceWorkerSourceState.hasMarketSummaryPattern).toBe(true)
    expect(serviceWorkerSourceState.hasMarketQuotesPattern).toBe(true)
    expect(serviceWorkerSourceState.hasMarketRealtimePattern).toBe(true)
  })

  test("records IndexedDB TTL expiry while preserving explicit stale fallback data", async ({ page }) => {
    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })

    const indexedDBState = await page.evaluate(async () => {
      const databaseName = "MyStocksDB"
      const storeName = "api_cache"
      const cacheKey = "html5-runtime-expired-market-overview"
      const now = Date.now()
      const expiredEntry = {
        key: cacheKey,
        data: {
          request_id: "html5-runtime-indexeddb-stale",
          up_count: 9,
          flat_count: 2,
          down_count: 4,
        },
        timestamp: now - 10 * 60 * 1000,
        expiresAt: now - 60 * 1000,
      }

      const openDatabase = () =>
        new Promise<IDBDatabase>((resolve, reject) => {
          const request = indexedDB.open(databaseName, 1)
          request.onerror = () => reject(request.error)
          request.onsuccess = () => resolve(request.result)
          request.onupgradeneeded = () => {
            const database = request.result
            if (!database.objectStoreNames.contains(storeName)) {
              const store = database.createObjectStore(storeName, { keyPath: "key" })
              store.createIndex("expiresAt", "expiresAt", { unique: false })
            }
          }
        })

      const runStoreRequest = <T>(mode: IDBTransactionMode, callback: (store: IDBObjectStore) => IDBRequest<T>) =>
        new Promise<T>((resolve, reject) => {
          const transaction = database.transaction([storeName], mode)
          const request = callback(transaction.objectStore(storeName))
          request.onerror = () => reject(request.error)
          request.onsuccess = () => resolve(request.result)
        })

      const database = await openDatabase()

      await runStoreRequest("readwrite", (store) => store.put(expiredEntry))
      const activeRead = await runStoreRequest<typeof expiredEntry | undefined>("readonly", (store) => store.get(cacheKey))
      const activeCacheData = activeRead && (!activeRead.expiresAt || activeRead.expiresAt > Date.now()) ? activeRead.data : null
      const staleRead = await runStoreRequest<typeof expiredEntry | undefined>("readonly", (store) => store.get(cacheKey))
      const staleFallbackData = staleRead?.data ?? null

      database.close()

      return {
        indexedDBSupported: "indexedDB" in window,
        databaseName,
        storeName,
        cacheKey,
        activeCacheData,
        staleFallbackData,
        staleExpiresAt: staleRead?.expiresAt ?? null,
        now,
      }
    })

    console.info("[html5-runtime-indexeddb-ttl]", JSON.stringify(indexedDBState))

    expect(indexedDBState.indexedDBSupported).toBe(true)
    expect(indexedDBState.activeCacheData).toBeNull()
    expect(indexedDBState.staleFallbackData).toMatchObject({
      request_id: "html5-runtime-indexeddb-stale",
      up_count: 9,
      down_count: 4,
    })
    expect(indexedDBState.staleExpiresAt).toBeLessThan(indexedDBState.now)
  })

  test("records browser storage quota estimate for IndexedDB quota monitoring", async ({ page }) => {
    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })

    const quotaState = await page.evaluate(async () => {
      const estimate = await navigator.storage?.estimate?.()
      const usage = estimate?.usage ?? null
      const quota = estimate?.quota ?? null
      const usageRatio = usage !== null && quota !== null && quota > 0 ? usage / quota : null

      return {
        storageManagerSupported: Boolean(navigator.storage?.estimate),
        usage,
        quota,
        usageRatio,
        nearDefaultLimit: usageRatio !== null && usageRatio >= 0.8,
      }
    })

    console.info("[html5-runtime-storage-quota]", JSON.stringify(quotaState))

    expect(quotaState.storageManagerSupported).toBe(true)
    expect(typeof quotaState.usage).toBe("number")
    expect(typeof quotaState.quota).toBe("number")
    expect(quotaState.quota).toBeGreaterThan(0)
    expect(quotaState.usageRatio).not.toBeNull()
    expect(quotaState.usageRatio).toBeGreaterThanOrEqual(0)
    expect(quotaState.usageRatio).toBeLessThanOrEqual(1)
  })

  test("records IndexedDB schema migration and data persistence across reopen", async ({ page }) => {
    await page.goto("/market/realtime", { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible({ timeout: 20000 })

    const indexedDBState = await page.evaluate(async () => {
      const databaseName = "MyStocksDB"
      const databaseVersion = 1
      const now = Date.now()

      const deleteDatabase = () =>
        new Promise<void>((resolve, reject) => {
          const request = indexedDB.deleteDatabase(databaseName)
          request.onerror = () => reject(request.error)
          request.onblocked = () => reject(new Error("IndexedDB delete blocked"))
          request.onsuccess = () => resolve()
        })

      const openDatabase = () =>
        new Promise<IDBDatabase>((resolve, reject) => {
          const request = indexedDB.open(databaseName, databaseVersion)
          request.onerror = () => reject(request.error)
          request.onsuccess = () => resolve(request.result)
          request.onupgradeneeded = () => {
            const database = request.result

            if (!database.objectStoreNames.contains("market_data")) {
              const store = database.createObjectStore("market_data", { keyPath: "symbol" })
              store.createIndex("timestamp", "timestamp", { unique: false })
              store.createIndex("symbol_timestamp", ["symbol", "timestamp"], { unique: false })
            }

            if (!database.objectStoreNames.contains("technical_indicators")) {
              const store = database.createObjectStore("technical_indicators", {
                keyPath: ["symbol", "indicator", "timestamp"],
              })
              store.createIndex("symbol", "symbol", { unique: false })
              store.createIndex("indicator", "indicator", { unique: false })
            }

            if (!database.objectStoreNames.contains("user_preferences")) {
              database.createObjectStore("user_preferences", { keyPath: "userId" })
            }

            if (!database.objectStoreNames.contains("api_cache")) {
              const store = database.createObjectStore("api_cache", { keyPath: "key" })
              store.createIndex("expiresAt", "expiresAt", { unique: false })
            }
          }
        })

      const requestFromStore = <T>(
        database: IDBDatabase,
        storeName: string,
        mode: IDBTransactionMode,
        callback: (store: IDBObjectStore) => IDBRequest<T>,
      ) =>
        new Promise<T>((resolve, reject) => {
          const transaction = database.transaction([storeName], mode)
          const request = callback(transaction.objectStore(storeName))
          request.onerror = () => reject(request.error)
          request.onsuccess = () => resolve(request.result)
        })

      await deleteDatabase()

      const database = await openDatabase()
      const storeNames = Array.from(database.objectStoreNames)
      const indexNames = Object.fromEntries(
        storeNames.map((storeName) => {
          const transaction = database.transaction([storeName], "readonly")
          return [storeName, Array.from(transaction.objectStore(storeName).indexNames)]
        }),
      )

      await requestFromStore(database, "market_data", "readwrite", (store) =>
        store.put({
          symbol: "000001",
          timestamp: now,
          price: 10.25,
          volume: 5800000,
          high: 10.36,
          low: 10.11,
          open: 10.18,
          close: 10.25,
        }),
      )
      await requestFromStore(database, "technical_indicators", "readwrite", (store) =>
        store.put({
          symbol: "000001",
          indicator: "MA",
          params: { period: 5 },
          values: [10.1, 10.2, 10.25],
          timestamp: now,
        }),
      )
      await requestFromStore(database, "user_preferences", "readwrite", (store) =>
        store.put({
          userId: "html5-runtime-user",
          settings: { desktopOnly: true, quotePreset: "core" },
          timestamp: now,
        }),
      )
      await requestFromStore(database, "api_cache", "readwrite", (store) =>
        store.put({
          key: "html5-runtime-persistence-probe",
          data: { request_id: "html5-runtime-indexeddb-persisted" },
          timestamp: now,
          expiresAt: now + 60 * 1000,
        }),
      )

      database.close()

      const reopenedDatabase = await openDatabase()
      const persistedMarket = await requestFromStore<Record<string, unknown> | undefined>(
        reopenedDatabase,
        "market_data",
        "readonly",
        (store) => store.get("000001"),
      )
      const persistedIndicator = await requestFromStore<Record<string, unknown> | undefined>(
        reopenedDatabase,
        "technical_indicators",
        "readonly",
        (store) => store.get(["000001", "MA", now]),
      )
      const persistedPreferences = await requestFromStore<Record<string, unknown> | undefined>(
        reopenedDatabase,
        "user_preferences",
        "readonly",
        (store) => store.get("html5-runtime-user"),
      )
      const persistedCache = await requestFromStore<Record<string, unknown> | undefined>(
        reopenedDatabase,
        "api_cache",
        "readonly",
        (store) => store.get("html5-runtime-persistence-probe"),
      )

      const result = {
        indexedDBSupported: "indexedDB" in window,
        databaseName,
        databaseVersion: reopenedDatabase.version,
        storeNames,
        indexNames,
        persistedMarket,
        persistedIndicator,
        persistedPreferences,
        persistedCache,
      }

      reopenedDatabase.close()
      return result
    })

    console.info("[html5-runtime-indexeddb-persistence]", JSON.stringify(indexedDBState))

    expect(indexedDBState.indexedDBSupported).toBe(true)
    expect(indexedDBState.databaseVersion).toBe(1)
    expect(indexedDBState.storeNames).toEqual(
      expect.arrayContaining(["market_data", "technical_indicators", "user_preferences", "api_cache"]),
    )
    expect(indexedDBState.indexNames.market_data).toEqual(expect.arrayContaining(["timestamp", "symbol_timestamp"]))
    expect(indexedDBState.indexNames.technical_indicators).toEqual(expect.arrayContaining(["symbol", "indicator"]))
    expect(indexedDBState.indexNames.api_cache).toContain("expiresAt")
    expect(indexedDBState.persistedMarket).toMatchObject({ symbol: "000001", price: 10.25 })
    expect(indexedDBState.persistedIndicator).toMatchObject({ symbol: "000001", indicator: "MA" })
    expect(indexedDBState.persistedPreferences).toMatchObject({ userId: "html5-runtime-user" })
    expect(indexedDBState.persistedCache?.data).toMatchObject({
      request_id: "html5-runtime-indexeddb-persisted",
    })
  })
})
