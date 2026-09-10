<template>
  <div class="min-h-[100dvh] bg-slate-50">
    <InfoDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :message="dialogMessage"
      :variant="dialogVariant"
    />

    <div class="sticky top-0 z-20 flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 shadow-sm">
      <router-link
        to="/dispatch"
        class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-700 hover:bg-slate-50"
        aria-label="Back to fleet map"
      >
        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </router-link>
      <div>
        <h1 class="text-base font-bold text-slate-900">{{ driver?.driver_name || 'Driver' }}</h1>
        <p class="flex items-center gap-1.5 text-xs font-semibold" :class="driver?.is_online && !isStale ? 'text-emerald-600' : 'text-slate-400'">
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="[driver?.is_online && !isStale ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300']"
          ></span>
          {{ driver?.is_online ? (isStale ? 'Stale' : 'Online') : 'Offline' }}
          <span v-if="driver?.last_ping_at" class="text-slate-400 font-normal">&middot; updated {{ lastSeenLabel }}</span>
        </p>
      </div>
    </div>

    <div ref="mapContainer" class="h-56 w-full border-b border-slate-200"></div>

    <div class="px-4 py-4">
      <h2 class="text-sm font-bold text-slate-900">Assigned Jobs ({{ jobs.length }})</h2>

      <div v-if="isLoading" class="mt-4 text-xs text-slate-400 italic">Loading...</div>
      <div v-else-if="jobs.length === 0" class="mt-4 rounded-xl border border-dashed border-slate-200 bg-white px-4 py-6 text-center text-sm text-slate-500">
        No active jobs assigned to this driver.
      </div>

      <div v-else class="mt-3 space-y-3">
        <div
          v-for="job in jobs"
          :key="job.name"
          class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">{{ job.name }}</p>
              <p class="mt-0.5 text-xs text-slate-500">{{ job.customer_name || 'Unknown customer' }}</p>
            </div>
            <span class="flex-shrink-0 whitespace-nowrap rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-blue-600">
              {{ job.status }}
            </span>
          </div>

          <div class="mt-3 space-y-2 border-t border-slate-100 pt-3">
            <div v-if="job.pickup_address" class="flex items-start gap-2">
              <svg class="mt-0.5 h-4 w-4 flex-shrink-0 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 2v3M12 19v3M2 12h3M19 12h3" stroke-linecap="round" />
              </svg>
              <p class="text-xs text-slate-600">{{ job.pickup_address }}</p>
            </div>
            <div class="flex items-start gap-2">
              <svg class="mt-0.5 h-4 w-4 flex-shrink-0 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <p class="text-xs font-semibold text-slate-700">{{ job.dropoff_address || 'Dropoff address not set' }}</p>
            </div>
          </div>

          <p v-if="job.last_status_at" class="mt-3 text-[10px] text-slate-400">
            Status updated {{ formatTimestamp(job.last_status_at) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getDriverRouteDetail } from '@/utils/auth'
import { createTrackingSocket } from '@/utils/socket'
import { tweenMarker, bearingBetween } from '@/utils/mapMotion'
import InfoDialog from '@/components/InfoDialog.vue'

const REFRESH_INTERVAL_MS = 60000 // safety net only - live pushes do the real work now
const STALE_MS = 90000
const TRAIL_LENGTH = 8

const route = useRoute()
const mapContainer = ref(null)
const isLoading = ref(true)
const driver = ref(null)
const jobs = ref([])
const nowTick = ref(Date.now())

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

const initials = computed(() => {
  const name = (driver.value?.driver_name || driver.value?.driver || '?').trim()
  const parts = name.split(/\s+/)
  return ((parts[0]?.[0] || '') + (parts[1]?.[0] || '')).toUpperCase() || '?'
})

const pingTimeMs = () => {
  if (!driver.value?.last_ping_at) return null
  return new Date(String(driver.value.last_ping_at).replace(' ', 'T')).getTime()
}

const isStale = computed(() => {
  const pingTime = pingTimeMs()
  if (pingTime == null) return false
  return nowTick.value - pingTime > STALE_MS
})

const lastSeenLabel = computed(() => {
  const pingTime = pingTimeMs()
  if (pingTime == null) return ''
  const diffSec = Math.max(0, Math.round((nowTick.value - pingTime) / 1000))
  if (diffSec < 5) return 'just now'
  if (diffSec < 60) return `${diffSec}s ago`
  const diffMin = Math.round(diffSec / 60)
  if (diffMin < 60) return `${diffMin}m ago`
  return `${Math.round(diffMin / 60)}h ago`
})

const formatTimestamp = (value) => {
  if (!value) return ''
  try {
    return new Date(value.replace(' ', 'T')).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (error) {
    return value
  }
}

let map = null
let marker = null
let L = null
let trail = []
let trailLayers = []
let heading = null
let refreshTimer = null
let tickTimer = null
let socket = null

const buildDriverIcon = () => {
  const arrow = heading != null
    ? `<div style="position:absolute; top:-8px; left:50%; transform:translateX(-50%); width:0; height:0; border-left:5px solid transparent; border-right:5px solid transparent; border-bottom:8px solid #2563eb;"></div>`
    : ''

  return L.divIcon({
    className: '',
    html: `
      <div style="position:relative; width:36px; height:36px; transform: rotate(${heading || 0}deg);">
        ${arrow}
        <div style="
          width:36px;height:36px;border-radius:50%;
          background:#2563eb;
          border:3px solid white;
          box-shadow:0 2px 6px rgba(0,0,0,0.4);
          display:flex; align-items:center; justify-content:center;
          color:white; font-weight:700; font-size:13px; font-family:inherit;
          transform: rotate(${-(heading || 0)}deg);
        ">${initials.value}</div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  })
}

const redrawTrail = () => {
  if (!map || !L) return
  trailLayers.forEach((line) => line.remove())
  trailLayers = []
  for (let i = 1; i < trail.length; i++) {
    const opacity = 0.15 + (i / trail.length) * 0.35
    trailLayers.push(
      L.polyline([trail[i - 1], trail[i]], { color: '#2563eb', weight: 3, opacity }).addTo(map)
    )
  }
}

const renderMap = () => {
  if (!map || !L || !driver.value) return
  if (driver.value.last_lat == null || driver.value.last_lng == null) return

  const position = [Number(driver.value.last_lat), Number(driver.value.last_lng)]
  map.invalidateSize()
  map.setView(position, 15)

  trail = [position]
  marker = L.marker(position, { icon: buildDriverIcon() }).addTo(map)

  // The container's final size can settle a beat after layout/paint
  // (route transition, PWA chrome), so re-check once more or the tile
  // grid stays sized to whatever it was at construction time.
  setTimeout(() => {
    map?.invalidateSize()
  }, 150)
}

// Applies a live location push: glides the marker instead of teleporting,
// and does NOT re-center the map - that would fight the dispatcher's own
// pan/zoom every time the driver moves.
const applyLiveLocation = (lat, lng) => {
  if (!map || !L || !marker) return

  const toPos = [Number(lat), Number(lng)]
  const fromPos = trail.length ? trail[trail.length - 1] : toPos

  trail.push(toPos)
  if (trail.length > TRAIL_LENGTH) trail.shift()
  if (trail.length >= 2) {
    heading = bearingBetween(trail[trail.length - 2], trail[trail.length - 1])
  }
  redrawTrail()

  tweenMarker(marker, fromPos, toPos)
  marker.setIcon(buildDriverIcon())
}

const loadDriver = async ({ initial = false } = {}) => {
  try {
    const data = await getDriverRouteDetail(route.params.driver)
    jobs.value = data?.jobs || []

    if (!driver.value) {
      driver.value = data
    } else {
      driver.value.driver_name = data.driver_name
      driver.value.is_online = data.is_online
      driver.value.last_ping_at = data.last_ping_at
    }

    if (initial) {
      renderMap()
    } else if (data.last_lat != null && data.last_lng != null) {
      // Route any refetch (job event or safety-net poll) through the same
      // tween path a live ping uses, so the marker self-corrects instead
      // of jumping or drifting out of sync with what's actually on screen.
      applyLiveLocation(data.last_lat, data.last_lng)
    }
  } catch (error) {
    showDialog('Could Not Load Driver', error.message || 'Unknown error', 'error')
  } finally {
    isLoading.value = false
  }
}

const handleJobEvent = (data) => {
  if (data?.driver === route.params.driver) loadDriver()
}

const handleJobStatusEvent = (data) => {
  if (data?.assigned_driver === route.params.driver) loadDriver()
}

onMounted(async () => {
  const leaflet = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  L = leaflet.default

  map = L.map(mapContainer.value).setView([-6.7924, 39.2083], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)
  map.whenReady(() => map.invalidateSize())

  await loadDriver({ initial: true })

  tickTimer = window.setInterval(() => {
    nowTick.value = Date.now()
  }, 1000)
  refreshTimer = window.setInterval(() => loadDriver(), REFRESH_INTERVAL_MS)

  socket = createTrackingSocket()
  socket.on('driver_location_updated', (data) => {
    if (data?.driver !== route.params.driver) return
    if (driver.value) driver.value.last_ping_at = data.ping_at
    applyLiveLocation(data.lat, data.lng)
  })
  socket.on('driver_status_updated', (data) => {
    if (data?.driver !== route.params.driver) return
    if (driver.value) driver.value.is_online = data.is_online
  })
  socket.on('new_delivery_job', handleJobEvent)
  socket.on('delivery_job_unassigned', handleJobEvent)
  socket.on('delivery_job_status_updated', handleJobStatusEvent)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (tickTimer) {
    window.clearInterval(tickTimer)
    tickTimer = null
  }
  if (socket) {
    socket.disconnect()
    socket = null
  }
  if (map) {
    map.remove()
    map = null
  }
})
</script>
