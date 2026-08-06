<template>
  <div class="min-h-[100dvh] bg-white text-slate-900">
    <InfoDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :message="dialogMessage"
      :variant="dialogVariant"
    />
    <div class="min-h-[100dvh] w-full px-6 py-8 lg:px-12 lg:py-12">
      <div class="mx-0 w-full max-w-none pb-24 lg:w-[420px]">
        <!-- Header -->
        <div class="sticky top-0 z-20 -mx-6 mb-6 flex items-center justify-between bg-white/95 px-6 py-4 backdrop-blur">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600 font-semibold border-2 border-blue-500/60">
              {{ driverInitials }}
            </div>
            <div>
              <h1 class="text-lg font-bold leading-tight">{{ driverName }}</h1>
              <p class="text-slate-500 text-xs">Driver ID: {{ driverId }}</p>
            </div>
          </div>
          <button @click="openNotifications" class="relative flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8a6 6 0 10-12 0c0 7-3 7-3 7h18s-3 0-3-7" />
              <path d="M13.73 21a2 2 0 01-3.46 0" />
            </svg>
            <span v-if="hasUnreadNotifications" class="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500"></span>
          </button>
        </div>

        <!-- Active Status -->
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-5 mb-6 shadow-[0_16px_40px_rgba(15,23,42,0.08)]">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-600">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              </div>
              <div>
                <p class="text-base font-bold">Active Status</p>
                <p class="text-slate-500 text-sm">{{ isActive ? 'Online' : 'Offline' }}</p>
              </div>
            </div>
            <label class="relative flex h-[31px] w-[51px] cursor-pointer items-center rounded-full bg-slate-300 p-0.5" :class="{ 'bg-blue-500': isActive }">
              <div class="h-full w-[27px] rounded-full bg-white shadow-md transition-transform" :class="{ 'translate-x-5': isActive }"></div>
              <input class="invisible absolute" type="checkbox" v-model="isActive" @change="toggleOnline" />
            </label>
          </div>
        </div>

        <!-- Progress -->
        <div class="mb-6">
          <div class="flex items-end justify-between mb-2">
            <div>
              <p class="text-slate-500 text-sm font-medium">Today's Progress</p>
              <p class="text-2xl font-bold">
                {{ completedDeliveries }}
                <span class="text-slate-400 text-lg font-normal">/ {{ dailyGoal }}</span>
              </p>
            </div>
            <span class="text-blue-400 font-semibold text-sm">{{ progressPercentage }}% Goal</span>
          </div>
          <div class="h-3 rounded-full bg-slate-200 overflow-hidden">
            <div class="h-full rounded-full bg-blue-500" :style="{ width: progressPercentage + '%' }"></div>
          </div>
          <p class="text-slate-500 text-xs mt-2">
            {{ remainingDeliveries }} deliveries remaining to hit your daily target
          </p>
        </div>

        <!-- Current Task -->
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-xl font-bold">Current Task</h2>
          <span v-if="currentTask" class="rounded-full bg-red-500/10 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-red-400">
            High Priority
          </span>
        </div>
        <div v-if="currentTask" class="rounded-xl overflow-hidden bg-white border border-slate-200 shadow-[0_18px_45px_rgba(15,23,42,0.1)]">
          <div class="relative h-44">
            <div
              ref="mapContainer"
              class="absolute inset-0 z-0 h-full w-full"
            ></div>
            <div class="absolute inset-0 z-10 bg-gradient-to-br from-slate-200 to-slate-300 opacity-20"></div>
            <div class="absolute inset-0 z-20 bg-gradient-to-t from-black/30 to-transparent"></div>
            <div class="absolute bottom-3 left-4 flex items-center gap-2">
              <span class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white text-blue-500">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
              </span>
              <span class="text-white text-xs font-bold uppercase">
                {{ currentTask.distance_label || 'En Route' }}
              </span>
            </div>
          </div>
          <div class="p-4">
            <div class="flex items-start justify-between mb-4">
              <div>
                <p class="text-lg font-bold">{{ currentTask.dropoff_address || 'Dropoff Address' }}</p>
                <p class="text-slate-500 text-sm">{{ currentTask.pickup_address || '' }}</p>
              </div>
              <div class="text-right">
                <p class="text-blue-400 text-lg font-bold">{{ currentTask.eta_label || '--' }}</p>
                <p class="text-slate-400 text-[10px] uppercase font-bold">ETA</p>
              </div>
            </div>
            <div class="flex items-center justify-between py-2 border-t border-slate-200">
              <div class="flex items-center gap-2">
                <svg class="h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
                <div>
                  <p class="text-slate-600 text-sm font-medium">
                    Customer: {{ currentTask.customer_name || '—' }}
                  </p>
                  <p v-if="currentTask.customer_phone" class="text-xs text-slate-500 font-semibold flex items-center gap-1 mt-0.5">
                    <span>📞</span> {{ currentTask.customer_phone }}
                  </p>
                </div>
              </div>
            </div>
            <div class="flex gap-2 mt-3">
              <router-link
                :to="{ path: '/driver/navigate', query: { job: currentTask.name } }"
                class="flex-1 flex items-center justify-center rounded-lg h-12 px-4 bg-blue-500 text-white text-base font-bold"
              >
                <svg class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                </svg>
                Navigate
              </router-link>
              <button class="flex size-12 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500 shadow-[0_14px_36px_rgba(15,23,42,0.08)]">
          No active task right now.
        </div>

        <!-- Upcoming Stops -->
        <h2 class="text-xl font-bold mt-6 mb-3">Upcoming Stops</h2>
        <div v-if="upcomingStops.length > 0" class="space-y-3">
          <div
            v-for="stop in upcomingStops"
            :key="stop.id"
            class="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition active:scale-[0.99]"
            @click="openStopSheet(stop)"
          >
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-700">
                #{{ stop.id }}
              </div>
              <div>
                <p class="font-bold text-slate-900 text-sm">{{ stop.address }}</p>
                <p class="text-xs text-slate-500 font-medium mt-0.5">
                  {{ stop.customer_name }}
                  <span v-if="stop.customer_phone" class="ml-1 text-slate-400">({{ stop.customer_phone }})</span>
                </p>
              </div>
            </div>
            <span class="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-blue-600">
              {{ stop.status || 'Pending' }}
            </span>
          </div>
        </div>
        <div v-else class="text-xs text-slate-400 italic">No upcoming stops queued.</div>

        <!-- Bottom Nav -->
        <DriverBottomNav />
        <div class="fixed bottom-1 left-1/2 -translate-x-1/2 w-32 h-1 bg-slate-200 rounded-full"></div>
      </div>
    </div>

    <transition name="fade">
      <div
        v-if="showStopSheet"
        class="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm"
        @click="closeStopSheet"
      ></div>
    </transition>
    <transition name="sheet">
      <div
        v-if="showStopSheet"
        class="fixed inset-x-0 bottom-0 z-50 flex max-h-[92%] w-full flex-col overflow-hidden rounded-t-[32px] bg-white shadow-[0_-20px_40px_rgba(15,23,42,0.2)] lg:ml-12 lg:mr-auto lg:max-w-[420px]"
      >
        <div class="flex justify-center py-3">
          <div class="h-1.5 w-12 rounded-full bg-slate-200"></div>
        </div>
        <div class="px-6 pb-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                <span>Stop #{{ selectedStop?.id }}</span>
              </div>
              <h3 class="mt-2 text-xl font-bold text-slate-900">{{ selectedStop?.address }}</h3>
              <p class="mt-1 text-sm text-slate-500">
                {{ selectedStop?.pickup_address || 'Pickup details available' }}
              </p>
            </div>
            <button
              type="button"
              class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-500"
              @click="closeStopSheet"
              aria-label="Close"
            >
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto px-6 pb-28 space-y-5">
          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-xl border border-slate-100 bg-slate-50 p-3">
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Customer</p>
              <p class="mt-1 text-sm font-semibold text-slate-900">{{ selectedStop?.customer_name || '—' }}</p>
            </div>
            <div class="rounded-xl border border-slate-100 bg-slate-50 p-3">
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Phone</p>
              <p class="mt-1 text-sm font-semibold text-slate-900">{{ selectedStop?.customer_phone || '—' }}</p>
            </div>
          </div>
          <div class="rounded-xl border border-blue-100 bg-blue-50 p-4">
            <div class="flex items-center gap-2 text-blue-600 text-xs font-bold uppercase tracking-widest">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8h.01" stroke-linecap="round" />
                <path d="M11 12h1v4h1" stroke-linecap="round" />
                <circle cx="12" cy="12" r="9" />
              </svg>
              Delivery Notes
            </div>
            <p class="mt-2 text-sm text-slate-600 whitespace-pre-wrap">
              {{ selectedStop?.notes || 'No delivery notes provided.' }}
            </p>
          </div>
          
          <div v-if="selectedStop?.items && selectedStop.items.length > 0">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold uppercase tracking-widest text-slate-500">Items to Deliver ({{ selectedStop.items.length }})</h4>
            </div>
            <div class="mt-3 space-y-2">
              <div v-for="(item, idx) in selectedStop.items" :key="idx" class="flex items-center justify-between rounded-lg border border-slate-100 bg-white p-3">
                <div class="flex items-center gap-3 text-slate-600">
                  <svg class="h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20.5 7.5L12 12l-8.5-4.5M3 7.5l9-4.5 9 4.5v9L12 21l-9-4.5v-9z" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  <span class="text-sm font-medium">{{ item.name }}</span>
                </div>
                <span class="text-xs font-bold text-slate-500">x{{ item.qty }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="absolute bottom-0 left-0 right-0 flex flex-col gap-3 border-t border-slate-100 bg-white/95 px-6 py-5">
          <button
            type="button"
            :disabled="isSettingCurrentTask"
            class="h-14 rounded-xl bg-blue-600 text-base font-bold text-white shadow-lg shadow-blue-600/20 disabled:cursor-not-allowed disabled:opacity-60"
            @click="setAsCurrentTask"
          >
            {{ isSettingCurrentTask ? 'Setting...' : 'Set as Current Task' }}
          </button>
          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 rounded-xl border border-slate-200 bg-slate-100 py-3 text-sm font-semibold text-slate-700"
              @click="showReorderComingSoon"
            >
              Reorder Route
            </button>
            <button
              type="button"
              :disabled="!selectedStop?.customer_phone"
              class="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-200 bg-slate-100 text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
              @click="callSelectedCustomer"
            >
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          </div>
          <div class="mx-auto h-1 w-32 rounded-full bg-slate-200"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { io } from 'socket.io-client'
import DriverBottomNav from '@/components/DriverBottomNav.vue'
import InfoDialog from '@/components/InfoDialog.vue'

const isActive = ref(false)
const driverName = ref('')
const driverId = ref('')
const driverInitials = ref('')
const completedDeliveries = ref(0)
const dailyGoal = ref(0)
const hasUnreadNotifications = ref(false)

const progressPercentage = computed(() => {
  if (!dailyGoal.value) return 0
  return Math.round((completedDeliveries.value / dailyGoal.value) * 100)
})

const remainingDeliveries = computed(() => {
  return Math.max(dailyGoal.value - completedDeliveries.value, 0)
})

const upcomingStops = ref([])
const mapProvider = ref('')
const mapApiKey = ref('')
const mapContainer = ref(null)
let mapInstance = null
let mapMarker = null

const currentTask = ref(null)
const showStopSheet = ref(false)
const selectedStop = ref(null)
const isSettingCurrentTask = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')
const dialogVariant = ref('info')

const showDialog = (title, message, variant = 'info') => {
  dialogTitle.value = title
  dialogMessage.value = message
  dialogVariant.value = variant
  dialogVisible.value = true
}

const getInitials = (name) => {
  if (!name) return ''
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] || ''
  const second = parts[1]?.[0] || ''
  return (first + second).toUpperCase()
}

