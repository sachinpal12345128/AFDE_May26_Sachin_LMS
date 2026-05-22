// Central axios instance - every API call in the app goes through here.
// Switch backend URL by setting VITE_API_BASE in a .env file (e.g.
// VITE_API_BASE=http://localhost:8000) or just edit the default below.

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ---------- Books ----------
export const listBooks = () => api.get('/books').then((r) => r.data);
export const getBook = (id) => api.get(`/books/${id}`).then((r) => r.data);
export const createBook = (data) => api.post('/books', data).then((r) => r.data);
export const updateBook = (id, data) => api.put(`/books/${id}`, data).then((r) => r.data);
export const deleteBook = (id) => api.delete(`/books/${id}`);

// ---------- Borrowers ----------
export const listBorrowers = () => api.get('/borrowers').then((r) => r.data);
export const createBorrower = (data) => api.post('/borrowers', data).then((r) => r.data);
export const updateBorrower = (id, data) => api.put(`/borrowers/${id}`, data).then((r) => r.data);
export const deleteBorrower = (id) => api.delete(`/borrowers/${id}`);

// ---------- Transactions ----------
export const borrowBook = (data) => api.post('/borrow', data).then((r) => r.data);
export const returnBook = (data) => api.post('/return', data).then((r) => r.data);
export const listTransactions = () => api.get('/transactions').then((r) => r.data);

// ---------- Search ----------
export const searchBooks = (q) =>
  api.get('/search', { params: { q } }).then((r) => r.data);

// ---------- Dashboard ----------
export const dashboardStats = () => api.get('/dashboard/stats').then((r) => r.data);

// ---------- Phase 2 - Analytics ----------
export const analyticsSummary = () =>
  api.get('/analytics/summary').then((r) => r.data);
export const analyticsMostBorrowed = (limit = 10) =>
  api.get('/analytics/most-borrowed', { params: { limit } }).then((r) => r.data);
export const analyticsCategoryBorrowing = () =>
  api.get('/analytics/category-borrowing').then((r) => r.data);
export const analyticsMonthlyTrend = () =>
  api.get('/analytics/monthly-trend').then((r) => r.data);
export const analyticsOverdue = (onlyOpen = false) =>
  api
    .get('/analytics/overdue', { params: onlyOpen ? { only_open: true } : {} })
    .then((r) => r.data);
export const analyticsEtlRuns = () =>
  api.get('/analytics/etl-runs').then((r) => r.data);

// Helper - extract a useful message from an axios error
export function errorMessage(err) {
  return (
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    'Something went wrong'
  );
}

export default api;
