import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import { definePreset } from '@primeuix/themes'

import '@fontsource/plus-jakarta-sans/latin-400.css'
import '@fontsource/plus-jakarta-sans/latin-500.css'
import '@fontsource/plus-jakarta-sans/latin-600.css'
import '@fontsource/plus-jakarta-sans/latin-700.css'
import '@fontsource/plus-jakarta-sans/latin-800.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import './style.css'

import App from './App.vue'
import router from './router'

// PrimeVue (hanya dipakai di Admin: tabel & dialog). Warna utama = biru navy.
const shades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
const AlurPreset = definePreset(Aura, {
  semantic: { primary: Object.fromEntries(shades.map((s) => [s, `{blue.${s}}`])) },
})

createApp(App)
  .use(createPinia())
  .use(router)
  .use(PrimeVue, {
    theme: {
      preset: AlurPreset,
      options: {
        darkModeSelector: '.never-dark',
        cssLayer: { name: 'primevue', order: 'tailwind-base, primevue, tailwind-utilities' },
      },
    },
  })
  .mount('#app')
