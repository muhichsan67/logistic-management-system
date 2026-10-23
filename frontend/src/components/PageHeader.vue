<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, required: true },
  backTo: { type: String, default: '/' }, // dipakai bila tidak ada riwayat navigasi
  tone: { type: String, default: 'navy' }, // navy | emerald
})
const router = useRouter()
const back = () => (window.history.state?.back ? router.back() : router.push(props.backTo))
</script>

<template>
  <header class="sticky top-0 z-30 flex items-center gap-2 px-3 py-3 text-white shadow" :class="tone === 'emerald' ? 'bg-emerald-600' : 'bg-navy'">
    <button type="button" class="flex h-11 w-11 items-center justify-center rounded-full hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-white" aria-label="Kembali" @click="back">
      <i class="fa-solid fa-arrow-left" aria-hidden="true"></i>
    </button>
    <h1 class="flex-1 truncate text-lg font-bold">{{ title }}</h1>
    <slot />
  </header>
</template>
