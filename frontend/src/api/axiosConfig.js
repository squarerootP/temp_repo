import axios from 'axios';
import { getToken, removeToken } from '@/services/tokenService';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// ✅ Request interceptor - MUST get token synchronously
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken(); // Get token from localStorage
    
    console.log('🔑 Request interceptor - Token:', token ? 'Found' : 'Not found'); // Debug
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log('📤 Request:', config.method?.toUpperCase(), config.url); // Debug
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ Response:', response.config.url, response.status); // Debug
    return response;
  },
  (error) => {
    console.error('❌ Response error:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data
    });
    
    if (error.response?.status === 401) {
      console.log('🚪 401 Unauthorized - Removing token and redirecting');
      removeToken();
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;