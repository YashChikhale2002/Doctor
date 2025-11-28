/**
 * API Configuration - Industry Standard
 * Centralized API config with environment variables
 */

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

export const ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    ME: '/api/auth/me',
    REFRESH: '/api/auth/refresh',
  },
  // Health
  HEALTH: {
    CHECK: '/api/health',
    STATS: '/api/stats',
    PING: '/api/ping',
  },
  // Facilities
  FACILITIES: {
    LIST: '/api/facilities',
    DETAIL: (id) => `/api/facilities/${id}`,
    CREATE: '/api/facilities',
    UPDATE: (id) => `/api/facilities/${id}`,
    DELETE: (id) => `/api/facilities/${id}`,
  },
  // Patients
  PATIENTS: {
    LIST: '/api/patients',
    DETAIL: (id) => `/api/patients/${id}`,
    CREATE: '/api/patients',
    UPDATE: (id) => `/api/patients/${id}`,
  },
  // Billing
  BILLING: {
    BILLS: '/api/billing/bills',
    BILL_DETAIL: (id) => `/api/billing/bills/${id}`,
    CREATE_BILL: '/api/billing/bills',
    PAYMENTS: '/api/payments/cash',
  },
};