const openNotifications = () => {
  dialogTitle.value = 'Notifications'
  dialogMessage.value = 'You have no new notifications.'
  dialogVariant.value = 'info'
  dialogVisible.value = true
}

const toggleOnline = async () => {
  try {
    const { setDriverOnline } = await import('@/utils/auth')
    const result = await setDriverOnline(isActive.value)
    isActive.value = Boolean(result?.is_online)
  } catch (error) {
    isActive.value = !isActive.value
  }
}

const openStopSheet = (stop) => {
  selectedStop.value = stop
  showStopSheet.value = true
}

const closeStopSheet = () => {
  showStopSheet.value = false
}

const formatStopMeta = (stop) => {
  const parts = []
  if (stop.distance) {
    parts.push(`${stop.distance} miles`)
  }
  parts.push(stop.type || 'Picked Up')
  return parts.join(' • ')
}

const setAsCurrentTask = async () => {
  if (!selectedStop.value?.jobName) return

  if (currentTask.value?.name && currentTask.value.name !== selectedStop.value.jobName) {
    showDialog(
      'Current Task Active',
      'Complete or fail the current En Route task before switching.',
      'warning'
    )
    return
  }

  isSettingCurrentTask.value = true
  try {
    const { updateJobStatus } = await import('@/utils/auth')
    const currentStatus = selectedStop.value.status || ''
    let targetStatus = 'En Route to Pickup'
    if (currentStatus === 'Picked Up') {
      targetStatus = 'En Route to Delivery'
    } else if (currentStatus === 'En Route' || currentStatus === 'En Route to Delivery' || currentStatus === 'En Route to Pickup') {
      targetStatus = currentStatus
    }

    await updateJobStatus(selectedStop.value.jobName, targetStatus)
    closeStopSheet()
    await loadDriverDashboard()
  } catch (error) {
    showDialog('Could Not Update Task', error.message || 'Failed to set this stop as current task.', 'error')
  } finally {
    isSettingCurrentTask.value = false
  }
}

