<template>
  <div class="min-h-[100dvh] bg-slate-100 text-slate-900">
    <div class="h-[100dvh] w-full px-6 py-6 lg:px-12 lg:py-10">
      <div class="relative mx-0 h-full w-full max-w-none overflow-hidden rounded-[32px] bg-white shadow-[0_24px_60px_rgba(15,23,42,0.16)] lg:w-[420px]">
        <div ref="mapContainer" class="absolute inset-0 z-0"></div>
        <div
          v-if="!hasMap"
          class="pointer-events-none absolute inset-0 z-10 bg-gradient-to-br from-slate-200 to-slate-300"
        ></div>
        <div class="pointer-events-none absolute inset-0 z-10 bg-black/10"></div>

        <div class="relative z-20 p-4 pt-10">
          <div class="rounded-2xl border border-white/15 bg-blue-600/95 p-4 text-white shadow-xl backdrop-blur">
            <div class="flex items-center gap-4">
              <div class="flex flex-col items-center">
                <svg class="h-9 w-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 20l8-8-8-8" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M18 12H6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span class="mt-1 text-[10px] font-bold">400 ft</span>
              </div>
              <div class="flex flex-col border-l border-white/25 pl-4">
                <p class="text-xs font-medium text-blue-100">Turn right onto</p>
                <h2 class="text-lg font-bold leading-tight">Marketplace Blvd</h2>
              </div>
            </div>
          </div>
        </div>

        <div class="absolute right-4 top-1/2 z-20 flex -translate-y-1/2 flex-col gap-3">
          <button
            class="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-slate-900 shadow-lg backdrop-blur"
            @click="recenterMap"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9" />
              <circle cx="12" cy="12" r="2" />
              <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke-linecap="round" />
            </svg>
          </button>
          <button
            class="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-slate-900 shadow-lg backdrop-blur"
            @click="zoomInMap"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="absolute bottom-0 left-0 right-0 z-20 px-4 pb-8">
          <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-2xl">
            <div class="mb-6 flex items-start justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-red-500"></span>
                  <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Arriving In</p>
                </div>
                <div class="mt-1 flex items-baseline gap-2">
                  <h3 class="text-3xl font-bold text-slate-900">{{ etaMinutes }}</h3>
                  <span class="text-lg font-bold text-slate-900">min</span>
                  <span class="text-sm font-medium text-slate-400">{{ distanceLabel }}</span>
                </div>
              </div>
              <div class="rounded-xl bg-slate-100 p-2">
                <svg class="h-7 w-7 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>

            <div class="mb-8 space-y-4">
              <div class="flex items-start gap-4">
                <svg class="mt-1 h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 21s7-4.4 7-11a7 7 0 1 0-14 0c0 6.6 7 11 7 11z" stroke-linecap="round" stroke-linejoin="round" />
                  <circle cx="12" cy="10" r="2.5" />
                </svg>
                <div>
                  <p class="text-lg font-bold text-slate-900">{{ taskAddress }}</p>
                  <p class="text-sm text-slate-500">{{ taskSubAddress }}</p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <svg class="h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
                <p class="text-base font-semibold text-slate-700">{{ customerName }}</p>
              </div>
            </div>

            <div class="flex gap-3">
              <router-link
                to="/driver/dashboard"
                class="flex flex-1 items-center justify-center rounded-2xl bg-red-50 py-4 text-sm font-bold text-red-600 transition active:scale-95"
              >
                <svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                Exit
              </router-link>
              <router-link
                to="/driver/complete"
                class="flex flex-1 items-center justify-center rounded-2xl bg-blue-600 py-4 text-sm font-bold text-white shadow-lg shadow-blue-600/30 transition active:scale-95"
              >
                <svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                Arrived
              </router-link>
              <button class="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-700 transition active:scale-95">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="pointer-events-none absolute bottom-3 left-1/2 z-30 h-1 w-32 -translate-x-1/2 rounded-full bg-slate-300"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { getDriverDashboard } from '@/utils/auth'

const mapContainer = ref(null)
const hasMap = ref(false)
const currentTask = ref(null)
const mapProvider = ref('')
const mapApiKey = ref('')

