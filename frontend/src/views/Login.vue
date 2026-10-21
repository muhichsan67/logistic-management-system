<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('eko.customer@gmail.com')
const password = ref('')
const router = useRouter()

const handleLogin = () => {
  // Cek emailnya siapa
  if (email.value === 'admin@alur.com') {
    // Kalau admin, masuk ke halaman admin
    router.push('/admin')
  } else if (email.value === 'budi.courier@alur.com') {
    // Nanti kalau halaman kurir udah jadi, aktifin ini
    // router.push('/courier') 
    alert('Halaman kurir belum dibuat!')
  } else {
    // Kalau customer (atau email lain), masuk ke halaman customer
    router.push('/customer')
  }
}
</script>

<template>
  <div id="app-customer-login" class="min-h-screen flex items-center justify-center bg-white">
    <div class="w-full max-w-md p-8">
      
      <!-- Logo & Title -->
      <div class="text-center mb-8">
        <div class="text-3xl text-navy mb-2"><i class="fa-solid fa-box-open"></i></div>
        <h1 class="text-2xl font-bold text-navy">LajuLogistik</h1>
        <p class="text-slate-500 text-sm mt-1">Masuk untuk melacak paket Anda</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input 
            type="email" 
            v-model="email" 
            class="w-full border border-slate-300 rounded px-3 py-2" 
            required
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input 
            type="password" 
            v-model="password" 
            class="w-full border border-slate-300 rounded px-3 py-2" 
            required
          >
        </div>
        
        <button type="submit" class="w-full bg-navy text-white rounded-xl py-3 font-semibold hover:bg-blue-900 transition">
          Masuk <i class="fa-solid fa-arrow-right ml-2"></i>
        </button>
        
        <p class="text-center text-sm text-slate-500 mt-4">
          Belum punya akun? <a href="#" class="text-blue-600 font-medium">Daftar disini</a>
        </p>
      </form>

    </div>
  </div>
</template>

<style scoped>
/* Kosongin aja dulu */
</style>