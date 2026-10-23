import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import { toast } from '@/utils/toast'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const http = axios.create({ baseURL, timeout: 20000 })

http.interceptors.request.use((config) => {
  const { accessToken } = useAuthStore()
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

// Satu proses refresh untuk banyak request yang 401 bersamaan.
let refreshing = null
function refreshSession(auth) {
  if (!refreshing) {
    refreshing = axios
      .post(`${baseURL}/auth/refresh`, { refresh_token: auth.refreshToken }) // axios polos: tanpa interceptor
      .then((r) => {
        auth.setSession(r.data) // refresh token DIROTASI, simpan yang baru
        return r.data.access_token
      })
      .finally(() => (refreshing = null))
  }
  return refreshing
}

function messageFor(error) {
  const res = error.response
  if (!res) return 'Koneksi bermasalah, coba lagi'
  if (res.status === 403) return 'Anda tidak memiliki akses'
  if (res.status >= 500) return 'Terjadi kesalahan pada server, coba lagi nanti'
  return res.data?.detail || 'Terjadi kesalahan, coba lagi'
}

http.interceptors.response.use(
  (r) => r,
  async (error) => {
    const { config, response } = error
    const auth = useAuthStore()
    const isAuthCall = /\/auth\/(login|refresh|register)/.test(config?.url || '')

    if (response?.status === 401 && !isAuthCall && !config._retry) {
      config._retry = true
      if (auth.refreshToken) {
        try {
          const token = await refreshSession(auth)
          config.headers.Authorization = `Bearer ${token}`
          return http(config) // ulangi request semula
        } catch {
          /* refresh gagal -> logout di bawah */
        }
      }
      auth.clear()
      router.push('/login')
      error.userMessage = 'Sesi berakhir, silakan masuk kembali'
      toast.error(error.userMessage)
      return Promise.reject(error)
    }

    error.userMessage = messageFor(error)
    error.fieldErrors = response?.data?.errors || []
    // GET: halaman menampilkan ErrorState + "Coba Lagi". Aksi lain: toast.
    if (config?.method !== 'get') toast.error(error.userMessage)
    return Promise.reject(error)
  },
)

export default http
