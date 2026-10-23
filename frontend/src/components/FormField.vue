<script setup>
// Label + pesan error tepat di bawah field. `forId` harus sama dengan id input di slot.
defineProps({
  label: { type: String, required: true },
  forId: { type: String, required: true },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },
})
</script>

<template>
  <div>
    <label :for="forId" class="mb-1 block text-sm font-semibold text-slate-700">{{ label }}</label>
    <slot />
    <p v-if="hint && !error" class="mt-1 text-xs text-slate-500">{{ hint }}</p>
    <p v-if="error" :id="`${forId}-error`" role="alert" class="mt-1 text-sm font-medium text-danger">
      <i class="fa-solid fa-circle-exclamation mr-1" aria-hidden="true"></i>{{ error }}
    </p>
  </div>
</template>