const showReorderComingSoon = () => {
  showDialog('Coming Soon', 'Route reordering is not available yet.', 'info')
}

const callSelectedCustomer = () => {
  const phone = (selectedStop.value?.customer_phone || '').trim()
  if (!phone) {
    showDialog('No Phone Number', 'This stop does not have a customer phone number.', 'warning')
    return
  }
  window.location.href = `tel:${phone.replace(/\s+/g, '')}`
}

const loadDriverDashboard = async () => {
  try {
    const { getDriverDashboard } = await import('@/utils/auth')
    const data = await getDriverDashboard()
    if (!data) return

    const profile = data.profile || {}
    driverName.value = profile.full_name || ''
    driverId.value = profile.driver_id || ''
    driverInitials.value = getInitials(driverName.value)
    isActive.value = Boolean(profile.is_online || profile.is_active)

    const progress = data.progress || {}
    completedDeliveries.value = progress.delivered_total || 0
    dailyGoal.value = progress.goal || progress.assigned_total || 0

    currentTask.value = data.current_task || null

    const mapSettings = data.map || {}
    mapProvider.value = mapSettings.provider || ''
    mapApiKey.value = mapSettings.api_key || ''

    await nextTick()
    await initMap()

    upcomingStops.value = (data.upcoming_stops || []).map((stop, index) => ({
      id: index + 1,
      jobName: stop.name,
      address: stop.dropoff_address || stop.pickup_address || 'Stop',
      distance: stop.distance_label || '',
      type: stop.status || 'Picked Up',
      pickup_address: stop.pickup_address,
      customer_name: stop.customer_name,
      customer_phone: stop.customer_phone,
      notes: stop.notes,
      items: stop.items || [],
    }))
  } catch (error) {
    // keep defaults
  }
}

