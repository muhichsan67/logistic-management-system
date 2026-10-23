<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/FormField.vue'
import { login } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useOnline } from '@/utils/online'
import { rule, runRules } from '@/utils/validate'

const router = useRouter()
const auth = useAuthStore()
const online = useOnline()

const form = reactive({ email: '', password: '' })
const errors = ref({})
const submitting = ref(false)
const showPassword = ref(false)

async function submit() {
  errors.value = runRules(form, {
    email: [rule.required('Email'), rule.email],
    password: [rule.required('Password')],
  })
  if (Object.keys(errors.value).length) return
  submitting.value = true
  try {
    auth.setSession(await login(form.email.trim().toLowerCase(), form.password))
    router.replace(auth.homePath) // CUSTOMER /customer, COURIER /courier, ADMIN /admin
  } catch {
    /* pesan ditampilkan interceptor */
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-white px-4">
    <div class="w-full max-w-md p-4 sm:p-8">
      <div class="mb-8 text-center">
        <div class="mb-2 text-4xl text-navy"><i class="fa-solid fa-box-open" aria-hidden="true"></i></div>
        <h1 class="text-2xl font-bold text-navy">LajuLogistik</h1>
        <p class="mt-1 text-sm text-slate-500">Masuk untuk mengirim dan melacak paket</p>
      </div>

      <form class="space-y-4" novalidate @submit.prevent="submit">
        <FormField label="Email" for-id="email" :error="errors.email">
          <input id="email" v-model="form.email" type="email" autocomplete="username" inputmode="email" class="input" :class="{ 'input-error': errors.email }" :aria-invalid="!!errors.email" />
        </FormField>
        <FormField label="Password" for-id="password" :error="errors.password">
          <div class="relative">
            <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" class="input pr-12" :class="{ 'input-error': errors.password }" :aria-invalid="!!errors.password" />
            <button type="button" class="absolute right-1 top-1/2 flex h-11 w-11 -translate-y-1/2 items-center justify-center text-slate-500" :aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'" @click="showPassword = !showPassword">
              <i class="fa-solid" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'" aria-hidden="true"></i>
            </button>
          </div>
        </FormField>

        <button type="submit" class="btn-primary w-full !py-3 text-base shadow-md" :disabled="submitting || !online">
          <i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i>
          {{ submitting ? 'Memproses...' : 'Masuk' }}
          <i v-if="!submitting" class="fa-solid fa-arrow-right" aria-hidden="true"></i>
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-slate-600">
        Belum punya akun? <RouterLink to="/register" class="font-bold text-navy underline">Daftar di sini</RouterLink>
      </p>
      <p class="mt-3 text-center text-sm text-slate-600">
        Hanya ingin melacak paket? <RouterLink to="/track" class="font-bold text-navy underline">Lacak resi</RouterLink>
      </p>
    </div>
  </div>
</template>
