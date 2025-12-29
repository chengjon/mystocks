/**
 * API客户端基础类
 * 封装axios，提供统一的HTTP请求接口
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ElMessage } from 'element-plus';

/**
 * API响应格式
 */
export interface APIResponse<T = any> {
  code: string;
  message: string;
  data: T;
  request_id?: string;
}

/**
 * API错误响应
 */
export interface APIErrorResponse {
  code: string;
  message: string;
  data: null;
  request_id?: string;
}

/**
 * 请求配置
 */
export interface RequestConfig extends AxiosRequestConfig {
  showError?: boolean; // 是否显示错误提示
  showLoading?: boolean; // 是否显示加载状态
}

/**
 * API客户端类
 */
export class APIClient {
  private client: AxiosInstance;
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * 设置拦截器
   */
  private setupInterceptors(): void {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        // 添加认证token
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }

        // 添加request_id
        config.headers['X-Request-ID'] = this.generateRequestId();

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        return this.handleError(error);
      }
    );
  }

  /**
   * 生成请求ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  }

  /**
   * 统一错误处理
   */
  private handleError(error: AxiosError): Promise<never> {
    let errorMessage = '请求失败';

    if (error.response) {
      // 服务器返回错误
      const data = error.response.data as APIErrorResponse;
      errorMessage = data.message || errorMessage;
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络错误，请检查网络连接';
    } else {
      // 请求配置出错
      errorMessage = error.message || '请求配置错误';
    }

    // 显示错误提示
    ElMessage.error(errorMessage);

    return Promise.reject(error);
  }

  /**
   * 设置认证token
   */
  public setToken(token: string): void {
    this.token = token;
  }

  /**
   * 清除token
   */
  public clearToken(): void {
    this.token = null;
  }

  /**
   * GET请求
   */
  public async get<T = any>(
    url: string,
    params?: any,
    config?: RequestConfig
  ): Promise<APIResponse<T>> {
    const response = await this.client.get<APIResponse<T>>(url, {
      params,
      ...config,
    });
    return response.data;
  }

  /**
   * POST请求
   */
  public async post<T = any>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<APIResponse<T>> {
    const response = await this.client.post<APIResponse<T>>(url, data, config);
    return response.data;
  }

  /**
   * PUT请求
   */
  public async put<T = any>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<APIResponse<T>> {
    const response = await this.client.put<APIResponse<T>>(url, data, config);
    return response.data;
  }

  /**
   * PATCH请求
   */
  public async patch<T = any>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<APIResponse<T>> {
    const response = await this.client.patch<APIResponse<T>>(url, data, config);
    return response.data;
  }

  /**
   * DELETE请求
   */
  public async delete<T = any>(
    url: string,
    config?: RequestConfig
  ): Promise<APIResponse<T>> {
    const response = await this.client.delete<APIResponse<T>>(url, config);
    return response.data;
  }

  /**
   * 文件上传
   */
  public async upload<T = any>(
    url: string,
    file: File,
    onProgress?: (percent: number) => void,
    config?: RequestConfig
  ): Promise<APIResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<APIResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
      ...config,
    });

    return response.data;
  }

  /**
   * 文件下载
   */
  public async download(
    url: string,
    filename: string,
    config?: RequestConfig
  ): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
      ...config,
    });

    // 创建下载链接
    const blob = new Blob([response.data]);
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();

    // 清理
    window.URL.revokeObjectURL(link.href);
  }
}

// 创建全局API客户端实例
export const apiClient = new APIClient();

/**
 * 设置认证token
 */
export function setAuthToken(token: string): void {
  apiClient.setToken(token);
  // 保存到localStorage
  localStorage.setItem('auth_token', token);
}

/**
 * 获取认证token
 */
export function getAuthToken(): string | null {
  return localStorage.getItem('auth_token');
}

/**
 * 清除认证token
 */
export function clearAuthToken(): void {
  apiClient.clearToken();
  localStorage.removeItem('auth_token');
}

/**
 * 初始化认证token (从localStorage恢复)
 */
export function initAuthToken(): void {
  const token = getAuthToken();
  if (token) {
    setAuthToken(token);
  }
}
