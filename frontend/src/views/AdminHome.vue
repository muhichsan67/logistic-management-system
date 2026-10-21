<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// State untuk ngatur halaman mana yang lagi aktif
const activeView = ref('dashboard') // Opsi: dashboard, shipments, couriers, settings

// State untuk ngatur Modal (buka/tutup)
const showAssignModal = ref(false)
const showRejectModal = ref(false)
const showDetailModal = ref(false)

// Fungsi Logout
const handleLogout = () => {
  router.push('/')
}
</script>

<template>
  <div id="app-admin" class="min-h-screen bg-slate-100 flex">
      
    <!-- SIDEBAR -->
    <div class="w-64 bg-navy text-white min-h-screen fixed shadow-xl z-20 flex flex-col">
        <div class="p-6 flex items-center gap-3 border-b border-blue-800">
            <i class="fa-solid fa-box-open text-amber text-2xl"></i>
            <span class="font-bold text-xl tracking-wide">Admin UI</span>
        </div>
        <nav class="flex-1 mt-6">
            <ul class="space-y-1 px-3">
                <li>
                  <button @click="activeView = 'dashboard'" :class="activeView === 'dashboard' ? 'bg-blue-800 text-white' : 'text-blue-200 hover:bg-blue-800/50 hover:text-white'" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition">
                    <i class="fa-solid fa-chart-pie w-5"></i> Dashboard
                  </button>
                </li>
                <li>
                  <button @click="activeView = 'shipments'" :class="activeView === 'shipments' ? 'bg-blue-800 text-white' : 'text-blue-200 hover:bg-blue-800/50 hover:text-white'" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition">
                    <i class="fa-solid fa-table-list w-5"></i> All Shipments
                  </button>
                </li>
                <li>
                  <button @click="activeView = 'couriers'" :class="activeView === 'couriers' ? 'bg-blue-800 text-white' : 'text-blue-200 hover:bg-blue-800/50 hover:text-white'" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition">
                    <i class="fa-solid fa-users w-5"></i> Data Couriers
                  </button>
                </li>
                <li>
                  <button @click="activeView = 'settings'" :class="activeView === 'settings' ? 'bg-blue-800 text-white' : 'text-blue-200 hover:bg-blue-800/50 hover:text-white'" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition">
                    <i class="fa-solid fa-gear w-5"></i> System Settings
                  </button>
                </li>
            </ul>
        </nav>
        <div class="p-4 border-t border-blue-800">
            <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-2 rounded-lg text-red-300 hover:bg-red-500/20 font-medium transition">
              <i class="fa-solid fa-arrow-right-from-bracket w-5"></i> Logout
            </button>
        </div>
    </div>

    <!-- MAIN CONTENT AREA -->
    <div class="ml-64 flex-1 flex flex-col">
        <!-- TOPBAR -->
        <header class="bg-white h-16 shadow-sm flex items-center justify-between px-8 z-10 border-b border-slate-200">
            <h2 class="font-bold text-slate-800 text-lg capitalize">{{ activeView }} Overview</h2>
            <div class="flex items-center gap-4">
                <div class="relative">
                    <i class="fa-solid fa-bell text-slate-400 text-xl cursor-pointer hover:text-navy"></i>
                    <span class="absolute -top-1 -right-1 bg-danger text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">1</span>
                </div>
                <div class="flex items-center gap-2 border-l pl-4 border-slate-200">
                    <div class="w-8 h-8 bg-navy text-white rounded-full flex items-center justify-center text-sm font-bold">SA</div>
                    <span class="text-sm font-bold text-slate-700">Super Admin</span>
                </div>
            </div>
        </header>

        <main class="p-8 relative h-full">
            
            <!-- View: DASHBOARD -->
            <div v-if="activeView === 'dashboard'" class="animate-fade-in block">
                <!-- Metrics Row -->
                <div class="grid grid-cols-4 gap-6 mb-8">
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-amber">
                        <p class="text-sm font-bold text-slate-500 uppercase">Pending Orders</p>
                        <h3 class="text-3xl font-bold text-navy mt-1">12</h3>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-blue-500">
                        <p class="text-sm font-bold text-slate-500 uppercase">In Transit</p>
                        <h3 class="text-3xl font-bold text-navy mt-1">45</h3>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-success">
                        <p class="text-sm font-bold text-slate-500 uppercase">Delivered Today</p>
                        <h3 class="text-3xl font-bold text-navy mt-1">28</h3>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-danger">
                        <p class="text-sm font-bold text-slate-500 uppercase">Rejected</p>
                        <h3 class="text-3xl font-bold text-navy mt-1">3</h3>
                    </div>
                </div>

                <!-- Recent Shipments Table -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <div class="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
                        <h3 class="font-bold text-slate-800"><i class="fa-solid fa-triangle-exclamation text-amber mr-2"></i> Action Required (Recent Shipments)</h3>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-100 text-slate-600 font-bold">
                                <tr>
                                    <th class="p-4">Tracking No</th>
                                    <th class="p-4">Customer</th>
                                    <th class="p-4">Origin → Dest</th>
                                    <th class="p-4">Status</th>
                                    <th class="p-4">Created (Wait Time)</th>
                                    <th class="p-4 text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-200">
                                <tr class="bg-red-50 hover:bg-red-100 transition animate-pulse">
                                    <td class="p-4 font-mono font-bold text-danger">TRX-20260926-9999</td>
                                    <td class="p-4 font-semibold text-slate-700">Eko Customer</td>
                                    <td class="p-4 text-slate-600 text-xs">Jkt → Bdg</td>
                                    <td class="p-4"><span class="bg-danger text-white px-3 py-1 rounded-full text-[10px] font-bold">PENDING ALERT</span></td>
                                    <td class="p-4 text-danger font-bold">45 Mins ago</td>
                                    <td class="p-4 text-center space-x-2">
                                        <button @click="showAssignModal = true" class="bg-navy text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-blue-800 shadow">Assign</button>
                                        <button @click="showRejectModal = true" class="bg-white text-danger border border-red-300 px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-red-50">Reject</button>
                                    </td>
                                </tr>
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-4 font-mono font-bold text-navy">TRX-20260925-1011</td>
                                    <td class="p-4 font-semibold text-slate-700">Budi Santoso</td>
                                    <td class="p-4 text-slate-600 text-xs">Sby → Mlg</td>
                                    <td class="p-4"><span class="bg-amber/20 text-amber px-3 py-1 rounded-full text-[10px] font-bold">IN TRANSIT</span></td>
                                    <td class="p-4 text-slate-500">2 Hours ago</td>
                                    <td class="p-4 text-center">
                                        <button @click="showDetailModal = true" class="text-navy hover:text-blue-800 bg-slate-100 px-3 py-1.5 rounded-lg text-xs font-bold"><i class="fa-solid fa-eye"></i> Details</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- View: ALL SHIPMENTS -->
            <div v-if="activeView === 'shipments'" class="animate-fade-in">
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[75vh] flex flex-col">
                    <div class="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
                        <div class="flex gap-3 items-center">
                            <input type="text" placeholder="Cari Resi / Nama..." class="border border-slate-300 rounded-lg px-4 py-2 text-sm focus:ring-navy outline-none w-64">
                            <select class="border border-slate-300 rounded-lg px-4 py-2 text-sm outline-none">
                                <option value="">Semua Status</option>
                                <option value="PENDING">Pending</option>
                                <option value="IN_TRANSIT">In Transit</option>
                                <option value="DELIVERED">Delivered</option>
                            </select>
                        </div>
                        <button class="bg-navy text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-800"><i class="fa-solid fa-download mr-2"></i> Export CSV</button>
                    </div>
                    <div class="overflow-auto flex-1">
                        <table class="w-full text-left text-sm">
                            <thead class="bg-slate-100 text-slate-600 font-bold sticky top-0 z-10">
                                <tr>
                                    <th class="p-4">Tracking No</th>
                                    <th class="p-4">Customer</th>
                                    <th class="p-4">Kurir</th>
                                    <th class="p-4">Status</th>
                                    <th class="p-4">Tanggal</th>
                                    <th class="p-4 text-center">Aksi</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-200">
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-4 font-mono font-bold text-navy">TRX-20260925-1011</td>
                                    <td class="p-4 font-semibold text-slate-700">Eko Customer</td>
                                    <td class="p-4 text-slate-600">Budi Kurir</td>
                                    <td class="p-4"><span class="bg-amber/20 text-amber px-2 py-1 rounded text-[10px] font-bold">IN TRANSIT</span></td>
                                    <td class="p-4 text-slate-500 text-xs">25 Sep 2026</td>
                                    <td class="p-4 text-center">
                                        <button @click="showDetailModal = true" class="text-navy bg-slate-100 p-2 rounded hover:bg-slate-200"><i class="fa-solid fa-eye"></i></button>
                                    </td>
                                </tr>
                                <tr class="hover:bg-slate-50 transition">
                                    <td class="p-4 font-mono font-bold text-slate-600">TRX-20260910-8822</td>
                                    <td class="p-4 font-semibold text-slate-700">Siti Aminah</td>
                                    <td class="p-4 text-slate-600">Agus Kurir</td>
                                    <td class="p-4"><span class="bg-success/20 text-success px-2 py-1 rounded text-[10px] font-bold">COMPLETED</span></td>
                                    <td class="p-4 text-slate-500 text-xs">10 Sep 2026</td>
                                    <td class="p-4 text-center">
                                        <button @click="showDetailModal = true" class="text-navy bg-slate-100 p-2 rounded hover:bg-slate-200"><i class="fa-solid fa-eye"></i></button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- View: COURIERS -->
            <div v-if="activeView === 'couriers'" class="animate-fade-in">
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h3 class="font-bold text-lg text-slate-800">Manajemen Kurir</h3>
                        <button class="bg-success text-white px-4 py-2 rounded-lg text-sm font-bold shadow hover:bg-emerald-600"><i class="fa-solid fa-plus mr-2"></i> Tambah Kurir</button>
                    </div>
                    <div class="grid grid-cols-3 gap-6">
                        <div class="border border-slate-200 rounded-xl p-5 flex items-center gap-4 hover:shadow-md transition">
                            <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-xl"><i class="fa-solid fa-motorcycle"></i></div>
                            <div>
                                <h4 class="font-bold text-slate-800">Budi Kurir</h4>
                                <p class="text-xs text-slate-500">081234567891</p>
                                <p class="text-[10px] font-bold text-success mt-1">Status: Aktif (2 Tugas)</p>
                            </div>
                        </div>
                        <div class="border border-slate-200 rounded-xl p-5 flex items-center gap-4 hover:shadow-md transition">
                            <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-xl"><i class="fa-solid fa-motorcycle"></i></div>
                            <div>
                                <h4 class="font-bold text-slate-800">Agus Kurir</h4>
                                <p class="text-xs text-slate-500">089988776655</p>
                                <p class="text-[10px] font-bold text-slate-400 mt-1">Status: Offline</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- View: SETTINGS -->
            <div v-if="activeView === 'settings'" class="animate-fade-in">
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 max-w-2xl">
                    <h3 class="font-bold text-lg text-slate-800 mb-6 border-b pb-3"><i class="fa-solid fa-sliders text-navy mr-2"></i> Konfigurasi Sistem Bisnis</h3>
                    <form @submit.prevent="alert('Pengaturan Disimpan!')" class="space-y-6">
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-1">Visual Alert Timeout (Menit)</label>
                            <p class="text-xs text-slate-500 mb-2">Durasi status PENDING sebelum muncul baris merah peringatan di Dashboard.</p>
                            <input type="number" value="30" class="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-navy outline-none">
                        </div>
                        <div>
                            <label class="block text-sm font-bold text-slate-700 mb-1">Auto-Complete Days (Hari)</label>
                            <p class="text-xs text-slate-500 mb-2">Durasi hari status DELIVERED otomatis diubah ke COMPLETED oleh Cron Job.</p>
                            <input type="number" value="3" class="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-navy outline-none">
                        </div>
                        <div class="pt-4 border-t border-slate-100">
                            <button type="submit" class="bg-navy text-white px-6 py-3 rounded-lg text-sm font-bold shadow hover:bg-blue-800">Simpan Konfigurasi</button>
                        </div>
                    </form>
                </div>
            </div>

        </main>
    </div>

    <!-- MODAL ADMIN: Assign Courier -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 relative">
            <button @click="showAssignModal = false" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            <h3 class="font-bold text-navy text-lg mb-1">Assign Courier</h3>
            <p class="text-xs text-slate-500 mb-4 font-mono">Resi: TRX-20260926-9999</p>
            
            <form @submit.prevent="showAssignModal = false; alert('Kurir berhasil ditugaskan!')">
                <label class="block text-sm font-bold text-slate-700 mb-2">Pilih Kurir:</label>
                <select class="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-navy outline-none mb-6">
                    <option value="">-- Pilih Kurir Aktif --</option>
                    <option value="1">Budi Kurir (2 Tugas)</option>
                    <option value="2">Agus Kurir (0 Tugas)</option>
                </select>
                <button type="submit" class="w-full bg-navy text-white font-bold py-3 rounded-lg hover:bg-blue-800">Assign & Update Status</button>
            </form>
        </div>
    </div>

    <!-- MODAL ADMIN: Reject DR -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-sm rounded-xl shadow-2xl p-6 relative border-t-4 border-danger">
            <button @click="showRejectModal = false" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><i class="fa-solid fa-xmark text-lg"></i></button>
            <h3 class="font-bold text-danger text-lg mb-1">Reject Request</h3>
            <p class="text-xs text-slate-500 mb-4 font-mono">Resi: TRX-20260926-9999</p>
            
            <form @submit.prevent="showRejectModal = false; alert('Permintaan Ditolak!')">
                <label class="block text-sm font-bold text-slate-700 mb-2">Alasan Penolakan:</label>
                <textarea required rows="3" placeholder="Alamat tidak valid, dll..." class="w-full border border-slate-300 rounded-lg p-3 text-sm focus:ring-danger outline-none mb-6"></textarea>
                <div class="flex gap-3">
                    <button type="button" @click="showRejectModal = false" class="flex-1 bg-slate-100 text-slate-600 font-bold py-3 rounded-lg hover:bg-slate-200">Batal</button>
                    <button type="submit" class="flex-1 bg-danger text-white font-bold py-3 rounded-lg hover:bg-red-600">Reject Data</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL ADMIN: View Detail -->
    <div v-if="showDetailModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-lg rounded-xl shadow-2xl p-6 relative max-h-[90vh] overflow-y-auto">
            <button @click="showDetailModal = false" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 bg-slate-100 p-2 rounded-full"><i class="fa-solid fa-xmark"></i></button>
            <div class="flex items-center gap-3 mb-4 border-b border-slate-100 pb-4">
                <div class="bg-amber/20 text-amber px-3 py-1 rounded text-xs font-bold inline-block">IN TRANSIT</div>
                <h3 class="font-bold text-navy text-xl font-mono">TRX-20260925-1011</h3>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-50 p-3 rounded-lg">
                    <p class="text-[10px] text-slate-400 font-bold uppercase">Customer</p>
                    <p class="text-sm font-semibold text-slate-800">Eko Customer</p>
                    <p class="text-xs text-navy">ID: #409</p>
                </div>
                <div class="bg-slate-50 p-3 rounded-lg">
                    <p class="text-[10px] text-slate-400 font-bold uppercase">Assigned Courier</p>
                    <p class="text-sm font-semibold text-slate-800">Budi Kurir</p>
                    <p class="text-xs text-emerald-600">ID: #102</p>
                </div>
            </div>

            <div class="bg-slate-50 p-4 rounded-lg mb-4 border border-slate-200">
                <p class="text-[10px] text-slate-400 font-bold uppercase mb-2">Package Details</p>
                <div class="flex justify-between text-sm mb-1"><span>Deskripsi:</span> <span class="font-semibold">Pakaian & Sepatu</span></div>
                <div class="flex justify-between text-sm"><span>Berat:</span> <span class="font-semibold">2.5 KG</span></div>
            </div>

            <div>
                <p class="text-[10px] text-slate-400 font-bold uppercase mb-2">Tracking History Logs</p>
                <div class="border-l-2 border-slate-200 ml-2 pl-4 space-y-3">
                    <div>
                        <p class="text-xs font-bold text-slate-700">IN TRANSIT</p>
                        <p class="text-[10px] text-slate-500">25 Sep 2026 14:00 by Budi Kurir</p>
                    </div>
                    <div>
                        <p class="text-xs font-bold text-slate-700">PICKED UP</p>
                        <p class="text-[10px] text-slate-500">25 Sep 2026 10:30 by Budi Kurir</p>
                    </div>
                    <div>
                        <p class="text-xs font-bold text-slate-700">ASSIGNED</p>
                        <p class="text-[10px] text-slate-500">25 Sep 2026 09:15 by Super Admin</p>
                    </div>
                    <div>
                        <p class="text-xs font-bold text-slate-700">PENDING</p>
                        <p class="text-[10px] text-slate-500">25 Sep 2026 09:00 System</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
</style>