<script setup>
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import FormField from '@/components/FormField.vue'
import { rejectShipment } from '@/api'
import { toast } from '@/utils/toast'
import { useOnline } from '@/utils/online'

const props = defineProps({ shipment: { type: Object, default: null } })
const emit = defineEmits(['done'])
const visible = defineModel({ type: Boolean, default: false })
const online = useOnline()

const reason = ref('')
const error = ref('')
const submitting = ref(false)

watch(visible, (v) => {
  if (v) reason.value = error.value = ''
})

async function submit() {
  if (!reason.value.trim()) {
    error.value = 'Alasan penolakan wajib diisi'
    return
  }
  submitting.value = true
  try {
    await rejectShipment(props.shipment.id, reason.value.trim())
    toast.success('Permintaan pengiriman ditolak')
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
  <Dialog v-model:visible="visible" modal header="Tolak Permintaan" :style="{ width: '26rem' }" :draggable="false">
    <form class="space-y-4" novalidate @submit.prevent="submit">
      <p class="font-mono text-sm text-slate-500">Resi: {{ shipment?.tracking_number }}</p>
      <FormField label="Alasan Penolakan" for-id="reject-reason" :error="error">
        <textarea id="reject-reason" v-model="reason" rows="3" class="input !text-sm" :class="{ 'input-error': error }" placeholder="Cth: Alamat tidak valid"></textarea>
      </FormField>
      <div class="flex gap-3">
        <button type="button" class="btn-secondary flex-1" @click="visible = false">Batal</button>
        <button type="submit" class="btn-danger flex-1" :disabled="submitting || !online">
          <i v-if="submitting" class="fa-solid fa-circle-notch fa-spin" aria-hidden="true"></i> Tolak
        </button>
      </div>
    </form>
  </Dialog>
</template>
