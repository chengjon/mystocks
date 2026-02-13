/**
 * MyStocks PWA Service Worker
 * Advanced caching strategies for quantitative trading platform
 */

const CACHE_NAME = 'mystocks-v1.0.0'
const API_CACHE_NAME = 'mystocks-api-v1.0.0'
const FONT_CACHE_NAME = 'mystocks-fonts-v1.0.0'

// Static assets to cache immediately
const STATIC_CACHE_URLS = [
  '/',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
]

// API endpoints that should be cached
const API_CACHE_PATTERNS = [
  /\/api\/v1\/market\/summary/,
  /\/api\/v1\/market\/realtime/,
  /\/api\/v1\/stocks\/list/,
  /\/api\/v1\/analysis\/indicators/
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...')

  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('📦 Caching static assets...')
        return cache.addAll(STATIC_CACHE_URLS)
      }),

      // Skip waiting to activate immediately
      self.skipWaiting()
    ]).then(() => {
      console.log('✅ Service Worker installed and static assets cached')
    }).catch((error) => {
      console.error('❌ Service Worker installation failed:', error)
    })
  )
})

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...')

  event.waitUntil(
    Promise.all([
      // Take control of all clients immediately
      self.clients.claim(),

      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME &&
                cacheName !== API_CACHE_NAME &&
                cacheName !== FONT_CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      })
    ]).then(() => {
      console.log('✅ Service Worker activated and old caches cleaned')
    }).catch((error) => {
      console.error('❌ Service Worker activation failed:', error)
    })
  )
})

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Handle different types of requests
  if (request.method !== 'GET') {
    return // Skip non-GET requests
  }

  // API requests - Network First strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request))
    return
  }

  // Font requests - Cache First strategy
  if (url.hostname === 'fonts.googleapis.com' ||
      url.hostname === 'fonts.gstatic.com') {
    event.respondWith(handleFontRequest(request))
    return
  }

  // Static assets - Cache First strategy
  if (isStaticAsset(request)) {
    event.respondWith(handleStaticRequest(request))
    return
  }

  // Navigation requests - Network First with offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(request))
    return
  }

  // Default - Network First
  event.respondWith(
    fetch(request).catch(() => {
      // Fallback for failed requests
      return new Response('Offline - Content not available', {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'text/plain' }
      })
    })
  )
})

// Handle API requests (Network First)
async function handleApiRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(API_CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    // Always return the network response (including 4xx/5xx)
    // Only network failures (offline) should trigger cache/503 fallback
    return networkResponse
  } catch (error) {
    console.warn('🌐 Network request failed, trying cache:', error)
  }

  // Fallback to cache (only reached on network failure, not HTTP errors)
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    console.log('📦 Serving API response from cache:', request.url)
    return cachedResponse
  }

  // Return offline message (only when truly offline and no cache)
  return new Response(
    JSON.stringify({
      error: 'Offline',
      message: 'You are currently offline. Please check your internet connection.',
      offline: true
    }),
    {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    }
  )
}

// Handle font requests (Cache First)
async function handleFontRequest(request) {
  // Try cache first
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    return cachedResponse
  }

  try {
    // Fetch from network and cache
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(FONT_CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    console.warn('❌ Font request failed:', error)
    // Return a basic fallback font or error
    return new Response('', { status: 404 })
  }
}

// Handle static assets (Cache First)
async function handleStaticRequest(request) {
  // Try cache first
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    return cachedResponse
  }

  try {
    // Fetch from network and cache
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    console.warn('❌ Static asset request failed:', error)
    return new Response('Asset not available', { status: 404 })
  }
}

