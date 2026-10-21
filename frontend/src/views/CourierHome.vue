<script setup>
import { ref } from 'vue'

// State buat buka/tutup modal
const showUpdateModal = ref(false)

// State buat nangkep data dari form
const selectedStatus = ref('IN_TRANSIT')
const courierNotes = ref('')

// Fungsi pas tombol Simpan Update diklik
const handleUpdate = () => {
  // Di sini nanti kita tembak API backend
  alert(`Status diubah ke: ${selectedStatus.value}\nCatatan: ${courierNotes.value}`)
  
  // Tutup modal setelah disimpan
  showUpdateModal.value = false
}
</script>

<template>
  <div id="app-courier" class="max-w-md mx-auto min-h-screen bg-slate-50 relative shadow-2xl">
    
    <!-- HEADER -->
    <div class="bg-emerald-600 text-white px-5 py-6 rounded-b-3xl shadow-md">
        <div class="flex justify-between items-center mb-4">
            <div class="font-bold text-lg"><i class="fa-solid fa-motorcycle"></i> Courier App</div>
            <div class="w-8 h-8 bg-emerald-800 rounded-full flex items-center justify-center">
                <i class="fa-solid fa-user text-xs"></i>
            </div>
        </div>
        <h2 class="text-xl font-bold">Semangat, Budi!</h2>
        <p class="text-emerald-100 text-sm">Ada 1 tugas aktif hari ini.</p>
    </div>

    <!-- CONTENT AREA -->
    <div class="px-5 py-6">
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-emerald-100 mb-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3 mb-3">
                <span class="font-mono font-bold text-slate-800">TRX-20260925-1011</span>
                <span class="bg-amber/10 text-amber px-2 py-1 rounded text-xs font-bold">In Transit</span>
            </div>
            <p class="text-xs text-slate-500"><i class="fa-solid fa-location-dot text-emerald-500 w-4"></i> Tujuan: Jl. Melati No 5, Bandung</p>
            <p class="text-xs text-slate-500 mt-1"><i class="fa-solid fa-user text-emerald-500 w-4"></i> Penerima: Budi Santoso (0812xxx)</p>
            
            <!-- Tombol Update Status -->
            <button @click="showUpdateModal = true" class="w-full mt-4 bg-emerald-500 text-white font-bold py-3 rounded-xl shadow hover:bg-emerald-600 transition">
                Update Status
            </button>
        </div>
    </div>

    <!-- MODAL: Update Status Courier -->
    <div v-if="showUpdateModal" class="fixed inset-0 bg-black/50 z-50 flex items-end justify-center">
        <div class="bg-white w-full max-w-md p-5 rounded-t-3xl shadow-2xl transform transition-transform">
            <div class="flex justify-between items-center mb-5">
                <h3 class="font-bold text-emerald-800 text-lg">Update TRX-20260925-1011</h3>
                <button @click="showUpdateModal = false" class="text-slate-400 hover:text-slate-600">
                    <i class="fa-solid fa-xmark text-xl"></i>
                </button>
            </div>
            
            <!-- Form Update -->
            <label class="block text-sm font-bold text-slate-700 mb-2">Ubah Status Menjadi:</label>
            <select v-model="selectedStatus" class="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none mb-4 bg-slate-50">
                <option value="IN_TRANSIT">In Transit (Perjalanan)</option>
                <option value="DELIVERED">Delivered (Sampai Tujuan)</option>
            </select>
            
            <label class="block text-sm font-bold text-slate-700 mb-2">Catatan Kurir:</label>
            <textarea v-model="courierNotes" rows="2" placeholder="Cth: Dititipkan ke satpam" class="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none mb-4"></textarea>
            
            <!-- Kotak Upload Foto -->
            <div class="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center mb-5 bg-slate-50 cursor-pointer hover:bg-slate-100 transition">
                <i class="fa-solid fa-camera text-3xl text-emerald-500 mb-2"></i>
                <p class="text-sm font-bold text-slate-600">Ambil Foto Bukti (POD)</p>
                <p class="text-xs text-slate-400">Wajib untuk status Delivered</p>
            </div>

            <!-- Tombol Simpan -->
            <button @click="handleUpdate" class="w-full bg-emerald-600 text-white font-bold py-4 rounded-xl shadow-lg hover:bg-emerald-700 transition">
                Simpan Update
            </button>
        </div>
    </div>

  </div>
</template>

<style scoped>
</style>