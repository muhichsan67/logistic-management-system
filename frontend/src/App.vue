<script setup>
import ToastHost from '@/components/ToastHost.vue'
import { useOnline } from '@/utils/online'

const online = useOnline()
</script>

<template>
  <div v-if="!online" role="status" class="fixed inset-x-0 top-0 z-[100] bg-slate-900 px-4 py-2 text-center text-sm font-semibold text-white">
    <i class="fa-solid fa-triangle-exclamation mr-1 text-amber" aria-hidden="true"></i>
    Anda sedang offline. Aksi yang mengubah data dinonaktifkan.
  </div>
  <RouterView />
  <ToastHost />
</template>
