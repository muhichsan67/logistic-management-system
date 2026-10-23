import { ref } from 'vue'

/**
 * Pola 3 keadaan layar (memuat / gagal / data) yang dipakai semua halaman.
 *   const list = useAsync(() => getMyShipments({ limit: 50 }))
 *   onMounted(list.run)   ->   list.loading / list.error / list.data
 */
export function useAsync(fn) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function run(...args) {
    loading.value = true
    error.value = ''
    try {
      data.value = await fn(...args)
      return data.value
    } catch (e) {
      error.value = e.userMessage || 'Terjadi kesalahan, coba lagi'
      return null
    } finally {
      loading.value = false
    }
  }
  return { data, loading, error, run }
}
