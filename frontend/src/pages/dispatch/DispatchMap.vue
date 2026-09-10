<template>
  <div class="flex h-[100dvh] w-full flex-col bg-slate-100">
    <InfoDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :message="dialogMessage"
      :variant="dialogVariant"
    />

    <div class="z-[500] flex flex-shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 py-3 shadow-sm">
      <div class="min-w-0">
        <h1 class="text-lg font-bold text-slate-900">Dispatch</h1>
        <p class="text-xs text-slate-500">{{ onlineCount }} online &middot; {{ drivers.length }} total drivers</p>
      </div>
      <div class="flex flex-shrink-0 items-center gap-2">
        <a
          href="/app/av-track"
          class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200"
        >
          Back to Desk
        </a>
        <button
          type="button"
          class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200"
          @click="handleLogout"
        >
          Log Out
        </button>
      </div>
    </div>

    <div class="relative flex-1">
      <div ref="mapContainer" class="absolute inset-0"></div>

      <div v-if="isLoading" class="absolute inset-x-0 top-3 z-[500] mx-auto w-fit rounded-full bg-white px-4 py-2 text-xs font-semibold text-slate-500 shadow">
        Loading fleet...
      </div>
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

const statusLabelForDriver = (driver) => {
  if (!driver.is_online) return 'Offline'
  if (driver.assigned_orders > 0) return 'On Delivery'
  return 'Available'
}

const initialsForDriver = (driver) => {
  const name = (driver.driver_name || driver.driver || '?').trim()
  const parts = name.split(/\s+/)
  return ((parts[0]?.[0] || '') + (parts[1]?.[0] || '')).toUpperCase() || '?'
}

const escapeHtml = (value) =>
  String(value ?? '').replace(/[&<>"']/g, (ch) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[ch]))

const buildIcon = (driver) => {
  return L.divIcon({
    className: '',
    html: `
      <div style="
        width:36px;height:36px;border-radius:50%;
        background:${colorForDriver(driver)};
        border:3px solid white;
        box-shadow:0 2px 6px rgba(0,0,0,0.4);
        display:flex; align-items:center; justify-content:center;
        color:white; font-weight:700; font-size:13px; font-family:inherit;
        cursor:pointer;
      ">${escapeHtml(initialsForDriver(driver))}</div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  })
}

const popupHtml = (driver) => {
  const name = escapeHtml(driver.driver_name || driver.driver || 'Driver')
  const status = statusLabelForDriver(driver)
  const color = colorForDriver(driver)
  const hasJob = Boolean(driver.current_job)

  const jobBlock = hasJob
    ? `
      <div style="border-top:1px solid #e2e8f0; margin-top:10px; padding-top:10px;">
        <div style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#94a3b8; margin-bottom:6px;">${escapeHtml(driver.current_job)}</div>
        <div style="display:flex; align-items:flex-start; gap:8px; margin-bottom:6px;">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="margin-top:2px; flex-shrink:0;">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <span style="font-size:12px; color:#0f172a;">${escapeHtml(driver.current_job_dropoff_address || 'Dropoff address not set')}</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="flex-shrink:0;">
            <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span style="font-size:12px; color:#0f172a;">${escapeHtml(driver.current_job_customer || 'Unknown customer')}</span>
        </div>
      </div>
    `
    : `
      <div style="border-top:1px solid #e2e8f0; margin-top:10px; padding-top:10px; font-size:12px; color:#94a3b8; font-style:italic;">
        No active job
      </div>
    `

  return `
    <div style="font-family: inherit; min-width: 220px; padding: 2px;">
      <div style="display:flex; align-items:center; gap:8px;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="flex-shrink:0;">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span style="font-weight:700; font-size:13px; color:#0f172a;">${name}</span>
      </div>
      <div style="display:flex; align-items:center; gap:8px; margin-top:8px;">
        <span style="width:8px; height:8px; border-radius:50%; background:${color}; flex-shrink:0; margin-left:4px;"></span>
        <span style="font-size:12px; color:#64748b;">${escapeHtml(status)} &middot; ${driver.assigned_orders || 0} active job${driver.assigned_orders === 1 ? '' : 's'}</span>
      </div>
      ${jobBlock}
      <button
        data-driver="${escapeHtml(driver.driver)}"
        class="dispatch-view-driver-btn"
        style="margin-top: 12px; width: 100%; padding: 8px 0; border-radius: 8px; background: #2563eb; color: white; font-size: 12px; font-weight: 700; border: none; cursor: pointer;"
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
    const icon = buildIcon(driver)

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

  map = L.map(mapContainer.value, { zoomControl: false }).setView(DEFAULT_CENTER, 12)
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)
  map.whenReady(() => map.invalidateSize())

  await loadFleet()

  if (drivers.value.some((d) => d.last_lat != null && d.last_lng != null)) {
    const bounds = L.latLngBounds(
      drivers.value
        .filter((d) => d.last_lat != null && d.last_lng != null)
        .map((d) => [Number(d.last_lat), Number(d.last_lng)])
    )
    map.invalidateSize()
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 })
    setTimeout(() => map?.invalidateSize(), 150)
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
