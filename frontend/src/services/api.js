import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
});

export const healthCheck = () => api.get('/api/health');
export const generateSampleData = () => api.post('/api/sample-data/generate');
export const uploadTransactions = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload/transactions', formData);
};
export const uploadSettlements = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload/settlements', formData);
};
export const runReconciliation = (month, year) =>
  api.post(`/api/reconciliation/run?month=${month}&year=${year}`);
export const getReconciliationSummary = () => api.get('/api/reconciliation/summary');
export const getReconciliationResults = (params) =>
  api.get('/api/reconciliation/results', { params });
export const getExceptions = () => api.get('/api/reconciliation/exceptions');
export const getMonthlyReconciliation = (month, year) =>
  api.get(`/api/reconciliation/monthly?month=${month}&year=${year}`);
export const exportReport = (format, type) =>
  api.get(`/api/reports/export?format=${format}&type=${type}`, { responseType: 'blob' });
export const getTransactions = () => api.get('/api/transactions');
export const getSettlements = () => api.get('/api/settlements');

export default api;
