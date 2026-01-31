// web/frontend/src/api/mockApiClient.ts

import { UnifiedResponse } from './apiClient';

// A simple delay function to simulate network latency
const simulateNetworkDelay = (min = 100, max = 500) =>
  new Promise((resolve) => setTimeout(resolve, Math.random() * (max - min) + min));

// Generic mock data for demonstration
const genericMockData = {
  success: true,
  code: 200,
  message: 'Mock data fetched successfully',
  data: {},
  timestamp: new Date().toISOString(),
  request_id: 'mock-req-123',
  errors: null,
};

export const mockApiClient = {
  async get<T = UnifiedResponse>(url: string, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] GET request to ${url} with config:`, config);
    // In a real scenario, you'd have specific mock data based on the URL
    // For now, return generic mock data
    return { ...genericMockData, data: { url, method: 'GET', ...config?.params } } as T;
  },

  async post<T = UnifiedResponse>(url: string, data?: any, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] POST request to ${url} with data:`, data, 'and config:', config);
    return { ...genericMockData, data: { url, method: 'POST', requestData: data, ...config?.params } } as T;
  },

  async put<T = UnifiedResponse>(url: string, data?: any, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] PUT request to ${url} with data:`, data, 'and config:', config);
    return { ...genericMockData, data: { url, method: 'PUT', requestData: data, ...config?.params } } as T;
  },

  async patch<T = UnifiedResponse>(url: string, data?: any, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] PATCH request to ${url} with data:`, data, 'and config:', config);
    return { ...genericMockData, data: { url, method: 'PATCH', requestData: data, ...config?.params } } as T;
  },

  async delete<T = UnifiedResponse>(url: string, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] DELETE request to ${url} with config:`, config);
    return { ...genericMockData, data: { url, method: 'DELETE', ...config?.params } } as T;
  },
};
