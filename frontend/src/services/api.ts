import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? 'https://api.arcsat.com.br/api'
    : 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
