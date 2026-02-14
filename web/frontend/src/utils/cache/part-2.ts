
/**
 * Cache Manager - Wrapper class for LRUCache with simplified API
 */
export class CacheManager<T = unknown> {
  private cache: LRUCache<T>;
  private name: string;

  constructor(name: string, options?: CacheOptions, config?: Partial<CacheConfig>) {
    this.name = name;
    this.cache = getCache<T>(name, options, config);
  }

  /**
   * Get value from cache (with optional type parameter for convenience)
   */
  get<K = T>(key: string): K | undefined {
    return this.cache.get(key) as unknown as K | undefined;
  }

  /**
   * Set value in cache
   */
  set<K = T>(key: string, value: K, options?: CacheOptions): void {
    this.cache.set(key, value as unknown as T, options);
  }

  /**
   * Check if key exists
   */
  has(key: string): boolean {
    return this.cache.has(key);
  }

  /**
   * Delete value from cache
   */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /**
   * Clear all values
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache size
   */
  get size(): number {
    return this.cache.size;
  }

  /**
   * Get all keys
   */
  keys(): string[] {
    return this.cache.keys();
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    return this.cache.getStats();
  }

  /**
   * Invalidate by pattern (simple substring match)
   */
  invalidateByPattern(pattern: string): number {
    let count = 0;
    for (const key of this.keys()) {
      if (key.includes(pattern)) {
        this.delete(key);
        count++;
      }
    }
    return count;
  }
}

export default LRUCache

