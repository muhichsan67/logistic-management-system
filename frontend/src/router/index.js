import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import CustomerHome from '../views/CustomerHome.vue'
import AdminHome from '../views/AdminHome.vue' // <-- Pastikan ini ada

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/customer', name: 'CustomerHome', component: CustomerHome },
  { path: '/admin', name: 'AdminHome', component: AdminHome } // <-- Pastikan ini ada
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router