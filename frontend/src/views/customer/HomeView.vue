<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'
import ShipmentCard from '@/components/ShipmentCard.vue'
import { getMyShipments } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useAsync } from '@/utils/useAsync'
import { firstName } from '@/utils/format'

const router = useRouter()
const auth = useAuthStore()
const ACTIVE = ['PENDING', 'ASSIGNED', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED']

const list = useAsync(() => getMyShipments({ limit: 50 }))
const active = computed(() => (list.data.value?.items ?? []).filter((s) => ACTIVE.includes(s.status)))
onMounted(list.run)

const resi = ref('')
function track() {
  const tn = resi.value.trim().toUpperCase()
  if (tn) router.push(`/track/${encodeURIComponent(tn)}`)
}
</script>

<template>
  <div>
    <header class="rounded-b-3xl bg-navy px-5 pb-6 pt-6 text-white shadow-md">
      <div class="mb-5 flex items-center justify-between">
        <div class="text-xl font-bold tracking-tight"><i class="fa-solid fa-box-open mr-1 text-amber" aria-hidden="true"></i> LajuLogistik</div>
      </div>
      <h1 class="text-2xl font-bold">Halo, {{ firstName(auth.name) }}! 👋</h1>
      <p class="mt-1 text-sm text-blue-200">Mau kirim atau lacak paket hari ini?</p>

      <RouterLink to="/customer/shipments/new" class="btn-amber mt-5 w-full !py-3 text-base shadow">
        <i class="fa-solid fa-paper-plane" aria-hidden="true"></i> Buat Pengiriman
      </RouterLink>

      <form class="mt-3 flex gap-2" role="search" @submit.prevent="track">
        <label for="resi" class="sr-only">Cari nomor resi</label>
        <input id="resi" v-model="resi" type="text" placeholder="Cari nomor resi (TRX-...)" autocapitalize="characters" class="min-h-[44px] flex-1 rounded-xl bg-white p-3 font-mono text-base uppercase text-slate-800 outline-none placeholder:font-sans placeholder:normal-case focus:ring-2 focus:ring-amber" />
        <button type="submit" class="btn bg-white px-4 text-navy hover:bg-slate-100" aria-label="Lacak"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i></button>
      </form>
    </header>

    <section class="px-5 py-6" aria-labelledby="active-title">
      <div class="mb-4 flex items-center justify-between">
        <h2 id="active-title" class="text-lg font-bold text-slate-800">Sedang Berlangsung</h2>
        <RouterLink to="/customer/history" class="flex min-h-[44px] items-center text-sm font-semibold text-navy">Lihat Semua</RouterLink>
      </div>

      <LoadingState v-if="list.loading.value && !list.data.value" />
      <ErrorState v-else-if="list.error.value" :message="list.error.value" @retry="list.run" />
      <EmptyState v-else-if="!active.length" title="Belum ada pengiriman aktif" description="Pengiriman yang sedang berjalan akan tampil di sini." />
      <div v-else class="space-y-3">
        <ShipmentCard v-for="s in active" :key="s.id" :shipment="s" :to="`/customer/shipments/${s.tracking_number}`" />
      </div>
    </section>
  </div>
</template>
