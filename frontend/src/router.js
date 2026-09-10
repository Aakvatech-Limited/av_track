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
  {
    path: '/dispatch',
    name: 'DispatchMap',
    component: () => import('@/pages/dispatch/DispatchMap.vue'),
    meta: { requiresDispatchAuth: true },
  },
  {
    path: '/dispatch/driver/:driver',
    name: 'DispatchDriverDetail',
    component: () => import('@/pages/dispatch/DispatchDriverDetail.vue'),
    meta: { requiresDispatchAuth: true },
  },
]

let router = createRouter({
  history: createWebHistory('/track'),
  routes,
})

router.beforeEach(async (to) => {
  if (to.meta.requiresDriverAuth) {
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
  }

  if (to.meta.requiresDispatchAuth) {
    const { getLoggedUser } = await import('./utils/auth')

    let user
    try {
      user = await getLoggedUser()
    } catch (error) {
      user = null
    }

    if (!user || user === 'Guest') {
      window.location.href = `/login?redirect-to=${encodeURIComponent('/track' + to.fullPath)}`
      return false
    }

    // Authorization itself (System Manager only, enforced server-side) is
    // checked by the dispatch pages when they load their data - they already
    // show a proper error dialog with the real failure reason if that call
    // is rejected, instead of duplicating the check here with a generic
    // native alert.
    return true
  }

  return true
})

export default router
