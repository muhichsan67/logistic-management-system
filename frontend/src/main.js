import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // Import router

const app = createApp(App)

app.use(router) // Pake router
app.mount('#app')