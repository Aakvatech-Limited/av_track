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
    meta: { requiresDriverAuth: true },
  },
  {
    path: '/driver/navigate',
    name: 'DriverNavigate',
    component: () => import('@/pages/drivee/DriverNavigate.vue'),
    meta: { requiresDriverAuth: true },
  },
  {
    path: '/driver/complete',
    name: 'DriverDeliveryComplete',
    component: () => import('@/pages/drivee/DriverDeliveryComplete.vue'),
    meta: { requiresDriverAuth: true },
  },
  {
    path: '/driver/account',
    name: 'DriverAccount',
    component: () => import('@/pages/drivee/DriverAccount.vue'),
    meta: { requiresDriverAuth: true },
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

router.beforeEach(async (to) => {
  if (!to.meta.requiresDriverAuth) return true

  const { getLoggedUser, getDriverAccount } = await import('./utils/auth')

  try {
    const user = await getLoggedUser()
    if (!user || user === 'Guest') {
      return { path: '/driver-login', query: { reason: 'auth' } }
    }

    const account = await getDriverAccount(user)
    if (!account) {
      return { path: '/driver-login', query: { reason: 'no_driver' } }
    }
  } catch (error) {
    return { path: '/driver-login', query: { reason: 'auth' } }
  }

  return true
})

export default router
