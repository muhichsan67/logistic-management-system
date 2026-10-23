<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import TrackingTimeline from '@/components/TrackingTimeline.vue'
import { confirmShipment, getMyShipment } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'
import { useAsync } from '@/utils/useAsync'
import { assetUrl, formatWeight } from '@/utils/format'

const route = useRoute()
const online = useOnline()
const detail = useAsync(() => getMyShipment(route.params.trackingNumber))
const confirming = ref(false)
onMounted(detail.run)

async function confirm() {
  if (!window.confirm('Konfirmasi bahwa paket sudah Anda terima?')) return
  confirming.value = true
  try {
    await confirmShipment(detail.data.value.id)
    toast.success('Pesanan dikonfirmasi selesai')
    await detail.run() // muat ulang dari server
  } catch {
    /* toast dari interceptor */
  } finally {
    confirming.value = false
  }
}
</script>

<template>
  <div>
    <PageHeader title="Detail Pengiriman" back-to="/customer/history" />

    <div class="px-5 py-5">
      <LoadingState v-if="detail.loading.value && !detail.data.value" />
      <ErrorState v-else-if="detail.error.value" :message="detail.error.value" @retry="detail.run" />

      <div v-else-if="detail.data.value" class="space-y-4">
        <div class="text-center">
          <StatusBadge :status="detail.data.value.status" />
          <h1 class="mt-2 font-mono text-xl font-bold text-navy">{{ detail.data.value.tracking_number }}</h1>
          <p v-if="detail.data.value.courier_name" class="mt-1 text-sm text-slate-600">
            Kurir: {{ detail.data.value.courier_name }}
            <a v-if="detail.data.value.courier_phone" :href="`tel:${detail.data.value.courier_phone}`" class="font-semibold text-navy underline">({{ detail.data.value.courier_phone }})</a>
          </p>
        </div>

        <div v-if="detail.data.value.status === 'REJECTED'" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <p class="font-bold">Permintaan ditolak</p>
          <p>{{ detail.data.value.rejection_reason }}</p>
        </div>

        <section class="rounded-xl border border-slate-100 bg-white p-4" aria-labelledby="route-title">
          <h2 id="route-title" class="mb-3 text-xs font-bold uppercase text-slate-500">Informasi Rute</h2>
          <div class="mb-3 flex gap-3">
            <i class="fa-solid fa-circle-dot mt-1 text-slate-400" aria-hidden="true"></i>
            <div class="text-sm">
              <p class="text-xs text-slate-500">Asal (Pengirim)</p>
              <p class="font-semibold">{{ detail.data.value.sender_name }}</p>
              <p class="text-slate-600">{{ detail.data.value.origin_address }}</p>
            </div>
          </div>
          <div class="flex gap-3">
            <i class="fa-solid fa-location-dot mt-1 text-amber" aria-hidden="true"></i>
            <div class="text-sm">
              <p class="text-xs text-slate-500">Tujuan (Penerima)</p>
              <p class="font-semibold">{{ detail.data.value.recipient_name }}</p>
              <p class="text-slate-600">{{ detail.data.value.destination_address }}</p>
            </div>
          </div>
        </section>

        <section class="rounded-xl border border-slate-100 bg-white p-4 text-sm" aria-labelledby="pkg-title">
          <h2 id="pkg-title" class="mb-2 text-xs font-bold uppercase text-slate-500">Detail Paket</h2>
          <p class="flex justify-between gap-4"><span class="text-slate-500">Isi Paket</span><span class="text-right font-semibold">{{ detail.data.value.package_description }}</span></p>
          <p class="flex justify-between gap-4"><span class="text-slate-500">Berat</span><span class="font-semibold">{{ formatWeight(detail.data.value.weight_kg) }}</span></p>
        </section>

        <section v-if="detail.data.value.proof_image_url" class="rounded-xl border border-slate-100 bg-white p-4">
          <h2 class="mb-2 text-xs font-bold uppercase text-slate-500">Bukti Pengiriman</h2>
          <a :href="assetUrl(detail.data.value.proof_image_url)" target="_blank" rel="noopener">
            <img :src="assetUrl(detail.data.value.proof_image_url)" alt="Foto bukti pengiriman" class="w-full rounded-lg object-cover" loading="lazy" />
          </a>
        </section>

        <section class="rounded-xl border border-slate-100 bg-white p-4" aria-labelledby="hist-title">
          <h2 id="hist-title" class="mb-4 text-xs font-bold uppercase text-slate-500">Riwayat Pengiriman</h2>
          <TrackingTimeline :history="detail.data.value.history" :rejection-reason="detail.data.value.rejection_reason || ''" />
        </section>

        <!-- Hanya saat DELIVERED. Customer tidak punya tombol batal. -->
        <button v-if="detail.data.value.status === 'DELIVERED'" type="button" class="btn-success w-full !py-3.5 text-base shadow-lg" :disabled="confirming || !online" @click="confirm">
          <i v-if="confirming" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i>
          <i v-else class="fa-solid fa-circle-check" aria-hidden="true"></i> Konfirmasi Selesai
        </button>
      </div>
    </div>
  </div>
</template>
