import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000, // 10 second timeout for better reliability
});

// Request Interceptor: Automatically attach token if available
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle global errors like 401 Unauthorized
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // If unauthorized, clear session and redirect to login
      localStorage.clear();
      if (!window.location.pathname.includes('/login')) {
         window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default API;
