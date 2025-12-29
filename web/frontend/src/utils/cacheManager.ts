const CACHE_PREFIX = 'kline_cache_';
const CACHE_EXPIRY = 60 * 60 * 1000;

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

class CacheManager {
  static get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(CACHE_PREFIX + key);
      if (!item) return null;

      const entry: CacheEntry<T> = JSON.parse(item);
      const now = Date.now();

      if (now - entry.timestamp > CACHE_EXPIRY) {
        localStorage.removeItem(CACHE_PREFIX + key);
        return null;
      }

      return entry.data;
    } catch {
      return null;
    }
  }

  static set<T>(key: string, data: T): void {
    try {
      const entry: CacheEntry<T> = {
        data,
        timestamp: Date.now()
      };
      localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(entry));
    } catch (e) {
      console.warn('Cache set failed:', e);
    }
  }

  static remove(key: string): void {
    localStorage.removeItem(CACHE_PREFIX + key);
  }

  static clear(): void {
    const keys = Object.keys(localStorage).filter(k => k.startsWith(CACHE_PREFIX));
    keys.forEach(k => localStorage.removeItem(k));
  }

  static generateKey(symbol: string, interval: string, adjust: string, startDate?: string, endDate?: string): string {
    return `${symbol}_${interval}_${adjust}_${startDate || ''}_${endDate || ''}`;
  }
}

export const klineCache = {
  get: CacheManager.get,
  set: CacheManager.set,
  remove: CacheManager.remove,
  clear: CacheManager.clear,
  generateKey: CacheManager.generateKey
};

export default klineCache;
