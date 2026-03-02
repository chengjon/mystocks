import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { apiClient } from '@/api/apiClient';
import type { UnifiedResponse } from '@/api/types/common';

/**
 * useArtDecoApi Composable
 * 
 * A specialized API wrapper for ArtDeco components that provides:
 * 1. Standardized loading and error states.
 * 2. Automated error notifications with ArtDeco styling.
 * 3. Tracing integration (request_id).
 * 4. Performance logging for slow frontend responses.
 */
export function useArtDecoApi() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastRequestId = ref<string>('');
  const lastProcessTime = ref<string>('');

  /**
   * Execute an API call with standardized ArtDeco handling
   * 
   * @param apiCall A function that returns a Promise of UnifiedResponse<T>
   * @param options Configuration for message display and error handling
   */
  async function exec<T>(
    apiCall: () => Promise<UnifiedResponse<T>>,
    options: {
      silent?: boolean;
      successMsg?: string;
      errorMsg?: string;
      showProcessTime?: boolean;
    } = {}
  ): Promise<T | null> {
    loading.value = true;
    error.value = null;
    
    const startTime = performance.now();

    try {
      const response = await apiCall();
      
      // Update tracing info
      lastRequestId.value = response.request_id || '';
      lastProcessTime.value = response.process_time || '';
      
      const endTime = performance.now();
      const frontendDuration = endTime - startTime;

      // Performance check: Log if frontend + backend > 1s or backend > 300ms
      if (frontendDuration > 1000 || (lastProcessTime.value && parseFloat(lastProcessTime.value) > 300)) {
        console.warn(`[ArtDeco Performance] Slow API call detected:`, {
          request_id: lastRequestId.value,
          backend_ms: lastProcessTime.value,
          total_frontend_ms: frontendDuration.toFixed(2),
        });
      }

      if (response.success) {
        if (options.successMsg && !options.silent) {
          ElMessage({
            message: options.successMsg,
            type: 'success',
            customClass: 'artdeco-message-success',
          });
        }
        return response.data;
      } else {
        const msg = options.errorMsg || response.message || '操作失败';
        error.value = msg;
        
        if (!options.silent) {
          ElMessage({
            message: `${msg} (ID: ${lastRequestId.value})`,
            type: 'error',
            customClass: 'artdeco-message-error',
            duration: 5000,
          });
        }
        return null;
      }
    } catch (err: unknown) {
      const msg = options.errorMsg || (err instanceof Error ? err.message : '网络请求异常');
      error.value = msg;
      
      if (!options.silent) {
        ElMessage({
          message: msg,
          type: 'error',
          customClass: 'artdeco-message-error',
        });
      }
      return null;
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    lastRequestId,
    lastProcessTime,
    exec,
  };
}
