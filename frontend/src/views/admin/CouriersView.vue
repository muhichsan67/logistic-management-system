<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import FormField from '@/components/FormField.vue'
import { createCourier, deactivateCourier, getCouriers, updateCourier } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'
import { applyServerErrors, rule, runRules } from '@/utils/validate'
import { formatDate } from '@/utils/format'

const online = useOnline()
const q = ref('')
const active = ref('') // '' | 'true' | 'false'
const rows = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await getCouriers({ q: q.value.trim(), is_active: active.value, page: page.value, limit: limit.value })
    rows.value = res.items
    total.value = res.total
  } catch (e) {
    error.value = e.userMessage
  } finally {
    loading.value = false
  }
}
const onPage = (e) => { page.value = e.page + 1; limit.value = e.rows; load() }
let timer
watch(q, () => { clearTimeout(timer); timer = setTimeout(() => { page.value = 1; load() }, 400) })
watch(active, () => { page.value = 1; load() })
onMounted(load)

// ---- Dialog tambah / ubah ----
const showForm = ref(false)
const editing = ref(null) // null = tambah baru
const form = reactive({ name: '', email: '', phone: '', password: '' })
const errors = ref({})
const submitting = ref(false)

function openForm(courier = null) {
  editing.value = courier
  Object.assign(form, { name: courier?.name ?? '', email: courier?.email ?? '', phone: courier?.phone ?? '', password: '' })
  errors.value = {}
  showForm.value = true
}

async function submit() {
  const isEdit = !!editing.value
  const optional = (fn) => (v) => (String(v ?? '').trim() ? fn(v) : '')
  errors.value = runRules(form, isEdit
    ? { name: [optional(rule.name('Nama'))], email: [optional(rule.email)], phone: [optional(rule.phone)], password: [optional(rule.password)] }
    : { name: [rule.required('Nama'), rule.name('Nama')], email: [rule.required('Email'), rule.email], phone: [rule.required('No. telepon'), rule.phone], password: [rule.required('Password'), rule.password] })
  if (Object.keys(errors.value).length) return

  const payload = { name: form.name.trim(), email: form.email.trim().toLowerCase(), phone: form.phone.trim(), password: form.password }
  if (isEdit) {
    // kirim hanya field yang berubah (password hanya bila diisi)
    for (const k of ['name', 'email', 'phone']) if (!payload[k] || payload[k] === editing.value[k]) delete payload[k]
    if (!payload.password) delete payload.password
    if (!Object.keys(payload).length) {
      toast.info('Tidak ada perubahan')
      return
    }
  }
  submitting.value = true
  try {
    if (isEdit) await updateCourier(editing.value.id, payload)
    else await createCourier(payload)
    toast.success(isEdit ? 'Data kurir diperbarui' : 'Kurir berhasil ditambahkan')
    showForm.value = false
    load()
  } catch (e) {
    applyServerErrors(errors.value, e)
  } finally {
    submitting.value = false
  }
}

// ---- Dialog nonaktifkan (soft delete, bukan hapus permanen) ----
const showDeactivate = ref(false)
const target = ref(null)
const deactivating = ref(false)
const askDeactivate = (c) => { target.value = c; showDeactivate.value = true }

async function doDeactivate() {
  deactivating.value = true
  try {
    await deactivateCourier(target.value.id)
    toast.success(`${target.value.name} dinonaktifkan`)
    showDeactivate.value = false
    load()
  } catch {
    /* toast dari interceptor */
  } finally {
    deactivating.value = false
  }
}
</script>

