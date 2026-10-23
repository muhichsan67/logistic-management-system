<script setup>
import { onMounted, reactive, ref } from 'vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import FormField from '@/components/FormField.vue'
import { getSettings, updateSettings } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'
import { useAsync } from '@/utils/useAsync'
import { applyServerErrors, rule, runRules } from '@/utils/validate'

const online = useOnline()
const settings = useAsync(getSettings)
const form = reactive({ pending_alert_timeout_minutes: '', auto_complete_days: '' })
const errors = ref({})
const saving = ref(false)

onMounted(async () => {
  const data = await settings.run()
  if (data) Object.assign(form, data)
})

async function submit() {
  errors.value = runRules(form, {
    pending_alert_timeout_minutes: [rule.positiveInt('Timeout alert')],
    auto_complete_days: [rule.positiveInt('Hari auto-complete')],
  })
  if (Object.keys(errors.value).length) return
  saving.value = true
  try {
    await updateSettings({
      pending_alert_timeout_minutes: String(form.pending_alert_timeout_minutes).trim(),
      auto_complete_days: String(form.auto_complete_days).trim(),
    })
    toast.success('Pengaturan sistem berhasil disimpan')
  } catch (e) {
    applyServerErrors(errors.value, e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 class="mb-6 border-b pb-3 text-lg font-bold text-slate-800"><i class="fa-solid fa-sliders mr-2 text-navy" aria-hidden="true"></i> Konfigurasi Sistem Bisnis</h2>

    <LoadingState v-if="settings.loading.value && !settings.data.value" />
    <ErrorState v-else-if="settings.error.value" :message="settings.error.value" @retry="settings.run" />
    <form v-else class="space-y-6" novalidate @submit.prevent="submit">
      <FormField label="Visual Alert Timeout (menit)" for-id="timeout" :error="errors.pending_alert_timeout_minutes" hint="Lama status PENDING sebelum baris ditandai merah di tabel Admin.">
        <input id="timeout" v-model="form.pending_alert_timeout_minutes" type="number" min="1" step="1" inputmode="numeric" class="input !text-sm" :class="{ 'input-error': errors.pending_alert_timeout_minutes }" />
      </FormField>
      <FormField label="Auto-Complete (hari)" for-id="days" :error="errors.auto_complete_days" hint="Lama status DELIVERED sebelum otomatis menjadi COMPLETED oleh sistem.">
        <input id="days" v-model="form.auto_complete_days" type="number" min="1" step="1" inputmode="numeric" class="input !text-sm" :class="{ 'input-error': errors.auto_complete_days }" />
      </FormField>
      <div class="border-t border-slate-100 pt-4">
        <button type="submit" class="btn-primary !px-6 !py-3" :disabled="saving || !online">
          <i v-if="saving" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Simpan Konfigurasi
        </button>
      </div>
    </form>
  </div>
</template>
