<script setup>
defineProps({ text: { type: String, default: 'Memuat data...' } })
</script>

<template>
  <div role="status" class="flex flex-col items-center justify-center gap-3 py-12 text-slate-500">
    <i class="fa-solid fa-circle-notch fa-spin text-2xl text-navy" aria-hidden="true"></i>
    <p class="text-sm">{{ text }}</p>
  </div>
</template>
