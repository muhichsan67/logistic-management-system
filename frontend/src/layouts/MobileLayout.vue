<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Dipakai Customer & Kurir. Navigasi bawah mengikuti role; disembunyikan di halaman detail/form.
const route = useRoute()
const auth = useAuthStore()

const NAV = {
  CUSTOMER: [
    { to: '/customer', label: 'Beranda', icon: 'fa-house', exact: true },
    { to: '/customer/history', label: 'Riwayat', icon: 'fa-clock-rotate-left' },
    { to: '/customer/profile', label: 'Profil', icon: 'fa-user' },
  ],
  COURIER: [
    { to: '/courier', label: 'Tugas', icon: 'fa-list-check', exact: true },
    { to: '/courier/profile', label: 'Profil', icon: 'fa-user' },
  ],
}
const items = computed(() => NAV[auth.role] ?? [])
const showNav = computed(() => !route.meta.hideNav)
const active = (i) => (i.exact ? route.path === i.to : route.path.startsWith(i.to))
const activeColor = computed(() => (auth.role === 'COURIER' ? 'text-emerald-700' : 'text-navy'))
</script>

<template>
  <div class="relative mx-auto min-h-screen max-w-md bg-slate-50 shadow-2xl">
    <main :class="showNav ? 'pb-24' : 'pb-6'" class="animate-fade-in">
      <RouterView />
    </main>

    <nav v-if="showNav" aria-label="Menu utama"
      class="fixed bottom-0 left-1/2 z-40 flex w-full max-w-md -translate-x-1/2 justify-around border-t border-slate-200 bg-white px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2 shadow-[0_-5px_15px_-10px_rgba(0,0,0,0.15)]">
      <RouterLink v-for="i in items" :key="i.to" :to="i.to"
        class="flex min-h-[48px] flex-1 flex-col items-center justify-center gap-0.5 rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-navy"
        :class="active(i) ? activeColor : 'text-slate-500'" :aria-current="active(i) ? 'page' : undefined">
        <i class="fa-solid text-xl" :class="i.icon" aria-hidden="true"></i>
        <span class="text-xs" :class="active(i) ? 'font-bold' : 'font-semibold'">{{ i.label }}</span>
      </RouterLink>
    </nav>
  </div>
</template>
