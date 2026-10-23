import { defineStore } from 'pinia'

const KEY = 'alur_auth'
const HOME = { CUSTOMER: '/customer', COURIER: '/courier', ADMIN: '/admin' }

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || {}
  } catch {
    return {}
  }
}

// Satu-satunya store. Hanya token + role + nama (JANGAN simpan password).
export const useAuthStore = defineStore('auth', {
  state: () => {
    const s = load()
    return {
      accessToken: s.accessToken || null,
      refreshToken: s.refreshToken || null,
      role: s.role || null,
      name: s.name || '',
    }
  },
  getters: {
    isLoggedIn: (s) => !!s.accessToken,
    homePath: (s) => HOME[s.role] || '/login',
  },
  actions: {
    /** Terima respons /auth/login atau /auth/refresh. */
    setSession(data) {
      this.accessToken = data.access_token
      this.refreshToken = data.refresh_token
      this.role = data.role
      this.name = data.name
      localStorage.setItem(
        KEY,
        JSON.stringify({ accessToken: this.accessToken, refreshToken: this.refreshToken, role: this.role, name: this.name }),
      )
    },
    clear() {
      this.accessToken = this.refreshToken = this.role = null
      this.name = ''
      localStorage.removeItem(KEY)
    },
  },
})
