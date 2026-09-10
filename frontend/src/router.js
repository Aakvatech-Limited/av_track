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
    const { getLoggedUser, getFleetOverview } = await import('./utils/auth')

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

    try {
      // get_fleet_overview is restricted server-side to System Manager, so a
      // successful call here doubles as the access check.
      await getFleetOverview()
    } catch (error) {
      window.alert("Your account doesn't have dispatch access.")
      return { path: '/' }
    }

    return true
  }

  return true
})

export default router
