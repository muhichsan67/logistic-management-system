<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import LoadingState from '@/components/LoadingState.vue'
import ErrorState from '@/components/ErrorState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import TrackingTimeline from '@/components/TrackingTimeline.vue'
import FormField from '@/components/FormField.vue'
import { getCourierTask, updateTaskStatus, uploadProof } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'
import { useAsync } from '@/utils/useAsync'
import { compressImage } from '@/utils/image'
import { assetUrl, formatWeight } from '@/utils/format'

const route = useRoute()
const online = useOnline()
const detail = useAsync(() => getCourierTask(route.params.id))
onMounted(detail.run)

// Tombol aksi per status (FRONTEND_RULES 6.2). Status lain: tidak ada tombol.
const NEXT = {
  ASSIGNED: { to: 'PICKED_UP', label: 'Sudah Dijemput', icon: 'fa-hand-holding' },
  PICKED_UP: { to: 'IN_TRANSIT', label: 'Dalam Perjalanan', icon: 'fa-truck-fast' },
  IN_TRANSIT: { to: 'DELIVERED', label: 'Terkirim', icon: 'fa-box-open', needsProof: true },
}
const next = computed(() => NEXT[detail.data.value?.status])

const notes = ref('')
const photo = ref(null)
const preview = ref('')
const photoError = ref('')
const uploadError = ref('')
const submitting = ref(false)

function setPhoto(file) {
  if (preview.value) URL.revokeObjectURL(preview.value)
  photo.value = file
  preview.value = file ? URL.createObjectURL(file) : ''
}
onBeforeUnmount(() => setPhoto(null))

async function onFile(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  photoError.value = uploadError.value = ''
  try {
    setPhoto(await compressImage(file))
  } catch (err) {
    setPhoto(null)
    photoError.value = err.message
  }
}

async function submit() {
  const action = next.value
  if (action.needsProof && !photo.value) {
    photoError.value = 'Foto bukti pengiriman wajib diambil'
    return
  }
  submitting.value = true
  uploadError.value = ''
  try {
    let proofUrl
    if (action.needsProof) {
      try {
        proofUrl = (await uploadProof(photo.value)).url
      } catch {
        // Unggah gagal -> status JANGAN diubah
        uploadError.value = 'Unggah foto gagal. Silakan coba lagi.'
        return
      }
    }
    await updateTaskStatus(detail.data.value.id, { status: action.to, notes: notes.value.trim() || undefined, proof_image_url: proofUrl })
    toast.success('Status berhasil diperbarui')
    notes.value = ''
    setPhoto(null)
    await detail.run() // muat ulang dari server
  } catch {
    /* toast dari interceptor */
  } finally {
    submitting.value = false
  }
}

