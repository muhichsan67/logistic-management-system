import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const MobileLayout = () => import('@/layouts/MobileLayout.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const Profile = () => import('@/views/auth/ProfileView.vue')

const routes = [
  { path: '/', redirect: () => { const a = useAuthStore(); return a.isLoggedIn ? a.homePath : '/login' } },

  // ---- Publik ----
  { path: '/login', component: () => import('@/views/auth/LoginView.vue'), meta: { public: true, guestOnly: true, title: 'Masuk' } },
  { path: '/register', component: () => import('@/views/auth/RegisterView.vue'), meta: { public: true, guestOnly: true, title: 'Daftar' } },
  { path: '/track/:trackingNumber?', component: () => import('@/views/public/TrackView.vue'), meta: { public: true, title: 'Lacak Paket' } },

  // ---- Customer (mobile) ----
  {
    path: '/customer', component: MobileLayout, meta: { roles: ['CUSTOMER'] },
    children: [
      { path: '', component: () => import('@/views/customer/HomeView.vue'), meta: { title: 'Beranda' } },
      { path: 'history', component: () => import('@/views/customer/HistoryView.vue'), meta: { title: 'Riwayat' } },
      { path: 'profile', component: Profile, meta: { title: 'Profil' } },
      { path: 'shipments/new', component: () => import('@/views/customer/CreateShipmentView.vue'), meta: { title: 'Buat Pengiriman', hideNav: true } },
      { path: 'shipments/:trackingNumber', component: () => import('@/views/customer/ShipmentDetailView.vue'), meta: { title: 'Detail Pengiriman', hideNav: true } },
    ],
  },

  // ---- Kurir (mobile) ----
  {
    path: '/courier', component: MobileLayout, meta: { roles: ['COURIER'] },
    children: [
      { path: '', component: () => import('@/views/courier/TaskListView.vue'), meta: { title: 'Tugas' } },
      { path: 'profile', component: Profile, meta: { title: 'Profil' } },
      { path: 'tasks/:id', component: () => import('@/views/courier/TaskDetailView.vue'), meta: { title: 'Detail Tugas', hideNav: true } },
    ],
  },

  // ---- Admin (desktop) ----
  {
    path: '/admin', component: AdminLayout, meta: { roles: ['ADMIN'] },
    children: [
      { path: '', component: () => import('@/views/admin/DashboardView.vue'), meta: { title: 'Dashboard' } },
      { path: 'shipments', component: () => import('@/views/admin/ShipmentsView.vue'), meta: { title: 'Semua Pengiriman' } },
      { path: 'couriers', component: () => import('@/views/admin/CouriersView.vue'), meta: { title: 'Data Kurir' } },
      { path: 'settings', component: () => import('@/views/admin/SettingsView.vue'), meta: { title: 'Pengaturan Sistem' } },
    ],
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Hanya untuk kenyamanan pengguna; keamanan sebenarnya dijaga backend.
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) return to.meta.guestOnly && auth.isLoggedIn ? auth.homePath : true
  if (!auth.isLoggedIn) return '/login'
  if (to.meta.roles && !to.meta.roles.includes(auth.role)) return auth.homePath
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · LajuLogistik` : 'LajuLogistik'
})

export default router
