/**
 * IndexedDB Manager for MyStocks
 * Client-side database for offline data storage and caching
 */

export interface MarketData {
  symbol: string;
  timestamp: number;
  price: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  close: number;
}

export interface TechnicalIndicator {
  symbol: string;
  indicator: string;
  params: Record<string, any>;
  values: number[];
  timestamp: number;
}

export interface UserPreferences {
  userId: string;
  settings: Record<string, any>;
  timestamp: number;
}

export interface CachedData<T> {
  key: string;
  data: T;
  timestamp: number;
  expiresAt?: number;
}

export class IndexedDBManager {
  private db: IDBDatabase | null = null;
  private readonly dbName = 'MyStocksDB';
  private readonly dbVersion = 1;
  private isInitialized = false;

  constructor() {
    this.init();
  }

  /**
   * Initialize IndexedDB database
   */
  async init(): Promise<void> {
    if (this.isInitialized) return;

    return new Promise((resolve, reject) => {
      const request = window.indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('IndexedDB initialization failed:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        this.isInitialized = true;
        console.log('✅ IndexedDB initialized successfully');
        resolve();
      };

      request.onupgradeneeded = (event: Event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object stores
        if (!db.objectStoreNames.contains('market_data')) {
          const marketStore = db.createObjectStore('market_data', { keyPath: 'symbol' });
          marketStore.createIndex('timestamp', 'timestamp', { unique: false });
          marketStore.createIndex('symbol_timestamp', ['symbol', 'timestamp'], { unique: false });
        }

        if (!db.objectStoreNames.contains('technical_indicators')) {
          const indicatorStore = db.createObjectStore('technical_indicators', { keyPath: ['symbol', 'indicator', 'timestamp'] });
          indicatorStore.createIndex('symbol', 'symbol', { unique: false });
          indicatorStore.createIndex('indicator', 'indicator', { unique: false });
        }

        if (!db.objectStoreNames.contains('user_preferences')) {
          db.createObjectStore('user_preferences', { keyPath: 'userId' });
        }

        if (!db.objectStoreNames.contains('api_cache')) {
          const cacheStore = db.createObjectStore('api_cache', { keyPath: 'key' });
          cacheStore.createIndex('expiresAt', 'expiresAt', { unique: false });
        }

        console.log('📦 IndexedDB schema created/updated');
      };
    });
  }

  /**
   * Ensure database is initialized
   */
  private async ensureInitialized(): Promise<void> {
    if (!this.isInitialized || !this.db) {
      await this.init();
    }
  }

  // ============ Market Data Operations ============

