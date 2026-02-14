/**
 * Adapter Utilities
 *
 * Simple factory for creating data transformation and validation adapters
 */

export interface AdapterConfig<T = unknown> {
  transform: (data: unknown) => T
  validate?: (data: unknown) => boolean
}

export interface Adapter<T = unknown> {
  transform: (data: unknown) => T
  validate: (data: unknown) => boolean
}

/**
 * Create a data adapter with transformation and optional validation
 */
export function createAdapter<T = unknown>(config: AdapterConfig<T>): Adapter<T> {
  return {
    transform: config.transform,
    validate: config.validate || (() => true)
  }
}

export default createAdapter
