<script setup>
import { ref } from 'vue'

// State untuk nentuin tab mana yang lagi aktif
const activeTab = ref('home')

// Fungsi buat ganti tab
const switchCustView = (tab) => {
  activeTab.value = tab
}
</script>

<template>
  <div id="app-customer" class="max-w-md mx-auto min-h-screen bg-slate-50 relative shadow-2xl pb-20">
    
    <!-- HEADER -->
    <div class="bg-navy text-white px-5 py-6 rounded-b-3xl shadow-md">
        <div class="flex justify-between items-center mb-6">
            <div class="font-bold text-xl tracking-tight"><i class="fa-solid fa-box-open text-amber"></i> LajuLogistik</div>
            <div class="w-10 h-10 bg-blue-800 rounded-full flex items-center justify-center border-2 border-slate-200">
                <i class="fa-solid fa-user text-sm"></i>
            </div>
        </div>
        <h2 class="text-2xl font-bold">Halo, Eko! 👋</h2>
        <p class="text-blue-200 text-sm mt-1">Mau kirim atau lacak paket hari ini?</p>
        
        <!-- Quick Actions -->
        <div class="flex gap-3 mt-6">
            <!-- Sementara tombol ini nggak ngejalanin apa-apa dulu -->
            <button class="flex-1 bg-amber text-navy font-bold py-3 px-4 rounded-xl shadow hover:bg-yellow-400 transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-paper-plane"></i> Kirim Paket
            </button>
            <button class="flex-1 bg-white text-navy font-bold py-3 px-4 rounded-xl shadow hover:bg-slate-100 transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-magnifying-glass"></i> Lacak Resi
            </button>
        </div>
    </div>

    <!-- CONTENT AREA -->
    <div class="px-5 py-6 relative">
        
        <!-- View: HOME (Tampil kalau activeTab === 'home') -->
        <div v-if="activeTab === 'home'" class="block animate-fade-in">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-slate-800 text-lg">Sedang Berlangsung</h3>
                <span class="text-xs text-navy font-semibold cursor-pointer" @click="switchCustView('history')">Lihat Semua</span>
            </div>
            <!-- Card Paket Aktif -->
            <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 mb-4 cursor-pointer">
                <div class="flex justify-between items-start border-b border-slate-100 pb-3 mb-3">
                    <div>
                        <p class="text-xs text-slate-500 font-medium">No. Resi</p>
                        <p class="font-bold text-navy text-sm">TRX-20260925-1011</p>
                    </div>
                    <span class="bg-amber/10 text-amber px-3 py-1 rounded-full text-xs font-bold">In Transit</span>
                </div>
                <div class="flex items-center gap-4">
                    <div class="flex-1">
                        <p class="text-[10px] text-slate-400">Pengirim</p>
                        <p class="text-sm font-semibold text-slate-700">Eko Customer</p>
                    </div>
                    <div class="text-slate-300 text-lg"><i class="fa-solid fa-arrow-right"></i></div>
                    <div class="flex-1 text-right">
                        <p class="text-[10px] text-slate-400">Penerima</p>
                        <p class="text-sm font-semibold text-slate-700">Budi Santoso</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- View: HISTORY -->
        <div v-if="activeTab === 'history'" class="block animate-fade-in">
            <h3 class="font-bold text-slate-800 text-lg mb-4">Riwayat Pengiriman</h3>
            <div class="space-y-3">
                <!-- History Item 1 -->
                <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 cursor-pointer hover:border-navy transition">
                    <div class="flex justify-between items-center mb-2">
                        <p class="font-bold text-navy text-sm">TRX-20260925-1011</p>
                        <span class="bg-amber/10 text-amber px-2 py-0.5 rounded text-[10px] font-bold">In Transit</span>
                    </div>
                    <p class="text-xs text-slate-500 mb-2">Tujuan: Budi Santoso (Jakarta Selatan)</p>
                    <p class="text-[10px] text-slate-400"><i class="fa-regular fa-clock"></i> 25 Sep 2026, 14:00</p>
                </div>
                <!-- History Item 2 -->
                <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 cursor-pointer">
                    <div class="flex justify-between items-center mb-2">
                        <p class="font-bold text-navy text-sm">TRX-20260910-8822</p>
                        <span class="bg-success/10 text-success px-2 py-0.5 rounded text-[10px] font-bold">Completed</span>
                    </div>
                    <p class="text-xs text-slate-500 mb-2">Tujuan: Siti Aminah (Bandung)</p>
                    <p class="text-[10px] text-slate-400"><i class="fa-regular fa-clock"></i> 12 Sep 2026, 09:30</p>
                </div>
            </div>
        </div>

        <!-- View: PROFILE -->
        <div v-if="activeTab === 'profile'" class="block animate-fade-in">
            <div class="text-center mb-6 pt-4">
                <div class="w-24 h-24 bg-blue-100 text-navy text-4xl rounded-full flex items-center justify-center mx-auto mb-3 shadow-inner">
                    <i class="fa-solid fa-user"></i>
                </div>
                <h3 class="font-bold text-xl text-slate-800">Eko Customer</h3>
                <p class="text-sm text-slate-500">Member sejak Jan 2026</p>
            </div>
            <div class="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
                <h4 class="font-bold text-navy mb-4 border-b pb-2">Informasi Pribadi</h4>
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-500 mb-1">Nama Lengkap</label>
                        <input type="text" value="Eko Customer" class="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-1 focus:ring-navy focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-500 mb-1">Email</label>
                        <input type="email" value="eko.customer@gmail.com" class="w-full border border-slate-300 rounded-lg p-2 text-sm focus:ring-1 focus:ring-navy focus:outline-none" readonly>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <!-- BOTTOM NAVIGATION -->
    <div class="fixed bottom-0 w-full max-w-md bg-white border-t border-slate-200 flex justify-around py-3 px-2 z-40 pb-5 shadow-[0_-5px_15px_-10px_rgba(0,0,0,0.1)]">
        <button @click="switchCustView('home')" :class="activeTab === 'home' ? 'text-navy' : 'text-slate-400'" class="flex flex-col items-center gap-1 flex-1">
            <i class="fa-solid fa-house text-xl"></i>
            <span class="text-[10px] font-bold">Beranda</span>
        </button>
        <button @click="switchCustView('history')" :class="activeTab === 'history' ? 'text-navy' : 'text-slate-400'" class="flex flex-col items-center gap-1 flex-1">
            <i class="fa-solid fa-clock-rotate-left text-xl"></i>
            <span class="text-[10px] font-semibold">Riwayat</span>
        </button>
        <button @click="switchCustView('profile')" :class="activeTab === 'profile' ? 'text-navy' : 'text-slate-400'" class="flex flex-col items-center gap-1 flex-1">
            <i class="fa-regular fa-user text-xl"></i>
            <span class="text-[10px] font-semibold">Profil</span>
        </button>
    </div>

  </div>
</template>

<style scoped>
</style>