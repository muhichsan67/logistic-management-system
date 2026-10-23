<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import TrackingTimeline from '@/components/TrackingTimeline.vue'
import { trackShipment } from '@/api'
import { useAuthStore } from '@/stores/auth'

// Halaman publik: bisa dibuka tanpa login.
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const input = ref(route.params.trackingNumber || '')
const result = ref(null)
const loading = ref(false)
const notFound = ref(false)
const error = ref('')

async function load(tn) {
  result.value = null
  notFound.value = false
  error.value = ''
  if (!tn) return
  loading.value = true
  try {
    result.value = await trackShipment(tn)
  } catch (e) {
    if (e.response?.status === 404) notFound.value = true
    else error.value = e.userMessage
  } finally {
    loading.value = false
  }
}

watch(() => route.params.trackingNumber, (tn) => { input.value = tn || ''; load(tn) }, { immediate: true })

function search() {
  const tn = input.value.trim().toUpperCase()
  if (!tn) return
  if (tn === route.params.trackingNumber) load(tn)
  else router.push(`/track/${encodeURIComponent(tn)}`)
}
</script>

<template>
  <div class="mx-auto min-h-screen max-w-md bg-slate-50 shadow-2xl">
    <header class="rounded-b-3xl bg-navy px-5 pb-6 pt-5 text-white shadow-md">
      <div class="mb-4 flex items-center justify-between">
        <RouterLink :to="auth.isLoggedIn ? auth.homePath : '/login'" class="flex min-h-[44px] items-center gap-2 font-bold">
          <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> {{ auth.isLoggedIn ? 'Beranda' : 'Masuk' }}
        </RouterLink>
        <i class="fa-solid fa-box-open text-xl text-amber" aria-hidden="true"></i>
      </div>
      <h1 class="text-2xl font-bold">Lacak Paket</h1>
      <p class="mb-4 text-sm text-blue-200">Masukkan nomor resi untuk melihat status terkini.</p>
      <form class="flex gap-2" role="search" @submit.prevent="search">
        <label for="resi" class="sr-only">Nomor resi</label>
        <input id="resi" v-model="input" type="text" placeholder="TRX-20260925-0001" autocapitalize="characters" class="min-h-[44px] flex-1 rounded-xl bg-white p-3 font-mono text-base uppercase text-slate-800 outline-none focus:ring-2 focus:ring-amber" />
        <button type="submit" class="btn-amber px-4" aria-label="Cari"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i></button>
      </form>
    </header>

    <main class="px-5 py-6">
      <LoadingState v-if="loading" text="Mencari paket..." />
      <ErrorState v-else-if="error" :message="error" @retry="load(route.params.trackingNumber)" />
      <EmptyState v-else-if="notFound" icon="fa-magnifying-glass" title="Nomor resi tidak ditemukan" description="Periksa kembali nomor resi Anda." />
      <EmptyState v-else-if="!result" icon="fa-truck-fast" title="Belum ada pencarian" description="Hasil pelacakan akan tampil di sini." />

      <div v-else class="card animate-fade-in p-5">
        <div class="mb-4 flex items-start justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <p class="text-xs text-slate-500">No. Resi</p>
            <p class="font-mono text-lg font-bold text-navy">{{ result.tracking_number }}</p>
          </div>
          <StatusBadge :status="result.status" />
        </div>
        <dl class="mb-5 space-y-2 text-sm">
          <div class="flex justify-between gap-4"><dt class="text-slate-500">Pengirim</dt><dd class="text-right font-semibold">{{ result.sender_name }}</dd></div>
          <div class="flex justify-between gap-4"><dt class="text-slate-500">Penerima</dt><dd class="text-right font-semibold">{{ result.recipient_name }}</dd></div>
          <div class="flex justify-between gap-4"><dt class="text-slate-500">Tujuan</dt><dd class="text-right font-semibold">{{ result.destination_address }}</dd></div>
        </dl>
        <h2 class="mb-3 text-sm font-bold text-slate-700">Riwayat Pengiriman</h2>
        <TrackingTimeline :history="result.history" />
      </div>
    </main>
  </div>
</template>
