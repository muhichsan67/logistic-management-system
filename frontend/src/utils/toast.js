import { reactive } from 'vue'

// Notifikasi singkat (bukan store Pinia). Ditampilkan oleh components/ToastHost.vue
export const toasts = reactive([])
let seq = 0

function push(type, message, ms = 4000) {
  const t = { id: ++seq, type, message }
  toasts.push(t)
  setTimeout(() => {
    const i = toasts.findIndex((x) => x.id === t.id)
    if (i > -1) toasts.splice(i, 1)
  }, ms)
}

export const toast = {
  success: (m) => push('success', m),
  error: (m) => push('error', m, 5500),
  info: (m) => push('info', m),
}