const mapUrl = (addr) => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(addr)}`
</script>

<template>
  <div>
    <PageHeader title="Detail Tugas" back-to="/courier" tone="emerald" />

    <div class="px-5 py-5">
      <LoadingState v-if="detail.loading.value && !detail.data.value" />
      <ErrorState v-else-if="detail.error.value && !detail.data.value" :message="detail.error.value" @retry="detail.run" />

      <div v-else-if="detail.data.value" class="space-y-4">
        <div class="flex items-center justify-between gap-2">
          <h1 class="font-mono text-lg font-bold text-slate-800">{{ detail.data.value.tracking_number }}</h1>
          <StatusBadge :status="detail.data.value.status" />
        </div>

        <section class="card p-4 text-sm" aria-labelledby="pickup-title">
          <h2 id="pickup-title" class="mb-2 text-xs font-bold uppercase text-slate-500">Jemput di (Pengirim)</h2>
          <p class="font-semibold">{{ detail.data.value.sender_name }}</p>
          <a :href="`tel:${detail.data.value.sender_phone}`" class="inline-flex min-h-[44px] items-center gap-2 font-semibold text-emerald-700 underline"><i class="fa-solid fa-phone" aria-hidden="true"></i>{{ detail.data.value.sender_phone }}</a>
          <p class="text-slate-600">{{ detail.data.value.origin_address }}</p>
          <a :href="mapUrl(detail.data.value.origin_address)" target="_blank" rel="noopener" class="mt-1 inline-flex min-h-[44px] items-center gap-2 font-semibold text-emerald-700"><i class="fa-solid fa-map-location-dot" aria-hidden="true"></i> Buka peta</a>
        </section>

        <section class="card p-4 text-sm" aria-labelledby="dest-title">
          <h2 id="dest-title" class="mb-2 text-xs font-bold uppercase text-slate-500">Antar ke (Penerima)</h2>
          <p class="font-semibold">{{ detail.data.value.recipient_name }}</p>
          <a :href="`tel:${detail.data.value.recipient_phone}`" class="inline-flex min-h-[44px] items-center gap-2 font-semibold text-emerald-700 underline"><i class="fa-solid fa-phone" aria-hidden="true"></i>{{ detail.data.value.recipient_phone }}</a>
          <p class="text-slate-600">{{ detail.data.value.destination_address }}</p>
          <a :href="mapUrl(detail.data.value.destination_address)" target="_blank" rel="noopener" class="mt-1 inline-flex min-h-[44px] items-center gap-2 font-semibold text-emerald-700"><i class="fa-solid fa-map-location-dot" aria-hidden="true"></i> Buka peta</a>
        </section>

        <section class="card p-4 text-sm" aria-labelledby="pkg-title">
          <h2 id="pkg-title" class="mb-2 text-xs font-bold uppercase text-slate-500">Paket</h2>
          <p class="flex justify-between gap-4"><span class="text-slate-500">Isi</span><span class="text-right font-semibold">{{ detail.data.value.package_description }}</span></p>
          <p class="flex justify-between gap-4"><span class="text-slate-500">Berat</span><span class="font-semibold">{{ formatWeight(detail.data.value.weight_kg) }}</span></p>
        </section>

        <!-- Aksi status berikutnya -->
        <section v-if="next" class="card space-y-4 border-emerald-200 p-4" aria-labelledby="action-title">
          <h2 id="action-title" class="font-bold text-emerald-800">Update status: {{ next.label }}</h2>

          <FormField label="Catatan Kurir (opsional)" for-id="notes">
            <textarea id="notes" v-model="notes" rows="2" placeholder="Cth: Dititipkan ke satpam" class="input focus:ring-emerald-500"></textarea>
          </FormField>

          <div v-if="next.needsProof">
            <p class="mb-1 text-sm font-semibold text-slate-700">Foto Bukti Pengiriman (wajib)</p>
            <input id="proof" type="file" accept="image/*" capture="environment" class="sr-only" :disabled="submitting" @change="onFile" />
            <img v-if="preview" :src="preview" alt="Pratinjau foto bukti" class="mb-2 max-h-64 w-full rounded-xl object-cover" />
            <label for="proof" class="flex min-h-[44px] cursor-pointer flex-col items-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-5 text-center hover:bg-slate-100 focus-within:ring-2 focus-within:ring-emerald-500" :class="{ 'pointer-events-none opacity-50': submitting }">
              <i class="fa-solid fa-camera mb-1 text-3xl text-emerald-600" aria-hidden="true"></i>
              <span class="text-sm font-bold text-slate-700">{{ photo ? 'Ambil Ulang Foto' : 'Ambil Foto Bukti' }}</span>
            </label>
            <p v-if="photoError" role="alert" class="mt-1 text-sm font-medium text-danger"><i class="fa-solid fa-circle-exclamation mr-1" aria-hidden="true"></i>{{ photoError }}</p>
            <p v-if="uploadError" role="alert" class="mt-1 text-sm font-medium text-danger"><i class="fa-solid fa-circle-exclamation mr-1" aria-hidden="true"></i>{{ uploadError }}</p>
          </div>

          <button type="button" class="btn-success w-full !py-3.5 text-base" :disabled="submitting || !online" @click="submit">
            <i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i>
            <i v-else class="fa-solid" :class="next.icon" aria-hidden="true"></i>
            {{ submitting ? (next.needsProof ? 'Mengunggah...' : 'Menyimpan...') : next.label }}
          </button>
        </section>

        <section v-if="detail.data.value.proof_image_url" class="card p-4">
          <h2 class="mb-2 text-xs font-bold uppercase text-slate-500">Bukti Pengiriman</h2>
          <img :src="assetUrl(detail.data.value.proof_image_url)" alt="Foto bukti pengiriman" class="w-full rounded-lg object-cover" loading="lazy" />
        </section>

        <section class="card p-4" aria-labelledby="hist-title">
          <h2 id="hist-title" class="mb-4 text-xs font-bold uppercase text-slate-500">Riwayat</h2>
          <TrackingTimeline :history="detail.data.value.history" />
        </section>
      </div>
    </div>
  </div>
</template>
