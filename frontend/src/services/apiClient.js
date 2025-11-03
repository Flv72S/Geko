import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor per aggiungere il token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('geko_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor per gestire errori di autenticazione
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Token scaduto o non valido
      localStorage.removeItem('geko_token');
      localStorage.removeItem('geko_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

