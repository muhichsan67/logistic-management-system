<script setup>
defineProps({ message: { type: String, default: 'Terjadi kesalahan, coba lagi' } })
defineEmits(['retry'])
</script>

<template>
  <div role="alert" class="flex flex-col items-center px-6 py-12 text-center">
    <div class="mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-red-50 text-2xl text-danger">
      <i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
    </div>
    <p class="font-bold text-slate-700">Gagal memuat data</p>
    <p class="mt-1 text-sm text-slate-500">{{ message }}</p>
    <button type="button" class="btn-primary mt-4" @click="$emit('retry')">
      <i class="fa-solid fa-rotate-right" aria-hidden="true"></i> Coba Lagi
    </button>
  </div>
</template>
