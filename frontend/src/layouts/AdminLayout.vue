<script setup>
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { logout } from '@/utils/session'
import { initials } from '@/utils/format'

const route = useRoute()
const auth = useAuthStore()

const NAV = [
  { to: '/admin', label: 'Dashboard', icon: 'fa-chart-pie', exact: true },
  { to: '/admin/shipments', label: 'Semua Pengiriman', icon: 'fa-table-list' },
  { to: '/admin/couriers', label: 'Data Kurir', icon: 'fa-users' },
  { to: '/admin/settings', label: 'Pengaturan Sistem', icon: 'fa-gear' },
]
const active = (i) => (i.exact ? route.path === i.to : route.path.startsWith(i.to))
</script>

<template>
  <!-- Desktop (>= 1024 px). Di layar lebih kecil konten bisa digulir horizontal. -->
  <div class="flex min-h-screen min-w-[1024px] bg-slate-100">
    <aside class="fixed z-20 flex min-h-screen w-64 flex-col bg-navy text-white shadow-xl">
      <div class="flex items-center gap-3 border-b border-blue-800 p-6">
        <i class="fa-solid fa-box-open text-2xl text-amber" aria-hidden="true"></i>
        <span class="text-xl font-bold tracking-wide">LajuLogistik</span>
      </div>
      <nav aria-label="Menu admin" class="mt-6 flex-1 space-y-1 px-3">
        <RouterLink v-for="i in NAV" :key="i.to" :to="i.to"
          class="flex w-full items-center gap-3 rounded-lg px-4 py-3 font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
          :class="active(i) ? 'bg-blue-800 text-white' : 'text-blue-100 hover:bg-blue-800/50 hover:text-white'"
          :aria-current="active(i) ? 'page' : undefined">
          <i class="fa-solid w-5" :class="i.icon" aria-hidden="true"></i>{{ i.label }}
        </RouterLink>
      </nav>
      <div class="border-t border-blue-800 p-4">
        <button type="button" class="flex w-full items-center gap-3 rounded-lg px-4 py-2 font-medium text-red-200 transition hover:bg-red-500/20" @click="logout">
          <i class="fa-solid fa-arrow-right-from-bracket w-5" aria-hidden="true"></i>Keluar
        </button>
      </div>
    </aside>

    <div class="ml-64 flex min-w-0 flex-1 flex-col">
      <header class="z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-8 shadow-sm">
        <h1 class="text-lg font-bold text-slate-800">{{ route.meta.title }}</h1>
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-full bg-navy text-sm font-bold text-white" aria-hidden="true">{{ initials(auth.name) }}</div>
          <span class="text-sm font-bold text-slate-700">{{ auth.name }}</span>
        </div>
      </header>
      <main class="animate-fade-in p-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>
