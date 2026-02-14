/**
 * Unified API Client (Legacy Wrapper)
 * Refactored 2026-02-14
 * 
 * This file now acts as a bridge to the new apiClient.ts 
 * to ensure backward compatibility without circular dependencies.
 */

import { apiClient } from './apiClient'

export const unifiedApiClient = apiClient;
export const _unifiedApiClient = apiClient;

export const createLoadingConfig = (show = true) => ({ show });
export const createCacheConfig = (use = false) => ({ use });
export const DEFAULT_RETRY_CONFIG = { retries: 0 };

export class ContractValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ContractValidationError';
  }
}

export const getUserFriendlyErrorMessage = (error: any) => {
  return error?.message || '请求失败，请检查网络';
};

export default unifiedApiClient;
