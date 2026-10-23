<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import EmptyState from '@/components/EmptyState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import BarChart from '@/components/BarChart.vue'
import AssignDialog from '@/components/AssignDialog.vue'
import RejectDialog from '@/components/RejectDialog.vue'
import ShipmentDetailDialog from '@/components/ShipmentDetailDialog.vue'
import { getAdminShipments, getDashboardSummary } from '@/api'
import { useAsync } from '@/utils/useAsync'
import { STATUS, STATUS_LIST, formatDateTime, formatDayMonth, formatMonthYear, timeAgo } from '@/utils/format'

const PERIODS = [{ v: '7d', l: '7 Hari' }, { v: '30d', l: '30 Hari' }, { v: '12m', l: '12 Bulan' }]
const period = ref('7d')

const summary = useAsync(() => getDashboardSummary(period.value))
const pending = useAsync(() => getAdminShipments({ status: 'PENDING', limit: 5 }))

onMounted(() => { summary.run(); pending.run() })
watch(period, () => summary.run())

const cards = computed(() => {
  const t = summary.data.value?.totals
  return [
    { label: 'Menunggu', value: t?.pending, border: 'border-l-amber' },
    { label: 'Dalam Proses', value: t?.active, border: 'border-l-blue-500' },
    { label: 'Terkirim Hari Ini', value: t?.delivered_today, border: 'border-l-success' },
    { label: 'Selesai', value: t?.completed, border: 'border-l-navy' },
  ]
})
const volume = computed(() =>
  (summary.data.value?.volume_per_day ?? []).map((p) => ({ label: period.value === '12m' ? formatMonthYear(p.date) : formatDayMonth(p.date), value: p.count })),
)
const byStatus = computed(() => STATUS_LIST.map((s) => ({ label: STATUS[s].label, value: summary.data.value?.by_status?.[s] ?? 0, color: STATUS[s].dot })))

// Dialog aksi
const assignTarget = ref(null); const showAssign = ref(false)
const rejectTarget = ref(null); const showReject = ref(false)
const detailId = ref(null); const showDetail = ref(false)
const openAssign = (s) => { assignTarget.value = s; showAssign.value = true }
const openReject = (s) => { rejectTarget.value = s; showReject.value = true }
const openDetail = (s) => { detailId.value = s.id; showDetail.value = true }
const refresh = () => { summary.run(); pending.run() }
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-slate-800">Ringkasan</h2>
      <div class="inline-flex rounded-lg bg-slate-200 p-1" role="group" aria-label="Periode">
        <button v-for="p in PERIODS" :key="p.v" type="button" class="rounded-md px-4 py-1.5 text-sm font-bold" :class="period === p.v ? 'bg-white text-navy shadow' : 'text-slate-600'" :aria-pressed="period === p.v" @click="period = p.v">{{ p.l }}</button>
      </div>
    </div>

    <ErrorState v-if="summary.error.value" :message="summary.error.value" @retry="summary.run" />
    <template v-else>
      <div class="grid grid-cols-4 gap-6">
        <div v-for="c in cards" :key="c.label" class="rounded-2xl border border-l-4 border-slate-200 bg-white p-5 shadow-sm" :class="c.border">
          <p class="text-sm font-bold uppercase text-slate-500">{{ c.label }}</p>
          <p class="mt-1 text-3xl font-bold text-navy">{{ summary.loading.value && !summary.data.value ? '…' : c.value ?? 0 }}</p>
        </div>
      </div>

      <div class="grid grid-cols-5 gap-6">
        <section class="col-span-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 font-bold text-slate-800">Volume Pengiriman <span class="text-sm font-medium text-slate-500">({{ period === '12m' ? 'per bulan' : 'per hari' }})</span></h3>
          <LoadingState v-if="summary.loading.value && !summary.data.value" />
          <BarChart v-else :items="volume" :label-every="period === '30d' ? 5 : 1" title="Volume pengiriman" />
        </section>
        <section class="col-span-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 class="mb-4 font-bold text-slate-800">Jumlah per Status <span class="text-sm font-medium text-slate-500">(dibuat dalam periode)</span></h3>
          <LoadingState v-if="summary.loading.value && !summary.data.value" />
          <BarChart v-else :items="byStatus" horizontal title="Jumlah per status" />
        </section>
      </div>
    </template>

    <section class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div class="border-b border-slate-200 bg-slate-50 p-5">
        <h3 class="font-bold text-slate-800"><i class="fa-solid fa-triangle-exclamation mr-2 text-amber" aria-hidden="true"></i> Perlu Tindakan (PENDING)</h3>
      </div>
      <LoadingState v-if="pending.loading.value && !pending.data.value" />
      <ErrorState v-else-if="pending.error.value" :message="pending.error.value" @retry="pending.run" />
      <EmptyState v-else-if="!pending.data.value?.items.length" icon="fa-circle-check" title="Tidak ada permintaan menunggu" description="Semua permintaan sudah diproses." />
      <table v-else class="w-full text-left text-sm">
        <thead class="bg-slate-100 font-bold text-slate-600">
          <tr><th class="p-4">No. Resi</th><th class="p-4">Customer</th><th class="p-4">Tujuan</th><th class="p-4">Status</th><th class="p-4">Dibuat</th><th class="p-4 text-center">Aksi</th></tr>
        </thead>
        <tbody class="divide-y divide-slate-200">
          <tr v-for="s in pending.data.value.items" :key="s.id" :class="s.is_overdue_pending ? 'bg-red-50' : 'hover:bg-slate-50'">
            <td class="p-4 font-mono font-bold" :class="s.is_overdue_pending ? 'text-danger' : 'text-navy'">
              <i v-if="s.is_overdue_pending" class="fa-solid fa-triangle-exclamation mr-1" aria-hidden="true"></i>
              <span v-if="s.is_overdue_pending" class="sr-only">Terlambat diproses. </span>{{ s.tracking_number }}
            </td>
            <td class="p-4 font-semibold text-slate-700">{{ s.customer_name }}</td>
            <td class="max-w-[16rem] truncate p-4 text-slate-600" :title="s.destination_address">{{ s.recipient_name }} · {{ s.destination_address }}</td>
            <td class="p-4"><StatusBadge :status="s.status" /></td>
            <td class="p-4" :class="s.is_overdue_pending ? 'font-bold text-danger' : 'text-slate-500'">{{ formatDateTime(s.created_at) }}<br /><span class="text-xs">{{ timeAgo(s.created_at) }}</span></td>
            <td class="space-x-2 whitespace-nowrap p-4 text-center">
              <button type="button" class="btn-primary !min-h-0 !px-3 !py-1.5 !text-xs" @click="openAssign(s)">Assign</button>
              <button type="button" class="btn-outline-danger !min-h-0 !px-3 !py-1.5 !text-xs" @click="openReject(s)">Tolak</button>
              <button type="button" class="btn-secondary !min-h-0 !px-3 !py-1.5 !text-xs" aria-label="Lihat detail" @click="openDetail(s)"><i class="fa-solid fa-eye" aria-hidden="true"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <AssignDialog v-model="showAssign" :shipment="assignTarget" @done="refresh" />
    <RejectDialog v-model="showReject" :shipment="rejectTarget" @done="refresh" />
    <ShipmentDetailDialog v-model="showDetail" :shipment-id="detailId" />
  </div>
</template>
