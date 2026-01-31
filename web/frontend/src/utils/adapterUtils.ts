/**
 * Adapter Utilities
 *
 * Simple factory for creating data transformation and validation adapters
 */

export interface AdapterConfig<T = any> {
  transform: (data: any) => T
  validate?: (data: any) => boolean
}

export interface Adapter<T = any> {
  transform: (data: any) => T
  validate: (data: any) => boolean
}

/**
 * Create a data adapter with transformation and optional validation
 */
export function createAdapter<T = any>(config: AdapterConfig<T>): Adapter<T> {
  return {
    transform: config.transform,
    validate: config.validate || (() => true)
  }
}

export default createAdapter
