import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import * as api from '@/api'

/** Logout: cabut refresh token di server (best-effort), hapus sesi lokal, ke /login. */
export async function logout() {
  const auth = useAuthStore()
  try {
    if (auth.refreshToken) await api.logout(auth.refreshToken)
  } catch {
    /* tetap logout lokal */
  }
  auth.clear()
  router.push('/login')
}
