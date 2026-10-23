<script setup>
import { computed } from 'vue'

// Grafik batang ringan (tanpa library). items: [{ label, value, tip?, color? }]
const props = defineProps({
  items: { type: Array, required: true },
  horizontal: { type: Boolean, default: false },
  labelEvery: { type: Number, default: 1 }, // tampilkan label tiap N batang (vertikal)
  title: { type: String, default: 'Grafik' },
})
const max = computed(() => Math.max(1, ...props.items.map((i) => i.value)))
const pct = (v) => (v === 0 ? 0 : Math.max(3, Math.round((v / max.value) * 100)))
const summary = computed(() => `${props.title}: ${props.items.map((i) => `${i.label} ${i.value}`).join(', ')}`)
</script>

<template>
  <ul v-if="horizontal" class="space-y-3" :aria-label="summary">
    <li v-for="it in items" :key="it.label" class="flex items-center gap-3 text-sm">
      <span class="w-36 shrink-0 text-slate-600">{{ it.label }}</span>
      <div class="h-3 flex-1 overflow-hidden rounded-full bg-slate-100">
        <div class="h-full rounded-full" :class="it.color || 'bg-navy'" :style="{ width: pct(it.value) + '%' }"></div>
      </div>
      <span class="w-10 text-right font-bold text-slate-800">{{ it.value }}</span>
    </li>
  </ul>

  <div v-else role="img" :aria-label="summary">
    <div class="flex h-48 items-end gap-1 border-b border-slate-200">
      <div v-for="it in items" :key="it.label" class="group flex h-full min-w-0 flex-1 flex-col justify-end" :title="`${it.label}: ${it.value}`">
        <span v-if="items.length <= 14" class="mb-1 text-center text-xs font-bold text-slate-600">{{ it.value }}</span>
        <div class="w-full rounded-t bg-navy transition group-hover:bg-blue-600" :style="{ height: pct(it.value) + '%' }"></div>
      </div>
    </div>
    <div class="mt-1 flex gap-1">
      <span v-for="(it, i) in items" :key="it.label" class="min-w-0 flex-1 truncate text-center text-xs text-slate-500">
        {{ i % labelEvery === 0 ? it.label : '' }}
      </span>
    </div>
  </div>
</template>
