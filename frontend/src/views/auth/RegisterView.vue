<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/FormField.vue'
import { register } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'
import { applyServerErrors, rule, runRules } from '@/utils/validate'

const router = useRouter()
const online = useOnline()

const form = reactive({ name: '', email: '', phone: '', password: '', confirm: '' })
const errors = ref({})
const submitting = ref(false)

async function submit() {
  errors.value = runRules(form, {
    name: [rule.required('Nama'), rule.name('Nama')],
    email: [rule.required('Email'), rule.email],
    phone: [rule.required('No. telepon'), rule.phone],
    password: [rule.required('Password'), rule.password],
    confirm: [rule.same(() => form.password, 'Konfirmasi password tidak sama')],
  })
  if (Object.keys(errors.value).length) return
  submitting.value = true
  try {
    await register({ name: form.name.trim(), email: form.email.trim().toLowerCase(), phone: form.phone.trim(), password: form.password })
    toast.success('Registrasi berhasil. Silakan masuk.')
    router.replace('/login')
  } catch (e) {
    applyServerErrors(errors.value, e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-white px-4 py-8">
    <div class="w-full max-w-md p-4 sm:p-8">
      <div class="mb-6 text-center">
        <div class="mb-2 text-4xl text-navy"><i class="fa-solid fa-box-open" aria-hidden="true"></i></div>
        <h1 class="text-2xl font-bold text-navy">Buat Akun</h1>
        <p class="mt-1 text-sm text-slate-500">Daftar sebagai Customer LajuLogistik</p>
      </div>

      <form class="space-y-4" novalidate @submit.prevent="submit">
        <FormField label="Nama Lengkap" for-id="name" :error="errors.name">
          <input id="name" v-model="form.name" type="text" autocomplete="name" class="input" :class="{ 'input-error': errors.name }" />
        </FormField>
        <FormField label="Email" for-id="email" :error="errors.email">
          <input id="email" v-model="form.email" type="email" autocomplete="email" inputmode="email" class="input" :class="{ 'input-error': errors.email }" />
        </FormField>
        <FormField label="No. HP / WhatsApp" for-id="phone" :error="errors.phone" hint="Angka saja, 8-20 karakter (boleh diawali +)">
          <input id="phone" v-model="form.phone" type="tel" autocomplete="tel" inputmode="tel" class="input" :class="{ 'input-error': errors.phone }" />
        </FormField>
        <FormField label="Password" for-id="password" :error="errors.password" hint="Minimal 8 karakter, memuat huruf dan angka">
          <input id="password" v-model="form.password" type="password" autocomplete="new-password" class="input" :class="{ 'input-error': errors.password }" />
        </FormField>
        <FormField label="Ulangi Password" for-id="confirm" :error="errors.confirm">
          <input id="confirm" v-model="form.confirm" type="password" autocomplete="new-password" class="input" :class="{ 'input-error': errors.confirm }" />
        </FormField>

        <button type="submit" class="btn-primary w-full !py-3 text-base shadow-md" :disabled="submitting || !online">
          <i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i>
          {{ submitting ? 'Memproses...' : 'Daftar' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-slate-600">
        Sudah punya akun? <RouterLink to="/login" class="font-bold text-navy underline">Masuk</RouterLink>
      </p>
    </div>
  </div>
</template>
