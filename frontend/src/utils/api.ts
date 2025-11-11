
import { toast } from 'react-hot-toast';

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api';

// 存储logout方法的引用，用于在身份验证失效时调用
let logoutHandler: (() => void) | null = null;

// 设置logout处理函数，由AuthProvider调用
export const setLogoutHandler = (handler: () => void) => {
  logoutHandler = handler;
};

// 创建一个API请求包装函数，处理身份验证失效的情况
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {},
  skipAuthErrorHandler = false
): Promise<Response> => {
  // 获取token
  const token = localStorage.getItem('token');

  // 设置默认headers
  const defaultHeaders: Record<string, string> = {
    ...(token && { Authorization: `Bearer ${token}` })
  };
  
  // 只有当body不是FormData时才设置Content-Type为application/json
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  // 合并headers
  const headers = {
    ...defaultHeaders,
    ...options.headers
  };

  // 构建完整URL
  const url = endpoint.startsWith('http') 
    ? endpoint 
    : `${API_BASE_URL}${endpoint}`;

  try {
    // 发送请求
    const response = await fetch(url, {
      ...options,
      headers
    });

    // 检查是否是身份验证错误
    if (response.status === 401 && !skipAuthErrorHandler) {
      // 显示身份失效提示
      toast.error('登录已过期，请重新登录');

      // 调用logout处理函数，如果存在的话
      if (logoutHandler) {
        logoutHandler();
      } else {
        // 如果没有设置logout处理函数，则清除本地存储
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }

      // 抛出错误，停止后续处理
      throw new Error('身份验证失效');
    }

    return response;
  } catch (error) {
    // 如果是身份验证错误，不再处理（已经在上面处理了）
    if (error instanceof Error && error.message === '身份验证失效') {
      throw error;
    }

    // 其他错误正常抛出
    throw error;
  }
};

// 便捷方法
export const apiGet = (endpoint: string, options: RequestInit = {}) => 
  apiRequest(endpoint, { method: 'GET', ...options });

export const apiPost = (endpoint: string, data?: any, options: RequestInit = {}, skipAuthErrorHandler = false) => 
  apiRequest(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
    ...options
  }, skipAuthErrorHandler);

export const apiPut = (endpoint: string, data?: any, options: RequestInit = {}) => 
  apiRequest(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
    ...options
  });

export const apiDelete = (endpoint: string, options: RequestInit = {}) => 
  apiRequest(endpoint, { method: 'DELETE', ...options });
