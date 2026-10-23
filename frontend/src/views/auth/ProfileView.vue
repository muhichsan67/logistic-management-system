<script setup>
import { onMounted } from 'vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import { getMe } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useAsync } from '@/utils/useAsync'
import { logout } from '@/utils/session'
import { ROLE_LABEL, formatDate, initials } from '@/utils/format'

// Dipakai Customer & Kurir. Backend belum punya endpoint ubah profil -> hanya lihat + keluar.
const auth = useAuthStore()
const me = useAsync(getMe)
onMounted(me.run)
</script>

<template>
  <div>
    <div class="rounded-b-3xl px-5 pb-8 pt-8 text-center text-white shadow-md" :class="auth.role === 'COURIER' ? 'bg-emerald-600' : 'bg-navy'">
      <div class="mx-auto mb-3 flex h-24 w-24 items-center justify-center rounded-full bg-white/20 text-3xl font-bold" aria-hidden="true">{{ initials(auth.name) }}</div>
      <h1 class="text-xl font-bold">{{ auth.name }}</h1>
      <p class="text-sm opacity-90">{{ ROLE_LABEL[auth.role] }}</p>
    </div>

    <div class="px-5 py-6">
      <LoadingState v-if="me.loading.value && !me.data.value" />
      <ErrorState v-else-if="me.error.value" :message="me.error.value" @retry="me.run" />
      <div v-else-if="me.data.value" class="card p-5">
        <h2 class="mb-4 border-b pb-2 font-bold text-navy">Informasi Pribadi</h2>
        <dl class="space-y-4 text-sm">
          <div><dt class="text-xs font-semibold text-slate-500">Nama Lengkap</dt><dd class="font-semibold">{{ me.data.value.name }}</dd></div>
          <div><dt class="text-xs font-semibold text-slate-500">Email</dt><dd class="font-semibold">{{ me.data.value.email }}</dd></div>
          <div><dt class="text-xs font-semibold text-slate-500">No. WhatsApp</dt><dd class="font-semibold">{{ me.data.value.phone }}</dd></div>
          <div><dt class="text-xs font-semibold text-slate-500">Member sejak</dt><dd class="font-semibold">{{ formatDate(me.data.value.created_at) }}</dd></div>
        </dl>
      </div>

      <button type="button" class="btn-outline-danger mt-4 w-full !py-3" @click="logout">
        <i class="fa-solid fa-arrow-right-from-bracket" aria-hidden="true"></i> Keluar Akun
      </button>
    </div>
  </div>
</template>
