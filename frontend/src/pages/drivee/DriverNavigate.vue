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

        <div v-if="nextStepTitle" class="relative z-20 p-4 pt-10">
          <div class="rounded-2xl border border-white/15 bg-blue-600/95 p-4 text-white shadow-xl backdrop-blur">
            <div class="flex items-center gap-4">
              <div class="flex flex-col items-center">
                <svg class="h-9 w-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 20l8-8-8-8" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M18 12H6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span class="mt-1 text-[10px] font-bold">{{ nextStepDistance }}</span>
              </div>
              <div class="flex flex-col border-l border-white/25 pl-4">
                <p class="text-xs font-medium text-blue-100">{{ nextStepPrefix }}</p>
                <h2 class="text-lg font-bold leading-tight">{{ nextStepTitle }}</h2>
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
                  <h3 class="text-2xl font-bold text-slate-900">{{ etaText }}</h3>
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
              <button
                type="button"
                :disabled="isConfirmingPickup"
                @click="handleArrived"
                class="flex flex-1 items-center justify-center rounded-2xl bg-blue-600 py-4 text-sm font-bold text-white shadow-lg shadow-blue-600/30 transition active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                {{ isConfirmingPickup ? 'Confirming...' : arrivedLabel }}
              </button>
              <button
                type="button"
                @click="showDelayModal = true"
                class="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-50 text-amber-600 border border-amber-200 transition active:scale-95"
                title="Report Delay"
              >
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
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

    <!-- Report Delay Modal -->
    <transition name="fade">
      <div v-if="showDelayModal" class="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm" @click="showDelayModal = false"></div>
    </transition>
    <transition name="sheet">
      <div v-if="showDelayModal" class="fixed inset-x-0 bottom-0 z-50 flex max-h-[92%] w-full flex-col overflow-hidden rounded-t-[32px] bg-white p-6 shadow-2xl lg:ml-12 lg:mr-auto lg:max-w-[420px]">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-slate-900">Report Delivery Delay</h3>
          <button @click="showDelayModal = false" class="rounded-full bg-slate-100 p-2 text-slate-500">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        
        <p class="text-xs font-semibold text-slate-500 mb-2">Select reason for delay:</p>
        <div class="grid grid-cols-2 gap-2 mb-4">
          <button
            v-for="reason in delayReasons"
            :key="reason"
            type="button"
            @click="selectedDelayReason = reason"
            class="rounded-xl border px-3 py-2.5 text-xs font-semibold transition text-left"
            :class="selectedDelayReason === reason ? 'border-amber-500 bg-amber-50 text-amber-700 font-bold' : 'border-slate-200 bg-slate-50 text-slate-700'"
          >
            {{ reason }}
          </button>
        </div>
        
        <label class="text-xs font-medium text-slate-500 mb-1">Additional Notes (Optional)</label>
        <textarea
          v-model="delayNotes"
          rows="2"
          placeholder="Explain cause of delay..."
          class="w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-amber-500 focus:outline-none mb-4"
        ></textarea>

        <div class="flex gap-3">
          <button @click="showDelayModal = false" class="flex-1 rounded-xl bg-slate-100 py-3 text-sm font-bold text-slate-700">Cancel</button>
          <button @click="submitDelay" :disabled="!selectedDelayReason || isSubmittingDelay" class="flex-1 rounded-xl bg-amber-500 py-3 text-sm font-bold text-white shadow-lg shadow-amber-500/20 disabled:opacity-50">
            {{ isSubmittingDelay ? 'Submitting...' : 'Submit Delay' }}
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDriverDashboard, postLocationPing, logDeliveryDelay, updateJobStatus } from '@/utils/auth'

const showDelayModal = ref(false)
const selectedDelayReason = ref('')
const delayNotes = ref('')
const isSubmittingDelay = ref(false)
const delayReasons = [
  'Traffic Congestion',
  'Vehicle Breakdown',
  'Store Delay',
  'Customer Not In Place',
  'Weather Conditions',
  'Other'
]

const submitDelay = async () => {
  if (!currentTask.value?.name || !selectedDelayReason.value) return
  isSubmittingDelay.value = true
  try {
    await logDeliveryDelay(currentTask.value.name, selectedDelayReason.value, delayNotes.value)
    showDelayModal.value = false
    selectedDelayReason.value = ''
    delayNotes.value = ''
    alert('Delay report submitted successfully to dispatch.')
  } catch (err) {
    alert('Failed to report delay: ' + (err.message || 'Unknown error'))
  } finally {
    isSubmittingDelay.value = false
  }
}

const route = useRoute()
const router = useRouter()
const isConfirmingPickup = ref(false)
const mapContainer = ref(null)
const hasMap = ref(false)
const currentTask = ref(null)
const mapProvider = ref('')
const mapApiKey = ref('')
const routeSummary = ref({
  durationText: '',
  distanceText: '',
  stepDistance: '',
  stepInstruction: '',
})