  /**
   * Save market data for a symbol
   */
  async saveMarketData(data: MarketData): Promise<void> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['market_data'], 'readwrite');
      const store = transaction.objectStore('market_data');

      const request = store.put(data);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get market data for a symbol
   */
  async getMarketData(symbol: string): Promise<MarketData | null> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['market_data'], 'readonly');
      const store = transaction.objectStore('market_data');

      const request = store.get(symbol);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all market data
   */
  async getAllMarketData(): Promise<MarketData[]> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['market_data'], 'readonly');
      const store = transaction.objectStore('market_data');

      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Delete market data for a symbol
   */
  async deleteMarketData(symbol: string): Promise<void> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['market_data'], 'readwrite');
      const store = transaction.objectStore('market_data');

      const request = store.delete(symbol);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // ============ Technical Indicators Operations ============

  /**
   * Save technical indicator data
   */
  async saveTechnicalIndicator(data: TechnicalIndicator): Promise<void> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['technical_indicators'], 'readwrite');
      const store = transaction.objectStore('technical_indicators');

      const request = store.put(data);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get technical indicator data
   */
  async getTechnicalIndicator(symbol: string, indicator: string, timestamp: number): Promise<TechnicalIndicator | null> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['technical_indicators'], 'readonly');
      const store = transaction.objectStore('technical_indicators');

      const request = store.get([symbol, indicator, timestamp]);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all technical indicators for a symbol
   */
  async getTechnicalIndicatorsForSymbol(symbol: string): Promise<TechnicalIndicator[]> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['technical_indicators'], 'readonly');
      const store = transaction.objectStore('technical_indicators');
      const index = store.index('symbol');

      const request = index.getAll(symbol);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // ============ User Preferences Operations ============

  /**
   * Save user preferences
   */
  async saveUserPreferences(prefs: UserPreferences): Promise<void> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['user_preferences'], 'readwrite');
      const store = transaction.objectStore('user_preferences');

      const request = store.put(prefs);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get user preferences
   */
  async getUserPreferences(userId: string): Promise<UserPreferences | null> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['user_preferences'], 'readonly');
      const store = transaction.objectStore('user_preferences');

      const request = store.get(userId);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  // ============ API Cache Operations ============

  /**
   * Cache API response
   */
  async setCache<T>(key: string, data: T, ttlSeconds: number = 300): Promise<void> {
    await this.ensureInitialized();

    const cacheData: CachedData<T> = {
      key,
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + (ttlSeconds * 1000)
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['api_cache'], 'readwrite');
      const store = transaction.objectStore('api_cache');

      const request = store.put(cacheData);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get cached API response
   */
  async getCache<T>(key: string): Promise<T | null> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['api_cache'], 'readonly');
      const store = transaction.objectStore('api_cache');

      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        if (!result) {
          resolve(null);
          return;
        }

        // Check if expired
        if (result.expiresAt && Date.now() > result.expiresAt) {
          // Auto-clean expired cache
          this.deleteCache(key).catch(console.warn);
          resolve(null);
          return;
        }

        resolve(result.data);
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Delete cached API response
   */
  async deleteCache(key: string): Promise<void> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['api_cache'], 'readwrite');
      const store = transaction.objectStore('api_cache');

      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clear all expired cache entries
   */
  async clearExpiredCache(): Promise<number> {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['api_cache'], 'readwrite');
      const store = transaction.objectStore('api_cache');
      const index = store.index('expiresAt');

      const now = Date.now();
      const range = IDBKeyRange.upperBound(now);
      const request = index.openCursor(range);

      let deletedCount = 0;

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          cursor.delete();
          deletedCount++;
          cursor.continue();
        } else {
          resolve(deletedCount);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  // ============ Utility Operations ============

  /**
   * Clear all data from all stores
   */
  async clearAllData(): Promise<void> {
    await this.ensureInitialized();

    const storeNames = ['market_data', 'technical_indicators', 'user_preferences', 'api_cache'];

    const promises = storeNames.map(storeName => {
      return new Promise<void>((resolve, reject) => {
        const transaction = this.db!.transaction([storeName], 'readwrite');
        const store = transaction.objectStore(storeName);

        const request = store.clear();

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    });

    await Promise.all(promises);
    console.log('🗑️ All IndexedDB data cleared');
  }

  /**
   * Get database statistics
   */
  async getStats(): Promise<Record<string, number>> {
    await this.ensureInitialized();

    const stats: Record<string, number> = {};
    const storeNames = ['market_data', 'technical_indicators', 'user_preferences', 'api_cache'];

    for (const storeName of storeNames) {
      await new Promise<void>((resolve, reject) => {
        const transaction = this.db!.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);

        const request = store.count();

        request.onsuccess = () => {
          stats[storeName] = request.result;
          resolve();
        };

        request.onerror = () => reject(request.error);
      });
    }

    return stats;
  }

  /**
   * Close database connection
   */
  close(): void {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.isInitialized = false;
      console.log('🔒 IndexedDB connection closed');
    }
  }
}

// Export singleton instance with clear name
export const indexedDBManager = new IndexedDBManager();

// Also export with legacy name for backward compatibility
export { indexedDBManager as indexedDB }