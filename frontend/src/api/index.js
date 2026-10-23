// Semua pemanggilan API ada di sini. Komponen/halaman TIDAK boleh menulis URL sendiri.
import http from './http'

const data = (r) => r.data
const clean = (p = {}) => Object.fromEntries(Object.entries(p).filter(([, v]) => v !== '' && v != null))

// ---- Auth ----
export const login = (email, password) => http.post('/auth/login', { email, password }).then(data)
export const register = (payload) => http.post('/auth/register', payload).then(data)
export const logout = (refreshToken) => http.post('/auth/logout', { refresh_token: refreshToken })
export const getMe = () => http.get('/auth/me').then(data)

// ---- Customer & publik ----
export const createShipment = (payload) => http.post('/shipments', payload).then(data)
export const getMyShipments = (params) => http.get('/shipments/me', { params: clean(params) }).then(data)
export const getMyShipment = (trackingNumber) => http.get(`/shipments/me/${encodeURIComponent(trackingNumber)}`).then(data)
export const confirmShipment = (id) => http.put(`/shipments/${id}/confirm`).then(data)
export const trackShipment = (trackingNumber) => http.get(`/shipments/${encodeURIComponent(trackingNumber)}/track`).then(data)

// ---- Kurir ----
export const getCourierTasks = (params) => http.get('/courier/shipments', { params: clean(params) }).then(data)
export const getCourierTask = (id) => http.get(`/courier/shipments/${id}`).then(data)
export const updateTaskStatus = (id, payload) => http.put(`/courier/shipments/${id}/status`, payload).then(data)
export const uploadProof = (file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/uploads/proof', form, { timeout: 60000 }).then(data)
}

// ---- Admin ----
export const getAdminShipments = (params) => http.get('/admin/shipments', { params: clean(params) }).then(data)
export const getAdminShipment = (id) => http.get(`/admin/shipments/${id}`).then(data)
export const assignCourier = (id, payload) => http.put(`/admin/shipments/${id}/assign`, payload).then(data)
export const rejectShipment = (id, rejection_reason) => http.put(`/admin/shipments/${id}/reject`, { rejection_reason }).then(data)
export const getDashboardSummary = (period) => http.get('/admin/dashboard/summary', { params: { period } }).then(data)
export const getCouriers = (params) => http.get('/admin/couriers', { params: clean(params) }).then(data)
export const createCourier = (payload) => http.post('/admin/couriers', payload).then(data)
export const updateCourier = (id, payload) => http.put(`/admin/couriers/${id}`, payload).then(data)
export const deactivateCourier = (id) => http.patch(`/admin/couriers/${id}/deactivate`).then(data)
export const getSettings = () => http.get('/admin/settings').then(data)
export const updateSettings = (payload) => http.put('/admin/settings', payload).then(data)
