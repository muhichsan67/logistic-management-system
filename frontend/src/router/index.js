import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import CustomerHome from '../views/CustomerHome.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: Login
  },
  {
    path: '/customer',
    name: 'CustomerHome',
    component: CustomerHome
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router