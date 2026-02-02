import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
  },
  {
    path: '/driver-login',
    name: 'DriverLogin',
    component: () => import('@/pages/DriverLogin.vue'),
  },
  {
    path: '/driver/dashboard',
    name: 'DriverDashboard',
    component: () => import('@/pages/drivee/DriverDashboard.vue'),
  },
  {
    path: '/customer-signup',
    name: 'CustomerSignup',
    component: () => import('@/pages/CustomerSignup.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/track'),
  routes,
})

export default router
