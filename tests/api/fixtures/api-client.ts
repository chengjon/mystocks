/**
 * API 测试客户端和工具函数
 */

/**
 * API 测试配置
 */
export const API_CONFIG = {
  baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
};

/**
 * API 错误码
 */
export const ERROR_CODES = {
  SUCCESS: 200,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_ERROR: 500,
  VALIDATION_ERROR: 422,
};

/**
 * API 响应结构
 */
export interface APIResponse<T = any> {
  success?: boolean;
  code?: number;
  message?: string;
  data: T;
  timestamp?: string;
  request_id?: string;
}

/**
 * API 测试客户端类
 */
export class APITestClient {
  baseURL: string;
  token: string | null;

  constructor(baseURL: string = API_CONFIG.baseURL) {
    this.baseURL = baseURL;
    this.token = null;
  }

  setToken(token: string) {
    this.token = token;
  }

  getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request<T = any>(
    method: string,
    path: string,
    data?: any,
    params?: Record<string, any>
  ): Promise<APIResponse<T>> {
    const url = new URL(path, this.baseURL);

    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== undefined) {
          url.searchParams.append(key, String(params[key]));
        }
      });
    }

    const response = await fetch(url.toString(), {
      method,
      headers: this.getHeaders(),
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(
        `API request failed: ${response.status} ${response.statusText}\n${error}`
      );
    }

    return response.json();
  }

  async get<T = any>(
    path: string,
    params?: Record<string, any>
  ): Promise<APIResponse<T>> {
    return this.request<T>('GET', path, undefined, params);
  }

  async post<T = any>(
    path: string,
    data?: any
  ): Promise<APIResponse<T>> {
    return this.request<T>('POST', path, data);
  }

  async put<T = any>(
    path: string,
    data?: any
  ): Promise<APIResponse<T>> {
    return this.request<T>('PUT', path, data);
  }

  async delete<T = any>(
    path: string
  ): Promise<APIResponse<T>> {
    return this.request<T>('DELETE', path);
  }

  async login(username: string, password: string) {
    // Login endpoint uses OAuth2PasswordRequestForm - send as form data
    const response = await fetch(new URL('/api/v1/auth/login', this.baseURL).toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
    });

    const data = await response.json();

    if (data.code === 200 && data.data?.token) {
      this.setToken(data.data.token);
    } else if (data.code === 200 && data.data?.access_token) {
      this.setToken(data.data.access_token);
    } else if (data.success === true && data.data?.token) {
      this.setToken(data.data.token);
    } else if (data.success === true && data.data?.access_token) {
      this.setToken(data.data.access_token);
    }

    return data;
  }
}

/**
 * 测试数据验证函数
 */

export function validateAPIResponse<T>(
  response: APIResponse<T>,
  expectedCode: number = 200
): T {
  // Handle both formats: {code: 200} and {success: true}
  const isSuccess = response.success === true || response.code === expectedCode;

  if (!isSuccess) {
    const actualCode = response.code;
    const actualSuccess = response.success;
    throw new Error(
      `Expected code ${expectedCode}, got code=${actualCode}, success=${actualSuccess}: ${response.message || 'No message'}`
    );
  }

  return response.data;
}

export function validateRequiredFields<T>(
  data: T,
  requiredFields: (keyof T)[]
): void {
  for (const field of requiredFields) {
    if (!(field in data) || data[field] === undefined || data[field] === null) {
      throw new Error(`Missing required field: ${String(field)}`);
    }
  }
}

export function validateFieldType<T>(
  data: T,
  field: keyof T,
  expectedType: string
): void {
  const value = data[field];

  if (value === undefined || value === null) {
    return;
  }

  const actualType = Array.isArray(value) ? 'array' : typeof value;

  if (actualType !== expectedType) {
    throw new Error(
      `Field ${String(field)} expected type ${expectedType}, got ${actualType}`
    );
  }
}

/**
 * 测试数据
 */

export const TEST_DATA = {
  auth: {
    admin: {
      username: 'admin',
      password: 'admin123',
    },
    user: {
      username: 'user',
      password: 'user123',
    },
  },

  stocks: {
    maotai: '600519',
    wuliangye: '000858',
    pingan: '000001',
    zhongshang: '601012',
    ningde: '300750',
  },

  klineIntervals: ['1m', '5m', '15m', '1h', '1d', '1w', '1M'],

  adjustTypes: ['qfq', 'hfq', 'none'],
};

/**
 * 性能基准验证
 */

export function validateResponseTime(
  startTime: number,
  maxTime: number
): number {
  const duration = Date.now() - startTime;

  if (duration > maxTime) {
    throw new Error(
      `Response time ${duration}ms exceeds maximum ${maxTime}ms`
    );
  }

  return duration;
}

export const PERFORMANCE_BENCHMARKS = {
  auth: 1000,
  market: 800,
  stock: 1200,
  strategy: 1500,
  wencai: 2000,
  technical: 1500,
  system: 500,
};

export function validatePerformanceByModule(
  startTime: number,
  module: keyof typeof PERFORMANCE_BENCHMARKS
): number {
  return validateResponseTime(startTime, PERFORMANCE_BENCHMARKS[module]);
}