let mapInstance = null
let mapMarker = null
let directionsRenderer = null
let pingIntervalId = null

const PING_INTERVAL_MS = 30000
const DEVICE_ID_KEY = 'av-track-device-id'

const etaText = computed(() => {
  const durationText = routeSummary.value.durationText
  if (durationText) {
    return durationText
  }
  if (!currentTask.value) return '--'
  return currentTask.value.eta_label || '--'
})

const distanceLabel = computed(() => {
  if (routeSummary.value.distanceText) return `(${routeSummary.value.distanceText})`
  if (!currentTask.value) return ''
  return currentTask.value.distance_label ? `(${currentTask.value.distance_label})` : ''
})

const isPickupLeg = computed(() => currentTask.value?.status === 'En Route to Pickup')

const taskAddress = computed(() => {
  if (!currentTask.value) return 'Unknown Destination'
  if (isPickupLeg.value) {
    return currentTask.value.pickup_address || currentTask.value.dropoff_address || 'Address not provided'
  }
  return currentTask.value.dropoff_address || currentTask.value.pickup_address || 'Address not provided'
})

const taskSubAddress = computed(() => {
  if (!currentTask.value) return ''
  if (isPickupLeg.value) return ''
  return currentTask.value.pickup_address && currentTask.value.dropoff_address
    ? currentTask.value.pickup_address
    : ''
})

const arrivedLabel = computed(() => (isPickupLeg.value ? 'Confirm Pickup' : 'Arrived'))

const customerName = computed(() => {
  if (!currentTask.value) return 'Customer'
  return currentTask.value.customer_name || 'Customer'
})

const nextStepDistance = computed(() => routeSummary.value.stepDistance || '')

const nextStepTitle = computed(() => routeSummary.value.stepInstruction || '')

const nextStepPrefix = computed(() =>
  routeSummary.value.stepInstruction ? 'Next step' : 'Continue to'
)

const handleArrived = async () => {
  if (!currentTask.value?.name) return

  if (!isPickupLeg.value) {
    router.push({
      path: '/driver/complete',
      query: { job: currentTask.value.name || route.query.job || '' },
    })
    return
  }

  isConfirmingPickup.value = true
  try {
    const position = await getCurrentPosition()
    await updateJobStatus(currentTask.value.name, 'Picked Up', {
      lat: position.lat,
      lng: position.lng,
    })
    router.push('/driver/dashboard')
  } catch (error) {
    alert('Could not confirm pickup: ' + (error.message || 'Unknown error'))
  } finally {
    isConfirmingPickup.value = false
  }
}

