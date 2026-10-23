<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import AssignDialog from '@/components/AssignDialog.vue'
import RejectDialog from '@/components/RejectDialog.vue'
import ShipmentDetailDialog from '@/components/ShipmentDetailDialog.vue'
import { getAdminShipments, getCouriers } from '@/api'
import { STATUS, STATUS_LIST, formatDateTime, timeAgo } from '@/utils/format'

const filters = reactive({ q: '', status: '', courier_id: '', date_from: '', date_to: '' })
const rows = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const loading = ref(false)
const error = ref('')
const couriers = ref([])

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await getAdminShipments({ ...filters, page: page.value, limit: limit.value })
    rows.value = res.items
    total.value = res.total
  } catch (e) {
    error.value = e.userMessage
  } finally {
    loading.value = false
  }
}

function onPage(e) {
  page.value = e.page + 1
  limit.value = e.rows
  load()
}

// Filter berubah -> kembali ke halaman 1. Pencarian teks di-debounce.
let timer
watch(() => filters.q, () => { clearTimeout(timer); timer = setTimeout(() => { page.value = 1; load() }, 400) })
watch(() => [filters.status, filters.courier_id, filters.date_from, filters.date_to], () => { page.value = 1; load() })

onMounted(async () => {
  load()
  try { couriers.value = (await getCouriers({ limit: 100 })).items } catch { /* filter kurir opsional */ }
})

const rowClass = (r) => (r.is_overdue_pending ? 'row-overdue' : '')

const assignTarget = ref(null); const showAssign = ref(false)
const rejectTarget = ref(null); const showReject = ref(false)
const detailId = ref(null); const showDetail = ref(false)
const openAssign = (s) => { assignTarget.value = s; showAssign.value = true }
const openReject = (s) => { rejectTarget.value = s; showReject.value = true }
const openDetail = (s) => { detailId.value = s.id; showDetail.value = true }
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
    <div class="flex flex-wrap items-end gap-3 border-b border-slate-200 bg-slate-50 p-5">
      <div>
        <label for="f-q" class="mb-1 block text-xs font-bold text-slate-600">Cari</label>
        <input id="f-q" v-model="filters.q" type="search" placeholder="No. resi / nama..." class="input !w-64 !p-2 !text-sm" />
      </div>
      <div>
        <label for="f-status" class="mb-1 block text-xs font-bold text-slate-600">Status</label>
        <select id="f-status" v-model="filters.status" class="input !w-44 !p-2 !text-sm">
          <option value="">Semua Status</option>
          <option v-for="s in STATUS_LIST" :key="s" :value="s">{{ STATUS[s].label }}</option>
        </select>
      </div>
      <div>
        <label for="f-courier" class="mb-1 block text-xs font-bold text-slate-600">Kurir</label>
        <select id="f-courier" v-model="filters.courier_id" class="input !w-44 !p-2 !text-sm">
          <option value="">Semua Kurir</option>
          <option v-for="c in couriers" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div>
        <label for="f-from" class="mb-1 block text-xs font-bold text-slate-600">Dari tanggal</label>
        <input id="f-from" v-model="filters.date_from" type="date" class="input !w-40 !p-2 !text-sm" />
      </div>
      <div>
        <label for="f-to" class="mb-1 block text-xs font-bold text-slate-600">Sampai tanggal</label>
        <input id="f-to" v-model="filters.date_to" type="date" :min="filters.date_from" class="input !w-40 !p-2 !text-sm" />
      </div>
    </div>

    <ErrorState v-if="error" :message="error" @retry="load" />
    <DataTable v-else :value="rows" :loading="loading" lazy paginator :rows="limit" :total-records="total" :first="(page - 1) * limit"
      :rows-per-page-options="[10, 20, 50]" data-key="id" :row-class="rowClass" size="small" @page="onPage">
      <template #empty><EmptyState title="Tidak ada pengiriman" description="Ubah filter atau tunggu permintaan baru." /></template>

      <Column header="No. Resi">
        <template #body="{ data }">
          <span class="font-mono font-bold" :class="data.is_overdue_pending ? 'text-danger' : 'text-navy'">
            <i v-if="data.is_overdue_pending" class="fa-solid fa-triangle-exclamation mr-1" title="PENDING melebihi batas waktu" aria-hidden="true"></i>
            <span v-if="data.is_overdue_pending" class="sr-only">Terlambat diproses. </span>{{ data.tracking_number }}
          </span>
        </template>
      </Column>
      <Column header="Customer"><template #body="{ data }"><span class="font-semibold text-slate-700">{{ data.customer_name }}</span></template></Column>
      <Column header="Kurir"><template #body="{ data }">{{ data.courier_name || '-' }}</template></Column>
      <Column header="Status"><template #body="{ data }"><StatusBadge :status="data.status" /></template></Column>
      <Column header="Dibuat">
        <template #body="{ data }">
          <span :class="data.is_overdue_pending ? 'font-bold text-danger' : 'text-slate-600'">{{ formatDateTime(data.created_at) }}</span>
          <br /><span class="text-xs text-slate-500">{{ timeAgo(data.created_at) }}</span>
        </template>
      </Column>
      <Column header="Aksi" body-class="text-center">
        <template #body="{ data }">
          <div class="flex justify-center gap-2 whitespace-nowrap">
            <template v-if="data.status === 'PENDING'">
              <button type="button" class="btn-primary !min-h-0 !px-3 !py-1.5 !text-xs" @click="openAssign(data)">Assign</button>
              <button type="button" class="btn-outline-danger !min-h-0 !px-3 !py-1.5 !text-xs" @click="openReject(data)">Tolak</button>
            </template>
            <button type="button" class="btn-secondary !min-h-0 !px-3 !py-1.5 !text-xs" :aria-label="`Detail ${data.tracking_number}`" @click="openDetail(data)"><i class="fa-solid fa-eye" aria-hidden="true"></i></button>
          </div>
        </template>
      </Column>
    </DataTable>

    <AssignDialog v-model="showAssign" :shipment="assignTarget" @done="load" />
    <RejectDialog v-model="showReject" :shipment="rejectTarget" @done="load" />
    <ShipmentDetailDialog v-model="showDetail" :shipment-id="detailId" />
  </div>
</template>
