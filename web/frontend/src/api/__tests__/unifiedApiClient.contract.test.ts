import { describe, it, expect } from 'vitest'
import { apiClient } from '../apiClient'
import unifiedApiClient, {
  _unifiedApiClient,
  ContractValidationError,
  createCacheConfig,
  createLoadingConfig,
  DEFAULT_RETRY_CONFIG,
  getUserFriendlyErrorMessage,
} from '../unifiedApiClient'

describe('unifiedApiClient legacy wrapper contract', () => {
  it('re-exports the current apiClient instance', () => {
    expect(unifiedApiClient).toBe(apiClient)
    expect(_unifiedApiClient).toBe(apiClient)
  })

  it('creates lightweight loading and cache configs', () => {
    expect(createLoadingConfig()).toEqual({ show: true })
    expect(createLoadingConfig(false)).toEqual({ show: false })
    expect(createCacheConfig()).toEqual({ use: false })
    expect(createCacheConfig(true)).toEqual({ use: true })
  })

  it('keeps the default retry config stable', () => {
    expect(DEFAULT_RETRY_CONFIG).toEqual({ retries: 0 })
  })

  it('wraps contract validation errors with the expected name', () => {
    const error = new ContractValidationError('invalid contract')

    expect(error).toBeInstanceOf(Error)
    expect(error.name).toBe('ContractValidationError')
    expect(error.message).toBe('invalid contract')
  })

  it('returns a friendly message when the error object contains one', () => {
    expect(getUserFriendlyErrorMessage({ message: '请求超时' })).toBe('请求超时')
  })

  it('falls back to a generic message for unknown errors', () => {
    expect(getUserFriendlyErrorMessage(null)).toBe('请求失败，请检查网络')
    expect(getUserFriendlyErrorMessage({})).toBe('请求失败，请检查网络')
  })
})