const getOrCreateDeviceId = () => {
  try {
    const existing = localStorage.getItem(DEVICE_ID_KEY)
    if (existing) return existing
    const generated = `avt-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
    localStorage.setItem(DEVICE_ID_KEY, generated)
    return generated
  } catch (error) {
    return null
  }
}

const getCurrentPosition = () =>
  new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({ lat: null, lng: null, accuracy: null })
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
        })
      },
      () => resolve({ lat: null, lng: null, accuracy: null }),
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 15000 }
    )
  })

let driverMarker = null

const sendLocationPing = async () => {
  const jobId = currentTask.value?.name
  if (!jobId) return

  const position = await getCurrentPosition()
  if (position.lat == null || position.lng == null) return

  if (mapInstance && window.google?.maps) {
    const driverPos = { lat: Number(position.lat), lng: Number(position.lng) }
    if (!driverMarker) {
      driverMarker = new window.google.maps.Marker({
        position: driverPos,
        map: mapInstance,
        title: 'Driver Current Location',
        icon: {
          path: window.google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          scale: 6,
          fillColor: '#1d4ed8',
          fillOpacity: 1,
          strokeWeight: 2,
          strokeColor: '#ffffff',
        },
      })
    } else {
      driverMarker.setPosition(driverPos)
    }
  }

  try {
    await postLocationPing({
      lat: position.lat,
      lng: position.lng,
      accuracy: position.accuracy,
      jobId,
      deviceId: getOrCreateDeviceId(),
    })
  } catch (error) {
    // Keep silent; retry on next cycle.
  }
}

const startLocationPingLoop = () => {
  if (pingIntervalId || !currentTask.value?.name) return
  sendLocationPing()
  pingIntervalId = window.setInterval(sendLocationPing, PING_INTERVAL_MS)
}

const stopLocationPingLoop = () => {
  if (!pingIntervalId) return
  window.clearInterval(pingIntervalId)
  pingIntervalId = null
}

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

const stripHtml = (rawText) => {
  if (!rawText) return ''
  return rawText.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()
}

const resetRouteSummary = () => {
  routeSummary.value = {
    durationText: '',
    distanceText: '',
    stepDistance: '',
    stepInstruction: '',
  }
}

const clearDirections = () => {
  if (!directionsRenderer) return
  directionsRenderer.setMap(null)
  directionsRenderer = null
}

const recenterMap = () => {
  if (!mapInstance || !currentTask.value) return
  const lat = isPickupLeg.value
    ? (currentTask.value.pickup_lat ?? currentTask.value.dropoff_lat)
    : (currentTask.value.dropoff_lat ?? currentTask.value.pickup_lat)
  const lng = isPickupLeg.value
    ? (currentTask.value.pickup_lng ?? currentTask.value.dropoff_lng)
    : (currentTask.value.dropoff_lng ?? currentTask.value.pickup_lng)
  if (lat == null || lng == null) return
  const center = { lat: Number(lat), lng: Number(lng) }
  if (directionsRenderer?.getDirections()?.routes?.[0]) {
    mapInstance.fitBounds(directionsRenderer.getDirections().routes[0].bounds, 40)
    return
  }
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

  const pickupLeg = isPickupLeg.value
  const destLat = pickupLeg
    ? (currentTask.value.pickup_lat ?? currentTask.value.dropoff_lat)
    : (currentTask.value.dropoff_lat ?? currentTask.value.pickup_lat)
  const destLng = pickupLeg
    ? (currentTask.value.pickup_lng ?? currentTask.value.dropoff_lng)
    : (currentTask.value.dropoff_lng ?? currentTask.value.pickup_lng)
  if (destLat == null || destLng == null) return

  // On the pickup leg, route from the driver's live position to the pickup point.
  // On the delivery leg, route from the pickup point to the dropoff point.
  let originLat = currentTask.value.pickup_lat
  let originLng = currentTask.value.pickup_lng
  if (pickupLeg) {
    const position = await getCurrentPosition()
    originLat = position.lat
    originLng = position.lng
  }

  const maps = await loadGoogleMapsScript(mapApiKey.value)
  const center = { lat: Number(destLat), lng: Number(destLng) }

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
  } else {
    mapInstance.setCenter(center)
  }

  if (!directionsRenderer) {
    directionsRenderer = new maps.DirectionsRenderer({
      map: mapInstance,
      suppressMarkers: false,
      preserveViewport: true,
      polylineOptions: {
        strokeColor: '#137fec',
        strokeOpacity: 0.9,
        strokeWeight: 5,
      },
    })
  }

  const canDrawRoute = originLat != null && originLng != null

  if (canDrawRoute) {
    const directionsService = new maps.DirectionsService()
    try {
      const response = await directionsService.route({
        origin: { lat: Number(originLat), lng: Number(originLng) },
        destination: { lat: Number(destLat), lng: Number(destLng) },
        travelMode: maps.TravelMode.DRIVING,
      })
      directionsRenderer.setDirections(response)

      const route = response.routes?.[0]
      const leg = route?.legs?.[0]
      const step = leg?.steps?.[0]

      routeSummary.value = {
        durationText: leg?.duration?.text || '',
        distanceText: leg?.distance?.text || '',
        stepDistance: step?.distance?.text || '',
        stepInstruction: stripHtml(step?.instructions || ''),
      }

      if (route?.bounds) {
        mapInstance.fitBounds(route.bounds, 40)
      }

      if (mapMarker) {
        mapMarker.setMap(null)
        mapMarker = null
      }
    } catch (error) {
      resetRouteSummary()
      clearDirections()
      if (!mapMarker) {
        mapMarker = new maps.Marker({
          position: center,
          map: mapInstance,
        })
      } else {
        mapMarker.setPosition(center)
      }
      mapInstance.setCenter(center)
      mapInstance.setZoom(17)
    }
  } else {
    resetRouteSummary()
    clearDirections()
    if (!mapMarker) {
      mapMarker = new maps.Marker({
        position: center,
        map: mapInstance,
      })
    } else {
      mapMarker.setPosition(center)
    }
    mapInstance.setCenter(center)
    mapInstance.setZoom(17)
  }

  hasMap.value = true
  maps.event.trigger(mapInstance, 'resize')
  setTimeout(() => {
    if (directionsRenderer?.getDirections()?.routes?.[0]?.bounds) {
      mapInstance.fitBounds(directionsRenderer.getDirections().routes[0].bounds, 40)
    } else {
      mapInstance.setCenter(center)
      mapInstance.setZoom(17)
    }
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
    if (currentTask.value?.name) {
      startLocationPingLoop()
    } else {
      stopLocationPingLoop()
    }
  } catch (error) {
    // Keep graceful fallback background.
  }
}

onMounted(() => {
  loadNavigateData()
})

watch(
  () => currentTask.value?.name,
  (jobId) => {
    if (jobId) {
      startLocationPingLoop()
    } else {
      stopLocationPingLoop()
    }
  }
)

onBeforeUnmount(() => {
  stopLocationPingLoop()
})
</script>