onMounted(() => {
  loadDriverDashboard()

  const host = window.location.hostname
  const port = window.location.port === '8080' ? ':9001' : (window.location.port ? `:${window.location.port}` : '')
  const protocol = window.location.protocol || 'http:'
  const url = `${protocol}//${host}${port}/${host}`

  try {
    const socket = io(url, { withCredentials: true, reconnectionAttempts: 5 })
    socket.on('new_delivery_job', () => {
      loadDriverDashboard()
      showDialog('New Job Assigned', 'A new delivery job has been assigned to you!', 'info')
    })
    socket.on('delivery_job_status_updated', () => {
      loadDriverDashboard()
    })
  } catch (e) {}

  if (window.frappe?.realtime) {
    window.frappe.realtime.on('new_delivery_job', () => loadDriverDashboard())
    window.frappe.realtime.on('delivery_job_status_updated', () => loadDriverDashboard())
  }
})

watch([currentTask, mapApiKey, mapProvider], () => {
  initMap()
})

const loadGoogleMapsScript = (key) => {
  if (!key) return Promise.reject(new Error('Missing map key'))
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (window.__avTrackGoogleMapsPromise) return window.__avTrackGoogleMapsPromise

  window.__avTrackGoogleMapsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&loading=async&libraries=marker`
    script.async = true
    script.defer = true
    script.onload = () => resolve(window.google.maps)
    script.onerror = () => reject(new Error('Failed to load Google Maps'))
    document.head.appendChild(script)
  })

  return window.__avTrackGoogleMapsPromise
}

const initMap = async () => {
  if (!mapContainer.value || !currentTask.value) return
  if (mapProvider.value !== 'Google Maps') return
  if (!mapApiKey.value) return

  const container = mapContainer.value
  if (!container.clientWidth || !container.clientHeight) {
    setTimeout(() => initMap(), 150)
    return
  }

  const dropLat = currentTask.value.dropoff_lat
  const dropLng = currentTask.value.dropoff_lng
  const pickLat = currentTask.value.pickup_lat
  const pickLng = currentTask.value.pickup_lng

  const lat = dropLat ?? pickLat
  const lng = dropLng ?? pickLng
  if (lat == null || lng == null) return

  const maps = await loadGoogleMapsScript(mapApiKey.value)
  const center = { lat: Number(lat), lng: Number(lng) }

  if (!mapInstance) {
    mapInstance = new maps.Map(mapContainer.value, {
      center,
      zoom: 17,
      mapTypeId: 'roadmap',
      disableDefaultUI: true,
      gestureHandling: 'greedy',
    })
  } else {
    mapInstance.setCenter(center)
  }

  if (!mapMarker) {
    mapMarker = new maps.Marker({
      position: center,
      map: mapInstance,
    })
  } else {
    mapMarker.setPosition(center)
  }

  if (dropLat != null && dropLng != null && pickLat != null && pickLng != null) {
    const bounds = new maps.LatLngBounds()
    bounds.extend({ lat: Number(dropLat), lng: Number(dropLng) })
    bounds.extend({ lat: Number(pickLat), lng: Number(pickLng) })
    const latDiff = Math.abs(Number(dropLat) - Number(pickLat))
    const lngDiff = Math.abs(Number(dropLng) - Number(pickLng))
    const isClose = latDiff < 0.01 && lngDiff < 0.01
    if (isClose) {
      mapInstance.setCenter(center)
      mapInstance.setZoom(17)
    } else {
      mapInstance.fitBounds(bounds, 24)
      maps.event.addListenerOnce(mapInstance, 'bounds_changed', () => {
        const currentZoom = mapInstance.getZoom()
        if (currentZoom && currentZoom > 16) {
          mapInstance.setZoom(16)
        }
      })
    }
  } else {
    mapInstance.setZoom(17)
  }

  maps.event.trigger(mapInstance, 'resize')
  setTimeout(() => {
    mapInstance.setCenter(center)
    mapInstance.setZoom(mapInstance.getZoom() || 17)
  }, 120)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.sheet-enter-active,
.sheet-leave-active {
  transition: transform 0.28s ease, opacity 0.28s ease;
}
.sheet-enter-from,
.sheet-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