<template>
  <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div class="flex flex-wrap items-end gap-3">
        <div>
          <label for="c-q" class="mb-1 block text-xs font-bold text-slate-600">Cari</label>
          <input id="c-q" v-model="q" type="search" placeholder="Nama / email..." class="input !w-64 !p-2 !text-sm" />
        </div>
        <div>
          <label for="c-active" class="mb-1 block text-xs font-bold text-slate-600">Status akun</label>
          <select id="c-active" v-model="active" class="input !w-40 !p-2 !text-sm">
            <option value="">Semua</option><option value="true">Aktif</option><option value="false">Nonaktif</option>
          </select>
        </div>
      </div>
      <button type="button" class="btn-success" @click="openForm()"><i class="fa-solid fa-plus" aria-hidden="true"></i> Tambah Kurir</button>
    </div>

    <ErrorState v-if="error" :message="error" @retry="load" />
    <DataTable v-else :value="rows" :loading="loading" lazy paginator :rows="limit" :total-records="total" :first="(page - 1) * limit"
      :rows-per-page-options="[10, 20, 50]" data-key="id" size="small" @page="onPage">
      <template #empty><EmptyState icon="fa-motorcycle" title="Belum ada kurir" description="Klik Tambah Kurir untuk membuat akun kurir." /></template>
      <Column header="Nama"><template #body="{ data }"><span class="font-semibold text-slate-800">{{ data.name }}</span></template></Column>
      <Column field="email" header="Email" />
      <Column field="phone" header="Telepon" />
      <Column header="Status">
        <template #body="{ data }">
          <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold" :class="data.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-200 text-slate-700'">
            <i class="fa-solid text-[10px]" :class="data.is_active ? 'fa-circle-check' : 'fa-ban'" aria-hidden="true"></i>{{ data.is_active ? 'Aktif' : 'Nonaktif' }}
          </span>
        </template>
      </Column>
      <Column header="Dibuat"><template #body="{ data }">{{ formatDate(data.created_at) }}</template></Column>
      <Column header="Aksi">
        <template #body="{ data }">
          <div class="flex gap-2 whitespace-nowrap">
            <button type="button" class="btn-secondary !min-h-0 !px-3 !py-1.5 !text-xs" @click="openForm(data)"><i class="fa-solid fa-pen" aria-hidden="true"></i> Ubah</button>
            <button v-if="data.is_active" type="button" class="btn-outline-danger !min-h-0 !px-3 !py-1.5 !text-xs" @click="askDeactivate(data)"><i class="fa-solid fa-user-slash" aria-hidden="true"></i> Nonaktifkan</button>
          </div>
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showForm" modal :header="editing ? 'Ubah Data Kurir' : 'Tambah Kurir'" :style="{ width: '28rem' }" :draggable="false">
      <form class="space-y-4" novalidate @submit.prevent="submit">
        <FormField label="Nama Lengkap" for-id="k-name" :error="errors.name"><input id="k-name" v-model="form.name" type="text" class="input !text-sm" :class="{ 'input-error': errors.name }" /></FormField>
        <FormField label="Email" for-id="k-email" :error="errors.email"><input id="k-email" v-model="form.email" type="email" class="input !text-sm" :class="{ 'input-error': errors.email }" /></FormField>
        <FormField label="No. Telepon" for-id="k-phone" :error="errors.phone"><input id="k-phone" v-model="form.phone" type="tel" class="input !text-sm" :class="{ 'input-error': errors.phone }" /></FormField>
        <FormField :label="editing ? 'Password Baru' : 'Password'" for-id="k-pass" :error="errors.password" :hint="editing ? 'Kosongkan jika tidak diubah. Mengubah password memaksa kurir login ulang.' : 'Minimal 8 karakter, memuat huruf dan angka'">
          <input id="k-pass" v-model="form.password" type="password" autocomplete="new-password" class="input !text-sm" :class="{ 'input-error': errors.password }" />
        </FormField>
        <div class="flex gap-3">
          <button type="button" class="btn-secondary flex-1" @click="showForm = false">Batal</button>
          <button type="submit" class="btn-primary flex-1" :disabled="submitting || !online"><i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Simpan</button>
        </div>
      </form>
    </Dialog>

    <Dialog v-model:visible="showDeactivate" modal header="Nonaktifkan Kurir?" :style="{ width: '26rem' }" :draggable="false">
      <p class="mb-5 text-sm text-slate-600">
        <strong>{{ target?.name }}</strong> tidak akan bisa login dan tidak bisa ditugaskan lagi. Riwayat pengiriman tetap tersimpan.
      </p>
      <div class="flex gap-3">
        <button type="button" class="btn-secondary flex-1" @click="showDeactivate = false">Batal</button>
        <button type="button" class="btn-danger flex-1" :disabled="deactivating || !online" @click="doDeactivate"><i v-if="deactivating" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Nonaktifkan</button>
      </div>
    </Dialog>
  </div>
</template>
