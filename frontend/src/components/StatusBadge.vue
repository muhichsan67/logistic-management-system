<script setup>
import { computed } from 'vue'
import { STATUS } from '@/utils/format'

const props = defineProps({ status: { type: String, required: true } })
const s = computed(() => STATUS[props.status] ?? { label: props.status, icon: 'fa-circle', cls: 'bg-slate-100 text-slate-700' })
</script>

<template>
  <!-- Selalu ada teks label (tidak hanya warna) -->
  <span class="inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-bold" :class="s.cls">
    <i class="fa-solid text-[10px]" :class="s.icon" aria-hidden="true"></i>{{ s.label }}
  </span>
</template>