// Handle navigation requests (Network First with offline fallback)
async function handleNavigationRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      return networkResponse
    }
  } catch (error) {
    console.warn('🌐 Navigation request failed, trying cache:', error)
  }

  // Fallback to cached version
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    console.log('📦 Serving page from cache:', request.url)
    return cachedResponse
  }

  // Return offline page
  const offlineResponse = await caches.match('/offline.html')
  if (offlineResponse) {
    return offlineResponse
  }

  // Ultimate fallback
  return new Response(
    `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>MyStocks - Offline</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #0A0A0A;
          color: #D4AF37;
          text-align: center;
          padding: 50px;
          margin: 0;
        }
        .container {
          max-width: 600px;
          margin: 0 auto;
        }
        h1 { color: #D4AF37; margin-bottom: 30px; }
        p { font-size: 18px; line-height: 1.6; }
        .retry-btn {
          background: #D4AF37;
          color: #0A0A0A;
          border: none;
          padding: 12px 24px;
          border-radius: 4px;
          font-size: 16px;
          cursor: pointer;
          margin-top: 20px;
        }
        .retry-btn:hover { opacity: 0.9; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🔌 Offline Mode</h1>
        <p>You are currently offline. MyStocks is not available at the moment.</p>
        <p>Please check your internet connection and try again.</p>
        <button class="retry-btn" onclick="window.location.reload()">Retry Connection</button>
      </div>
    </body>
    </html>
    `,
    {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    }
  )
}

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag)

  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync())
  } else if (event.tag === 'market-data-sync') {
    event.waitUntil(syncMarketData())
  } else if (event.tag === 'user-preferences-sync') {
    event.waitUntil(syncUserPreferences())
  }
})

// Enhanced background sync with queuing system
class BackgroundSyncQueue {
  constructor() {
    this.queue = []
    this.isProcessing = false
  }

  async add(request) {
    this.queue.push({
      ...request,
      id: Date.now() + Math.random(),
      timestamp: Date.now(),
      retries: 0
    })

    // Auto-trigger sync if not already processing
    if (!this.isProcessing) {
      this.processQueue()
    }
  }

  async processQueue() {
    if (this.isProcessing || this.queue.length === 0) return

    this.isProcessing = true
    console.log(`🔄 Processing ${this.queue.length} queued requests`)

    while (this.queue.length > 0) {
      const request = this.queue.shift()

      try {
        const response = await fetch(request.url, {
          method: request.method || 'GET',
          headers: request.headers || {},
          body: request.body
        })

        if (response.ok) {
          console.log('✅ Background sync success:', request.url)
        } else {
          throw new Error(`HTTP ${response.status}`)
        }
      } catch (error) {
        console.warn('❌ Background sync failed:', request.url, error)

        // Retry logic
        if (request.retries < 3) {
          request.retries++
          this.queue.push(request)
          await new Promise(resolve => setTimeout(resolve, 5000 * request.retries)) // Exponential backoff
        } else {
          console.error('🚫 Max retries exceeded for:', request.url)
        }
      }
    }

    this.isProcessing = false
    console.log('✅ Background sync queue processed')
  }
}

const syncQueue = new BackgroundSyncQueue()

// Push notifications (for future market alerts)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json()
    const options = {
      body: data.body,
      icon: '/icons/icon-192.png',
      badge: '/icons/icon-72.png',
      data: data.url || '/',
      requireInteraction: true,
      silent: false
    }

    event.waitUntil(
      self.registration.showNotification(data.title || 'MyStocks Alert', options)
    )
  }
})

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  const url = event.notification.data || '/'

  event.waitUntil(
    clients.openWindow(url)
  )
})

// Utility functions
function isStaticAsset(request) {
  const url = new URL(request.url)
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2']
  return staticExtensions.some(ext => url.pathname.endsWith(ext))
}

async function doBackgroundSync() {
  console.log('🔄 Performing background sync...')

  // Get pending requests from IndexedDB or similar
  // For now, this is a placeholder for future implementation
  // This would typically sync failed API requests

  console.log('✅ Background sync completed')
}

