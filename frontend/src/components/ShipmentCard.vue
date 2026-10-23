<script setup>
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDateTime } from '@/utils/format'

// variant "customer": pengirim -> penerima. variant "courier": tujuan + penerima.
defineProps({
  shipment: { type: Object, required: true },
  to: { type: [String, Object], required: true },
  variant: { type: String, default: 'customer' },
})
</script>

<template>
  <RouterLink :to="to" class="card block p-4 transition hover:border-navy focus:outline-none focus-visible:ring-2 focus-visible:ring-navy">
    <div class="mb-3 flex items-start justify-between gap-2 border-b border-slate-100 pb-3">
      <div>
        <p class="text-xs font-medium text-slate-500">No. Resi</p>
        <p class="font-mono text-sm font-bold text-navy">{{ shipment.tracking_number }}</p>
      </div>
      <StatusBadge :status="shipment.status" />
    </div>

    <div v-if="variant === 'customer'" class="flex items-center gap-3">
      <div class="min-w-0 flex-1">
        <p class="text-xs text-slate-500">Pengirim</p>
        <p class="truncate text-sm font-semibold text-slate-700">{{ shipment.sender_name }}</p>
      </div>
      <i class="fa-solid fa-arrow-right text-slate-300" aria-hidden="true"></i>
      <div class="min-w-0 flex-1 text-right">
        <p class="text-xs text-slate-500">Penerima</p>
        <p class="truncate text-sm font-semibold text-slate-700">{{ shipment.recipient_name }}</p>
      </div>
    </div>
    <div v-else class="space-y-1 text-sm text-slate-600">
      <p><i class="fa-solid fa-location-dot w-5 text-emerald-600" aria-hidden="true"></i>{{ shipment.destination_address }}</p>
      <p><i class="fa-solid fa-user w-5 text-emerald-600" aria-hidden="true"></i>{{ shipment.recipient_name }} · {{ shipment.recipient_phone }}</p>
    </div>

    <p class="mt-3 text-xs text-slate-500">
      <i class="fa-regular fa-clock mr-1" aria-hidden="true"></i>{{ formatDateTime(shipment.created_at) }}
    </p>
  </RouterLink>
</template>
