<script setup>
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import FormField from '@/components/FormField.vue'
import { assignCourier, getCouriers } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'

const props = defineProps({ shipment: { type: Object, default: null } })
const emit = defineEmits(['done'])
const visible = defineModel({ type: Boolean, default: false })
const online = useOnline()

const couriers = ref([])
const courierId = ref('')
const notes = ref('')
const error = ref('')
const loadError = ref('')
const submitting = ref(false)

watch(visible, async (v) => {
  if (!v) return
  courierId.value = ''
  notes.value = ''
  error.value = loadError.value = ''
  try {
    couriers.value = (await getCouriers({ is_active: true, limit: 100 })).items
  } catch (e) {
    loadError.value = e.userMessage
  }
})

async function submit() {
  if (!courierId.value) {
    error.value = 'Pilih kurir terlebih dahulu'
    return
  }
  submitting.value = true
  try {
    await assignCourier(props.shipment.id, { courier_id: Number(courierId.value), notes: notes.value.trim() || undefined })
    toast.success('Kurir berhasil ditugaskan')
    visible.value = false
    emit('done')
  } catch {
    /* toast ditampilkan interceptor */
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Dialog v-model:visible="visible" modal header="Tugaskan Kurir" :style="{ width: '26rem' }" :draggable="false">
    <form class="space-y-4" novalidate @submit.prevent="submit">
      <p class="font-mono text-sm text-slate-500">Resi: {{ shipment?.tracking_number }}</p>
      <p v-if="loadError" role="alert" class="rounded-lg bg-red-50 p-3 text-sm text-red-800">{{ loadError }}</p>
      <FormField label="Pilih Kurir" for-id="assign-courier" :error="error">
        <select id="assign-courier" v-model="courierId" class="input !text-sm" :class="{ 'input-error': error }">
          <option value="">-- Pilih Kurir Aktif --</option>
          <option v-for="c in couriers" :key="c.id" :value="c.id">{{ c.name }} ({{ c.phone }})</option>
        </select>
      </FormField>
      <FormField label="Catatan (opsional)" for-id="assign-notes">
        <textarea id="assign-notes" v-model="notes" rows="2" class="input !text-sm" placeholder="Cth: Prioritas, jemput sebelum jam 12"></textarea>
      </FormField>
      <div class="flex gap-3">
        <button type="button" class="btn-secondary flex-1" @click="visible = false">Batal</button>
        <button type="submit" class="btn-primary flex-1" :disabled="submitting || !online">
          <i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Tugaskan
        </button>
      </div>
    </form>
  </Dialog>
</template>