// Enhanced cache versioning and cleanup system
class CacheManager {
  constructor() {
    this.versions = {
      [CACHE_NAME]: '1.0.0',
      [API_CACHE_NAME]: '1.0.0',
      [FONT_CACHE_NAME]: '1.0.0'
    }
    this.maxEntries = {
      [CACHE_NAME]: 200,      // Static assets
      [API_CACHE_NAME]: 100,  // API responses
      [FONT_CACHE_NAME]: 20   // Font files
    }
    this.expirationTimes = {
      [CACHE_NAME]: 24 * 60 * 60 * 1000,      // 24 hours
      [API_CACHE_NAME]: 5 * 60 * 1000,        // 5 minutes
      [FONT_CACHE_NAME]: 365 * 24 * 60 * 60 * 1000  // 1 year
    }
  }

  async cleanup() {
    try {
      const cacheNames = await caches.keys()

      for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName)
        const keys = await cache.keys()
        const maxEntries = this.maxEntries[cacheName] || 50
        const expirationTime = this.expirationTimes[cacheName] || 60 * 60 * 1000 // 1 hour

        console.log(`🧹 Cleaning cache ${cacheName}: ${keys.length} entries`)

        // Remove expired entries
        const now = Date.now()
        const expiredEntries = []

        for (const request of keys) {
          try {
            const response = await cache.match(request)
            if (response) {
              const dateHeader = response.headers.get('date') ||
                               response.headers.get('last-modified')
              if (dateHeader) {
                const entryTime = new Date(dateHeader).getTime()
                if (now - entryTime > expirationTime) {
                  expiredEntries.push(request)
                }
              }
            }
          } catch (error) {
            // If we can't check the entry, consider it for removal if over limit
            expiredEntries.push(request)
          }
        }

        // Remove expired entries
        if (expiredEntries.length > 0) {
          console.log(`🗑️ Removing ${expiredEntries.length} expired entries from ${cacheName}`)
          await Promise.all(
            expiredEntries.map(request => cache.delete(request))
          )
        }

        // If still over limit, remove oldest entries (LRU strategy)
        const remainingKeys = await cache.keys()
        if (remainingKeys.length > maxEntries) {
          const entriesToDelete = remainingKeys
            .sort((a, b) => {
              // Sort by URL to provide some deterministic ordering
              // In a real implementation, you'd want timestamps
              return a.url.localeCompare(b.url)
            })
            .slice(0, remainingKeys.length - maxEntries)

          console.log(`🗑️ Removing ${entriesToDelete.length} oldest entries from ${cacheName}`)
          await Promise.all(
            entriesToDelete.map(request => cache.delete(request))
          )
        }

        const finalCount = (await cache.keys()).length
        console.log(`✅ Cache ${cacheName} cleaned: ${finalCount} entries remaining`)
      }
    } catch (error) {
      console.warn('⚠️ Cache cleanup failed:', error)
    }
  }

  async getStats() {
    const stats = {}
    const cacheNames = await caches.keys()

    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName)
      const keys = await cache.keys()
      stats[cacheName] = {
        entries: keys.length,
        size: await this.estimateSize(cache, keys),
        version: this.versions[cacheName] || 'unknown'
      }
    }

    return stats
  }

  async estimateSize(cache, keys) {
    // Rough estimation - in a real implementation you'd calculate actual sizes
    let totalSize = 0
    for (const request of keys.slice(0, 10)) { // Sample first 10 entries
      try {
        const response = await cache.match(request)
        if (response) {
          const contentLength = response.headers.get('content-length')
          if (contentLength) {
            totalSize += parseInt(contentLength, 10)
          } else {
            totalSize += 1024 // Rough estimate for responses without size header
          }
        }
      } catch (error) {
        totalSize += 512 // Fallback estimate
      }
    }

    // Extrapolate for all entries
    return Math.round((totalSize / Math.min(10, keys.length)) * keys.length)
  }
}

const cacheManager = new CacheManager()

// Periodic cache cleanup (run every hour)
setInterval(() => {
  cacheManager.cleanup()
}, 60 * 60 * 1000) // Every hour

// Immediate cleanup on activation
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      // ... existing activation logic ...
      cacheManager.cleanup() // Initial cleanup
    ])
  )
})