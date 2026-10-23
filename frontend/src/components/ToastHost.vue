<script setup>
import { toasts } from '@/utils/toast'

const style = {
  success: ['bg-emerald-600', 'fa-circle-check'],
  error: ['bg-red-600', 'fa-circle-exclamation'],
  info: ['bg-slate-800', 'fa-circle-info'],
}
</script>

<template>
  <div class="pointer-events-none fixed inset-x-0 top-3 z-[90] flex flex-col items-center gap-2 px-4" aria-live="polite">
    <div
      v-for="t in toasts" :key="t.id" role="status"
      class="pointer-events-auto flex w-full max-w-sm animate-fade-in items-start gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-white shadow-lg"
      :class="style[t.type][0]"
    >
      <i class="fa-solid mt-0.5" :class="style[t.type][1]" aria-hidden="true"></i>
      <span>{{ t.message }}</span>
    </div>
  </div>
</template>
