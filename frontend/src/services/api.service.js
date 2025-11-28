/**
 * Advanced API Service with Interceptors, Retry Logic, Error Handling
 * Industry-level implementation
 */

import axios from 'axios';
import { API_CONFIG } from '@/config/api.config';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Setup request and response interceptors
   */
  setupInterceptors() {
    // Request Interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add JWT token
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request timestamp
        config.metadata = { startTime: new Date() };

        // Log request in development
        if (import.meta.env.DEV) {
          console.log('🚀 API Request:', {
            method: config.method?.toUpperCase(),
            url: config.url,
            data: config.data,
          });
        }

        return config;
      },
      (error) => {
        console.error('❌ Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response Interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Calculate request duration
        const duration = new Date() - response.config.metadata.startTime;

        // Log response in development
        if (import.meta.env.DEV) {
          console.log('✅ API Response:', {
            url: response.config.url,
            status: response.status,
            duration: `${duration}ms`,
            data: response.data,
          });
        }

        return response.data;
      },
      async (error) => {
        return this.handleError(error);
      }
    );
  }

  /**
   * Advanced error handling with retry logic
   */
  async handleError(error) {
    const originalRequest = error.config;

    // Log error
    console.error('❌ API Error:', {
      url: originalRequest?.url,
      method: originalRequest?.method,
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
    });

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const newToken = await this.refreshToken();
        if (newToken) {
          this.setToken(newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return this.client(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        this.handleLogout();
        return Promise.reject(refreshError);
      }
    }

    // Handle network errors with retry
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
      if (!originalRequest._retryCount) {
        originalRequest._retryCount = 0;
      }

      if (originalRequest._retryCount < API_CONFIG.RETRY_ATTEMPTS) {
        originalRequest._retryCount++;
        
        console.log(`🔄 Retrying request (${originalRequest._retryCount}/${API_CONFIG.RETRY_ATTEMPTS})...`);
        
        // Wait before retry
        await this.sleep(API_CONFIG.RETRY_DELAY * originalRequest._retryCount);
        
        return this.client(originalRequest);
      }
    }

    // Format error response
    const formattedError = {
      message: error.response?.data?.message || error.message || 'An error occurred',
      status: error.response?.status,
      code: error.response?.data?.code,
      errors: error.response?.data?.errors,
      originalError: error,
    };

    return Promise.reject(formattedError);
  }

  /**
   * Refresh JWT token
   */
  async refreshToken() {
    try {
      const response = await axios.post(
        `${API_CONFIG.BASE_URL}/api/auth/refresh`,
        {},
        {
          headers: {
            Authorization: `Bearer ${this.getToken()}`,
          },
        }
      );
      return response.data.access_token;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Handle logout
   */
  handleLogout() {
    this.clearToken();
    this.clearUser();
    window.location.href = '/login';
  }

  /**
   * Token management
   */
  getToken() {
    return localStorage.getItem('access_token');
  }

  setToken(token) {
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    localStorage.removeItem('access_token');
  }

  /**
   * User management
   */
  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
  }

  clearUser() {
    localStorage.removeItem('user');
  }

  /**
   * Helper: Sleep function for retry delay
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * HTTP Methods
   */
  get(url, config = {}) {
    return this.client.get(url, config);
  }

  post(url, data, config = {}) {
    return this.client.post(url, data, config);
  }

  put(url, data, config = {}) {
    return this.client.put(url, data, config);
  }

  patch(url, data, config = {}) {
    return this.client.patch(url, data, config);
  }

  delete(url, config = {}) {
    return this.client.delete(url, config);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
