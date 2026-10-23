<script setup>
defineProps({
  icon: { type: String, default: 'fa-box-open' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="flex flex-col items-center px-6 py-12 text-center">
    <div class="mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 text-2xl text-slate-400">
      <i class="fa-solid" :class="icon" aria-hidden="true"></i>
    </div>
    <p class="font-bold text-slate-700">{{ title }}</p>
    <p v-if="description" class="mt-1 text-sm text-slate-500">{{ description }}</p>
    <div class="mt-4"><slot /></div>
  </div>
</template>
