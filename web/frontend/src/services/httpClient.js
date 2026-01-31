import { apiClient } from '@/api/apiClient'; // Import the apiClient with mock/real switch

class HttpClient {
  constructor() {
    // No need for baseURL and CSRF token state here, apiClient handles it
    this.csrfToken = null; // Keep for getCsrfToken, but it will read from apiClient's internal state or localStorage
  }

  // Simplified getCsrfToken for backward compatibility, will rely on apiClient's interceptor
  getCsrfToken() {
    // In a real scenario, this should fetch from where apiClient stores it (e.g., localStorage or a central auth store)
    // For now, it's just a placeholder as apiClient's interceptors manage this.
    console.warn('HttpClient.getCsrfToken() is deprecated. Use apiClient.interceptors for CSRF handling.');
    return null; // apiClient handles CSRF token transparently
  }

  // No longer needed. apiClient's interceptors handle JWT/CSRF token.
  // async initializeCsrfToken() {
  //   console.warn('HttpClient.initializeCsrfToken() is deprecated. CSRF handling is now automatic via apiClient.');
  //   return true;
  // }

  // Simplified request method to use apiClient
  async request(path, options = {}) {
    const method = (options.method || 'GET').toLowerCase(); // apiClient methods are lowercase

    try {
      let response;
      const config = { ...options }; // Pass original options as config

      // Convert body to data for POST/PUT/PATCH if present
      let requestData = config.body;
      if (typeof requestData === 'string' && config.headers?.['Content-Type']?.includes('application/json')) {
        try {
          requestData = JSON.parse(requestData);
        } catch (e) {
          console.error('Failed to parse request body to JSON:', e);
          // Keep as string if parsing fails
        }
      }
      delete config.body; // remove body as apiClient expects 'data' for these methods

      switch (method) {
        case 'get':
          response = await apiClient.get(path, config);
          break;
        case 'post':
          response = await apiClient.post(path, requestData, config);
          break;
        case 'put':
          response = await apiClient.put(path, requestData, config);
          break;
        case 'patch':
          response = await apiClient.patch(path, requestData, config);
          break;
        case 'delete':
          response = await apiClient.delete(path, config);
          break;
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }

      // apiClient already returns UnifiedResponse. Check success.
      if (!response.success) {
        // Throw an error with the message from UnifiedResponse for error handling chain
        const error = new Error(response.message || 'Request failed');
        error.code = response.code;
        error.data = response.data;
        error.request_id = response.request_id;
        throw error;
      }

      return response; // Return the full UnifiedResponse
    } catch (error) {
      console.error(`❌ Request failed [${method.toUpperCase()} ${path}]:`, error);
      throw error;
    }
  }

  // These methods now simply call the general request method
  get(path, options = {}) {
    return this.request(path, { ...options, method: 'GET' });
  }

  post(path, data = {}, options = {}) {
    return this.request(path, { ...options, method: 'POST', body: data });
  }

  put(path, data = {}, options = {}) {
    return this.request(path, { ...options, method: 'PUT', body: data });
  }

  patch(path, data = {}, options = {}) {
    return this.request(path, { ...options, method: 'PATCH', body: data });
  }

  delete(path, options = {}) {
    return this.request(path, { ...options, method: 'DELETE' });
  }
}

// 创建全局HTTP客户端实例
export const httpClient = new HttpClient();

/**
 * SECURITY: initializeSecurity is no longer needed as apiClient handles CSRF/JWT.
 * Keeping a stub for compatibility if other modules call it.
 */
export async function initializeSecurity() {
  console.warn('🛡️ initializeSecurity is deprecated. CSRF/JWT handling is now automatic via apiClient.');
  return true; // Always return true for compatibility
}

export default httpClient;
