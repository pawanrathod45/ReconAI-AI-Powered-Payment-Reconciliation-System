import axios from 'axios';

// Remove trailing slash if provided in environment variable
const rawBase = import.meta.env.VITE_API_URL || '';
const API_BASE = rawBase.replace(/\/+$/, '');

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

export const healthCheck = () => api.get('/api/health');
export const generateSampleData = () => api.post('/api/sample-data/generate');

export const uploadTransactions = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload/transactions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadSettlements = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload/settlements', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const runReconciliation = (month = 10, year = 2026) =>
  api.post(`/api/reconciliation/run?month=${month}&year=${year}`);

export const getReconciliationSummary = () => api.get('/api/reconciliation/summary');

export const getReconciliationResults = (params) =>
  api.get('/api/reconciliation/results', { params });

export const getExceptions = () => api.get('/api/reconciliation/exceptions');

export const getMonthlyReconciliation = (month = 10, year = 2026) =>
  api.get(`/api/reconciliation/monthly?month=${month}&year=${year}`);

export const exportReport = (format = 'csv', type = 'full') =>
  api.get(`/api/reports/export?format=${format}&type=${type}`, { responseType: 'blob' });

export const getTransactions = (params) => api.get('/api/transactions', { params });
export const getSettlements = (params) => api.get('/api/settlements', { params });

export default api;
