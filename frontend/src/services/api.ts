import axios from 'axios';

// Usar variável de ambiente do Vite ou fallback para localhost
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 segundos
});

// Interceptor para logging (útil para debug)
api.interceptors.request.use(
  (config) => {
    console.log(`📡 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export default api;
