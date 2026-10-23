<script setup>
import { onMounted, ref, watch } from 'vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'
import ShipmentCard from '@/components/ShipmentCard.vue'
import { getMyShipments } from '@/api'
import { STATUS, STATUS_LIST } from '@/utils/format'

const LIMIT = 10
const filter = ref('')
const items = ref([])
const page = ref(1)
const pages = ref(0)
const loading = ref(false)
const error = ref('')

async function load(reset = true) {
  if (reset) {
    page.value = 1
    items.value = []
  }
  loading.value = true
  error.value = ''
  try {
    const res = await getMyShipments({ status: filter.value, page: page.value, limit: LIMIT })
    items.value = reset ? res.items : [...items.value, ...res.items]
    pages.value = res.pages
  } catch (e) {
    error.value = e.userMessage
  } finally {
    loading.value = false
  }
}

function more() {
  page.value += 1
  load(false)
}

onMounted(load)
watch(filter, () => load())
</script>

<template>
  <div class="px-5 pt-6">
    <h1 class="mb-4 text-xl font-bold text-slate-800">Riwayat Pengiriman</h1>

    <div class="hide-scroll -mx-5 mb-4 flex gap-2 overflow-x-auto px-5 pb-1" role="group" aria-label="Filter status">
      <button type="button" class="min-h-[44px] shrink-0 rounded-full border px-4 text-sm font-semibold"
        :class="filter === '' ? 'border-navy bg-navy text-white' : 'border-slate-300 bg-white text-slate-700'" :aria-pressed="filter === ''" @click="filter = ''">Semua</button>
      <button v-for="s in STATUS_LIST" :key="s" type="button" class="min-h-[44px] shrink-0 rounded-full border px-4 text-sm font-semibold"
        :class="filter === s ? 'border-navy bg-navy text-white' : 'border-slate-300 bg-white text-slate-700'" :aria-pressed="filter === s" @click="filter = s">{{ STATUS[s].label }}</button>
    </div>

    <LoadingState v-if="loading && !items.length" />
    <ErrorState v-else-if="error && !items.length" :message="error" @retry="load()" />
    <EmptyState v-else-if="!items.length" title="Belum ada pengiriman" :description="filter ? 'Tidak ada pengiriman dengan status ini.' : 'Buat pengiriman pertama Anda dari Beranda.'" />
    <div v-else class="space-y-3">
      <ShipmentCard v-for="s in items" :key="s.id" :shipment="s" :to="`/customer/shipments/${s.tracking_number}`" />
      <p v-if="error" role="alert" class="text-center text-sm text-danger">{{ error }}</p>
      <button v-if="page < pages" type="button" class="btn-secondary w-full" :disabled="loading" @click="more">
        <i v-if="loading" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Muat lebih banyak
      </button>
    </div>
  </div>
</template>
