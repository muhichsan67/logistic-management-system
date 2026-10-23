<script setup>
import { computed, onMounted, ref } from 'vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'
import ShipmentCard from '@/components/ShipmentCard.vue'
import { getCourierTasks } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { firstName } from '@/utils/format'

const auth = useAuthStore()
const ACTIVE = ['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']

const items = ref([])
const loading = ref(false)
const error = ref('')
const tab = ref('active') // active | history

// Tugas kurir tidak banyak: muat semua halaman (maks 5 x 100) lalu pisahkan Aktif / Riwayat di sisi klien.
async function load() {
  loading.value = true
  error.value = ''
  try {
    const all = []
    for (let page = 1; page <= 5; page++) {
      const res = await getCourierTasks({ page, limit: 100 })
      all.push(...res.items)
      if (page >= res.pages) break
    }
    items.value = all
  } catch (e) {
    error.value = e.userMessage
  } finally {
    loading.value = false
  }
}
onMounted(load)

const activeTasks = computed(() => items.value.filter((s) => ACTIVE.includes(s.status)))
const historyTasks = computed(() => items.value.filter((s) => !ACTIVE.includes(s.status)))
const shown = computed(() => (tab.value === 'active' ? activeTasks.value : historyTasks.value))
</script>

<template>
  <div>
    <header class="rounded-b-3xl bg-emerald-600 px-5 pb-6 pt-6 text-white shadow-md">
      <div class="mb-4 text-lg font-bold"><i class="fa-solid fa-motorcycle mr-1" aria-hidden="true"></i> Aplikasi Kurir</div>
      <h1 class="text-xl font-bold">Semangat, {{ firstName(auth.name) }}!</h1>
      <p class="text-sm text-emerald-100">Ada {{ activeTasks.length }} tugas aktif saat ini.</p>
    </header>

    <div class="px-5 py-5">
      <div class="mb-4 grid grid-cols-2 gap-2 rounded-xl bg-slate-200 p-1" role="tablist">
        <button type="button" role="tab" :aria-selected="tab === 'active'" class="min-h-[44px] rounded-lg text-sm font-bold" :class="tab === 'active' ? 'bg-white text-emerald-700 shadow' : 'text-slate-600'" @click="tab = 'active'">Aktif ({{ activeTasks.length }})</button>
        <button type="button" role="tab" :aria-selected="tab === 'history'" class="min-h-[44px] rounded-lg text-sm font-bold" :class="tab === 'history' ? 'bg-white text-emerald-700 shadow' : 'text-slate-600'" @click="tab = 'history'">Riwayat ({{ historyTasks.length }})</button>
      </div>

      <LoadingState v-if="loading && !items.length" />
      <ErrorState v-else-if="error" :message="error" @retry="load" />
      <EmptyState v-else-if="!shown.length" icon="fa-clipboard-list" :title="tab === 'active' ? 'Belum ada tugas aktif' : 'Belum ada riwayat tugas'" description="Tugas dari Admin akan tampil di sini." />
      <div v-else class="space-y-3">
        <ShipmentCard v-for="s in shown" :key="s.id" :shipment="s" :to="`/courier/tasks/${s.id}`" variant="courier" />
      </div>
    </div>
  </div>
</template>
