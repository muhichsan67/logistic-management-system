<script setup>
import { watch } from 'vue'
import Dialog from 'primevue/dialog'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import TrackingTimeline from '@/components/TrackingTimeline.vue'
import { getAdminShipment } from '@/api'
import { useAsync } from '@/utils/useAsync'
import { assetUrl, formatDateTime, formatWeight } from '@/utils/format'

const props = defineProps({ shipmentId: { type: Number, default: null } })
const visible = defineModel({ type: Boolean, default: false })
const detail = useAsync(() => getAdminShipment(props.shipmentId))

watch(visible, (v) => {
  if (v && props.shipmentId) {
    detail.data.value = null
    detail.run()
  }
})
</script>

<template>
  <Dialog v-model:visible="visible" modal header="Detail Pengiriman" :style="{ width: '36rem' }" :draggable="false">
    <LoadingState v-if="detail.loading.value && !detail.data.value" />
    <ErrorState v-else-if="detail.error.value" :message="detail.error.value" @retry="detail.run()" />
    <div v-else-if="detail.data.value" class="space-y-4 text-sm">
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 pb-3">
        <StatusBadge :status="detail.data.value.status" />
        <span class="font-mono text-lg font-bold text-navy">{{ detail.data.value.tracking_number }}</span>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-lg bg-slate-50 p-3">
          <p class="text-xs font-bold uppercase text-slate-500">Customer</p>
          <p class="font-semibold">{{ detail.data.value.customer_name || '-' }}</p>
          <p class="text-xs text-slate-500">ID: #{{ detail.data.value.customer_id }}</p>
        </div>
        <div class="rounded-lg bg-slate-50 p-3">
          <p class="text-xs font-bold uppercase text-slate-500">Kurir</p>
          <p class="font-semibold">{{ detail.data.value.courier_name || 'Belum ditugaskan' }}</p>
          <p v-if="detail.data.value.courier_phone" class="text-xs text-slate-500">{{ detail.data.value.courier_phone }}</p>
        </div>
        <div class="rounded-lg bg-slate-50 p-3">
          <p class="text-xs font-bold uppercase text-slate-500">Pengirim</p>
          <p class="font-semibold">{{ detail.data.value.sender_name }} · {{ detail.data.value.sender_phone }}</p>
          <p class="text-slate-600">{{ detail.data.value.origin_address }}</p>
        </div>
        <div class="rounded-lg bg-slate-50 p-3">
          <p class="text-xs font-bold uppercase text-slate-500">Penerima</p>
          <p class="font-semibold">{{ detail.data.value.recipient_name }} · {{ detail.data.value.recipient_phone }}</p>
          <p class="text-slate-600">{{ detail.data.value.destination_address }}</p>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 p-3">
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Detail Paket</p>
        <p class="flex justify-between"><span>Deskripsi</span><span class="font-semibold">{{ detail.data.value.package_description }}</span></p>
        <p class="flex justify-between"><span>Berat</span><span class="font-semibold">{{ formatWeight(detail.data.value.weight_kg) }}</span></p>
        <p class="flex justify-between"><span>Dibuat</span><span class="font-semibold">{{ formatDateTime(detail.data.value.created_at) }}</span></p>
      </div>

      <div v-if="detail.data.value.proof_image_url">
        <p class="mb-1 text-xs font-bold uppercase text-slate-500">Bukti Pengiriman</p>
        <a :href="assetUrl(detail.data.value.proof_image_url)" target="_blank" rel="noopener">
          <img :src="assetUrl(detail.data.value.proof_image_url)" alt="Foto bukti pengiriman" class="max-h-56 rounded-lg border border-slate-200 object-contain" />
        </a>
      </div>

      <div>
        <p class="mb-2 text-xs font-bold uppercase text-slate-500">Log Riwayat</p>
        <TrackingTimeline :history="detail.data.value.history" :rejection-reason="detail.data.value.rejection_reason || ''" />
      </div>
    </div>
  </Dialog>
</template>
