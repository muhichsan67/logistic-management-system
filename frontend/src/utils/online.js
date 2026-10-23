import { ref } from 'vue'

const online = ref(navigator.onLine)
window.addEventListener('online', () => (online.value = true))
window.addEventListener('offline', () => (online.value = false))

/** ref(boolean) status koneksi. Pakai untuk menonaktifkan tombol yang mengubah data. */
export const useOnline = () => online
