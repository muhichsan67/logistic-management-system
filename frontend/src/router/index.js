import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import CustomerHome from '../views/CustomerHome.vue'
import AdminHome from '../views/AdminHome.vue'
import CourierHome from '../views/CourierHome.vue' // <-- Pastikan ada ini

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/customer', name: 'CustomerHome', component: CustomerHome },
  { path: '/admin', name: 'AdminHome', component: AdminHome },
  { path: '/courier', name: 'CourierHome', component: CourierHome } // <-- Pastikan ada ini
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router