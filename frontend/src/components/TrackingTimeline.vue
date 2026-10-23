<script setup>
import { computed } from 'vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { STATUS, formatDateTime } from '@/utils/format'

const props = defineProps({
  history: { type: Array, required: true }, // terlama -> terbaru (urutan dari API)
  rejectionReason: { type: String, default: '' },
})
// Terbaru di atas, seperti prototype
const items = computed(() => [...props.history].reverse())
</script>

<template>
  <ol class="relative space-y-5 pl-8 before:absolute before:inset-y-1 before:left-[11px] before:w-0.5 before:bg-slate-200">
    <li v-for="(h, i) in items" :key="i" class="relative">
      <span
        class="absolute -left-8 flex h-6 w-6 items-center justify-center rounded-full text-white ring-4 ring-white"
        :class="i === 0 ? STATUS[h.status]?.dot : 'bg-slate-300'"
      >
        <i class="fa-solid text-[10px]" :class="STATUS[h.status]?.icon" aria-hidden="true"></i>
      </span>
      <StatusBadge :status="h.status" />
      <p class="mt-1.5 text-sm text-slate-700">{{ h.notes }}</p>
      <p v-if="h.status === 'REJECTED' && rejectionReason" class="mt-1 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
        <span class="font-bold">Alasan penolakan:</span> {{ rejectionReason }}
      </p>
      <p class="mt-0.5 text-xs text-slate-500">
        {{ formatDateTime(h.created_at) }}<template v-if="h.created_by_name"> · oleh {{ h.created_by_name }}</template>
      </p>
    </li>
  </ol>
</template>
