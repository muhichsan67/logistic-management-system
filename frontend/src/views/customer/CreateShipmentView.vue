<script setup>
import { onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import FormField from '@/components/FormField.vue'
import { createShipment, getMe } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'
import { askNotificationPermissionOnce } from '@/utils/push'
import { applyServerErrors, rule, runRules } from '@/utils/validate'

const online = useOnline()
const form = reactive({
  sender_name: '', sender_phone: '', origin_address: '',
  recipient_name: '', recipient_phone: '', destination_address: '',
  package_description: '', weight_kg: '',
})
const errors = ref({})
const submitting = ref(false)
const created = ref(null) // { tracking_number, ... } setelah sukses
const copied = ref(false)

// Prefill pengirim dari akun (boleh diubah)
onMounted(async () => {
  try {
    const me = await getMe()
    form.sender_name ||= me.name
    form.sender_phone ||= me.phone
  } catch {
    /* prefill opsional */
  }
})

async function submit() {
  errors.value = runRules(form, {
    sender_name: [rule.required('Nama pengirim'), rule.name('Nama pengirim')],
    sender_phone: [rule.required('No. HP pengirim'), rule.phone],
    origin_address: [rule.required('Alamat asal')],
    recipient_name: [rule.required('Nama penerima'), rule.name('Nama penerima')],
    recipient_phone: [rule.required('No. HP penerima'), rule.phone],
    destination_address: [rule.required('Alamat tujuan')],
    package_description: [rule.required('Deskripsi paket')],
    weight_kg: [rule.weight],
  })
  if (Object.keys(errors.value).length) {
    document.querySelector('[aria-invalid="true"]')?.focus()
    return
  }
  submitting.value = true
  try {
    created.value = await createShipment({
      sender_name: form.sender_name.trim(), sender_phone: form.sender_phone.trim(), origin_address: form.origin_address.trim(),
      recipient_name: form.recipient_name.trim(), recipient_phone: form.recipient_phone.trim(), destination_address: form.destination_address.trim(),
      package_description: form.package_description.trim(), weight_kg: Number(String(form.weight_kg).replace(',', '.')),
    })
    askNotificationPermissionOnce() // setelah aksi pertama, bukan saat app dibuka
  } catch (e) {
    applyServerErrors(errors.value, e)
  } finally {
    submitting.value = false
  }
}

async function copy() {
  try {
    await navigator.clipboard.writeText(created.value.tracking_number)
    copied.value = true
    toast.success('Nomor resi disalin')
  } catch {
    toast.info('Salin manual nomor resi di atas')
  }
}
</script>

<template>
  <div>
    <PageHeader title="Buat Pengiriman Baru" back-to="/customer" />

    <!-- Sukses: tampilkan nomor resi -->
    <div v-if="created" class="animate-fade-in px-5 py-10 text-center">
      <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-green-100 text-4xl text-green-700"><i class="fa-solid fa-check" aria-hidden="true"></i></div>
      <h2 class="text-xl font-bold text-slate-800">Permintaan Berhasil Dibuat</h2>
      <p class="mt-1 text-sm text-slate-500">Menunggu konfirmasi Admin. Simpan nomor resi Anda:</p>
      <p class="my-5 rounded-2xl bg-white py-5 font-mono text-2xl font-bold text-navy shadow-sm">{{ created.tracking_number }}</p>
      <div class="space-y-3">
        <button type="button" class="btn-secondary w-full" @click="copy"><i class="fa-regular fa-copy" aria-hidden="true"></i> {{ copied ? 'Tersalin' : 'Salin Nomor Resi' }}</button>
        <RouterLink :to="`/customer/shipments/${created.tracking_number}`" class="btn-primary w-full">Lihat Detail</RouterLink>
        <RouterLink to="/customer" class="btn w-full text-navy">Kembali ke Beranda</RouterLink>
      </div>
    </div>

    <form v-else class="space-y-5 px-5 py-5" novalidate @submit.prevent="submit">
      <section class="space-y-3 rounded-xl border border-slate-100 bg-white p-4" aria-labelledby="sec-sender">
        <h2 id="sec-sender" class="flex items-center gap-2 text-sm font-bold text-slate-700"><i class="fa-solid fa-circle-dot text-slate-400" aria-hidden="true"></i> Detail Pengirim</h2>
        <FormField label="Nama Pengirim" for-id="sender_name" :error="errors.sender_name">
          <input id="sender_name" v-model="form.sender_name" type="text" class="input" :class="{ 'input-error': errors.sender_name }" :aria-invalid="!!errors.sender_name" />
        </FormField>
        <FormField label="No. HP Pengirim" for-id="sender_phone" :error="errors.sender_phone">
          <input id="sender_phone" v-model="form.sender_phone" type="tel" inputmode="tel" class="input" :class="{ 'input-error': errors.sender_phone }" :aria-invalid="!!errors.sender_phone" />
        </FormField>
        <FormField label="Alamat Asal (Penjemputan)" for-id="origin_address" :error="errors.origin_address">
          <textarea id="origin_address" v-model="form.origin_address" rows="3" class="input" :class="{ 'input-error': errors.origin_address }" :aria-invalid="!!errors.origin_address"></textarea>
        </FormField>
      </section>

      <section class="space-y-3 rounded-xl border border-slate-100 bg-white p-4" aria-labelledby="sec-recipient">
        <h2 id="sec-recipient" class="flex items-center gap-2 text-sm font-bold text-slate-700"><i class="fa-solid fa-location-dot text-amber" aria-hidden="true"></i> Detail Penerima</h2>
        <FormField label="Nama Penerima" for-id="recipient_name" :error="errors.recipient_name">
          <input id="recipient_name" v-model="form.recipient_name" type="text" class="input" :class="{ 'input-error': errors.recipient_name }" :aria-invalid="!!errors.recipient_name" />
        </FormField>
        <FormField label="No. HP / WhatsApp Penerima" for-id="recipient_phone" :error="errors.recipient_phone">
          <input id="recipient_phone" v-model="form.recipient_phone" type="tel" inputmode="tel" class="input" :class="{ 'input-error': errors.recipient_phone }" :aria-invalid="!!errors.recipient_phone" />
        </FormField>
        <FormField label="Alamat Lengkap Tujuan" for-id="destination_address" :error="errors.destination_address">
          <textarea id="destination_address" v-model="form.destination_address" rows="3" class="input" :class="{ 'input-error': errors.destination_address }" :aria-invalid="!!errors.destination_address"></textarea>
        </FormField>
      </section>

      <section class="space-y-3 rounded-xl border border-slate-100 bg-white p-4" aria-labelledby="sec-pkg">
        <h2 id="sec-pkg" class="flex items-center gap-2 text-sm font-bold text-slate-700"><i class="fa-solid fa-box text-navy" aria-hidden="true"></i> Detail Barang</h2>
        <FormField label="Deskripsi Isi Paket" for-id="package_description" :error="errors.package_description">
          <textarea id="package_description" v-model="form.package_description" rows="2" placeholder="Cth: Pakaian, Dokumen" class="input" :class="{ 'input-error': errors.package_description }" :aria-invalid="!!errors.package_description"></textarea>
        </FormField>
        <FormField label="Berat Estimasi" for-id="weight_kg" :error="errors.weight_kg">
          <div class="relative">
            <input id="weight_kg" v-model="form.weight_kg" type="text" inputmode="decimal" class="input pr-14" :class="{ 'input-error': errors.weight_kg }" :aria-invalid="!!errors.weight_kg" />
            <span class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-sm font-bold text-slate-500">KG</span>
          </div>
        </FormField>
      </section>

      <button type="submit" class="btn-primary w-full !py-4 text-base shadow-lg" :disabled="submitting || !online">
        <i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i>
        {{ submitting ? 'Mengirim...' : 'Ajukan Pengiriman' }}
        <i v-if="!submitting" class="fa-solid fa-check" aria-hidden="true"></i>
      </button>
    </form>
  </div>
</template>
