import { apiClient } from '@/api/apiClient.ts';

class HttpClient {
  constructor() {
    this.csrfToken = null;
  }

  // Backward-compatible getter: prefer persisted token if available.
  getCsrfToken() {
    return localStorage.getItem('csrf_token') || this.csrfToken || null;
  }

  async request(path, options = {}) {
    const method = (options.method || 'GET').toLowerCase();

    try {
      let response;
      const config = { ...options };

      let requestData = config.body;
      if (typeof requestData === 'string' && config.headers?.['Content-Type']?.includes('application/json')) {
        try {
          requestData = JSON.parse(requestData);
        } catch (e) {
          console.error('Failed to parse request body to JSON:', e);
        }
      }
      delete config.body;

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
          if (requestData !== undefined) {
            config.data = requestData;
          }
          response = await apiClient.delete(path, config);
          break;
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }

      if (!response.success) {
        const error = new Error(response.message || 'Request failed');
        error.code = response.code;
        error.data = response.data;
        error.request_id = response.request_id;
        throw error;
      }

      return response;
    } catch (error) {
      console.error(`❌ Request failed [${method.toUpperCase()} ${path}]:`, error);
      throw error;
    }
  }

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

export const httpClient = new HttpClient();

// Compatibility stub: security bootstrap now handled by apiClient interceptors.
export async function initializeSecurity() {
  return true;
}

export default httpClient;

