<template>
  <div class="relative h-[100dvh] w-full bg-slate-100">
    <InfoDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :message="dialogMessage"
      :variant="dialogVariant"
    />

    <div class="absolute inset-x-0 top-0 z-[500] flex items-center justify-between bg-white/95 px-4 py-3 shadow-sm backdrop-blur">
      <div>
        <h1 class="text-lg font-bold text-slate-900">Dispatch</h1>
        <p class="text-xs text-slate-500">{{ onlineCount }} online &middot; {{ drivers.length }} total drivers</p>
      </div>
      <button
        type="button"
        class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200"
        @click="handleLogout"
      >
        Log Out
      </button>
    </div>

    <div ref="mapContainer" class="absolute inset-0"></div>

    <div v-if="isLoading" class="absolute inset-x-0 top-16 z-[500] mx-auto w-fit rounded-full bg-white px-4 py-2 text-xs font-semibold text-slate-500 shadow">
      Loading fleet...
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getFleetOverview, logout } from '@/utils/auth'
import InfoDialog from '@/components/InfoDialog.vue'

const router = useRouter()
const mapContainer = ref(null)
const isLoading = ref(true)
const drivers = ref([])
const onlineCount = ref(0)

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

const DEFAULT_CENTER = [-6.7924, 39.2083] // Dar es Salaam fallback
const REFRESH_INTERVAL_MS = 20000

let map = null
let markers = {}
let refreshTimer = null
let L = null

const colorForDriver = (driver) => {
  if (!driver.is_online) return '#94a3b8' // slate - offline
  if (driver.assigned_orders > 0) return '#2563eb' // blue - on delivery
  return '#16a34a' // green - online, available
}

const buildIcon = (color) => {
  return L.divIcon({
    className: '',
    html: `<div style="width:16px;height:16px;border-radius:50%;background:${color};border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.4);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  })
}

const popupHtml = (driver) => {
  const name = driver.driver_name || driver.driver || 'Driver'
  const status = driver.current_status || (driver.is_online ? 'Available' : 'Offline')
  return `
    <div style="font-family: inherit; min-width: 160px;">
      <div style="font-weight: 700; font-size: 13px; color: #0f172a;">${name}</div>
      <div style="font-size: 12px; color: #475569; margin-top: 2px;">${status}</div>
      <div style="font-size: 12px; color: #475569;">Assigned orders (${driver.assigned_orders || 0})</div>
      <button
        data-driver="${driver.driver}"
        class="dispatch-view-driver-btn"
        style="margin-top: 8px; width: 100%; padding: 6px 0; border-radius: 8px; background: #2563eb; color: white; font-size: 12px; font-weight: 600; border: none; cursor: pointer;"
      >View Details</button>
    </div>
  `
}

const renderDrivers = () => {
  if (!map || !L) return

  const seen = new Set()

  drivers.value.forEach((driver) => {
    if (driver.last_lat == null || driver.last_lng == null) return
    seen.add(driver.driver)

    const position = [Number(driver.last_lat), Number(driver.last_lng)]
    const icon = buildIcon(colorForDriver(driver))

    if (markers[driver.driver]) {
      markers[driver.driver].setLatLng(position)
      markers[driver.driver].setIcon(icon)
      markers[driver.driver].setPopupContent(popupHtml(driver))
    } else {
      const marker = L.marker(position, { icon }).addTo(map)
      marker.bindPopup(popupHtml(driver))
      marker.on('popupopen', () => {
        const btn = document.querySelector(`.dispatch-view-driver-btn[data-driver="${driver.driver}"]`)
        if (btn) {
          btn.addEventListener('click', () => {
            router.push(`/dispatch/driver/${encodeURIComponent(driver.driver)}`)
          })
        }
      })
      markers[driver.driver] = marker
    }
  })

  // Remove markers for drivers no longer present/online with a location
  Object.keys(markers).forEach((driverId) => {
    if (!seen.has(driverId)) {
      markers[driverId].remove()
      delete markers[driverId]
    }
  })
}

const loadFleet = async () => {
  try {
    const data = await getFleetOverview()
    drivers.value = Array.isArray(data) ? data : []
    onlineCount.value = drivers.value.filter((d) => d.is_online).length
    renderDrivers()
  } catch (error) {
    showDialog('Could Not Load Fleet', error.message || 'Unknown error', 'error')
  } finally {
    isLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await logout()
  } catch (error) {
    // ignore
  }
  // The route guard will bounce straight to Frappe's own login page.
  router.push('/dispatch')
}

onMounted(async () => {
  const leaflet = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  L = leaflet.default

  map = L.map(mapContainer.value).setView(DEFAULT_CENTER, 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)

  await loadFleet()

  if (drivers.value.some((d) => d.last_lat != null && d.last_lng != null)) {
    const bounds = L.latLngBounds(
      drivers.value
        .filter((d) => d.last_lat != null && d.last_lng != null)
        .map((d) => [Number(d.last_lat), Number(d.last_lng)])
    )
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 })
  }

  refreshTimer = window.setInterval(loadFleet, REFRESH_INTERVAL_MS)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (map) {
    map.remove()
    map = null
  }
  markers = {}
})
</script>