let mapInstance = null
let mapMarker = null

const etaMinutes = computed(() => {
  if (!currentTask.value) return '8'
  const eta = currentTask.value.eta_label || ''
  const numeric = String(eta).match(/\d+/)
  return numeric ? numeric[0] : '8'
})

const distanceLabel = computed(() => {
  if (!currentTask.value) return '(1.2 miles)'
  return currentTask.value.distance_label ? `(${currentTask.value.distance_label})` : '(1.2 miles)'
})

const taskAddress = computed(() => {
  if (!currentTask.value) return 'Current task address'
  return currentTask.value.dropoff_address || currentTask.value.pickup_address || 'Current task address'
})

const taskSubAddress = computed(() => {
  if (!currentTask.value) return 'Navigation preview'
  return currentTask.value.pickup_address || 'Navigation preview'
})

const customerName = computed(() => {
  if (!currentTask.value) return 'Customer'
  return currentTask.value.customer_name || 'Customer'
})

const loadGoogleMapsScript = (key) => {
  if (!key) return Promise.reject(new Error('Missing map key'))
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (window.__avTrackGoogleMapsPromise) return window.__avTrackGoogleMapsPromise

  window.__avTrackGoogleMapsPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${key}&loading=async`
    script.async = true
    script.defer = true
    script.onload = () => resolve(window.google.maps)
    script.onerror = () => reject(new Error('Failed to load Google Maps'))
    document.head.appendChild(script)
  })
  return window.__avTrackGoogleMapsPromise
}

const recenterMap = () => {
  if (!mapInstance || !currentTask.value) return
  const lat = currentTask.value.dropoff_lat ?? currentTask.value.pickup_lat
  const lng = currentTask.value.dropoff_lng ?? currentTask.value.pickup_lng
  if (lat == null || lng == null) return
  const center = { lat: Number(lat), lng: Number(lng) }
  mapInstance.setCenter(center)
  mapInstance.setZoom(17)
}

const zoomInMap = () => {
  if (!mapInstance) return
  const current = mapInstance.getZoom() || 17
  mapInstance.setZoom(Math.min(current + 1, 20))
}

const initMap = async () => {
  if (!mapContainer.value || !currentTask.value) return
  if (mapProvider.value !== 'Google Maps') return
  if (!mapApiKey.value) return

  const lat = currentTask.value.dropoff_lat ?? currentTask.value.pickup_lat
  const lng = currentTask.value.dropoff_lng ?? currentTask.value.pickup_lng
  if (lat == null || lng == null) return

  const maps = await loadGoogleMapsScript(mapApiKey.value)
  const center = { lat: Number(lat), lng: Number(lng) }

  if (!mapInstance) {
    mapInstance = new maps.Map(mapContainer.value, {
      center,
      zoom: 17,
      mapTypeId: maps.MapTypeId.ROADMAP,
      disableDefaultUI: true,
      gestureHandling: 'greedy',
      draggable: true,
      scrollwheel: true,
      disableDoubleClickZoom: false,
    })
    maps.event.addListenerOnce(mapInstance, 'idle', () => {
      mapInstance.setCenter(center)
      mapInstance.setZoom(17)
    })
  } else {
    mapInstance.setCenter(center)
    mapInstance.setZoom(17)
  }

  if (!mapMarker) {
    mapMarker = new maps.Marker({
      position: center,
      map: mapInstance,
    })
  } else {
    mapMarker.setPosition(center)
  }

  hasMap.value = true
  maps.event.trigger(mapInstance, 'resize')
  setTimeout(() => {
    mapInstance.setCenter(center)
    mapInstance.setZoom(17)
  }, 150)
}

const loadNavigateData = async () => {
  try {
    const data = await getDriverDashboard()
    if (!data) return
    currentTask.value = data.current_task || null
    mapProvider.value = data.map?.provider || ''
    mapApiKey.value = data.map?.api_key || ''
    await nextTick()
    await initMap()
  } catch (error) {
    // Keep graceful fallback background.
  }
}

onMounted(() => {
  loadNavigateData()
})
</script>
