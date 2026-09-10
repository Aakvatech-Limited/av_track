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
        <p class="text-xs font-semibold" :class="driver?.is_online ? 'text-emerald-600' : 'text-slate-400'">
          {{ driver?.is_online ? 'Online' : 'Offline' }}
          <span v-if="driver?.last_ping_at" class="text-slate-400 font-normal">&middot; last seen {{ lastSeenLabel }}</span>
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
import InfoDialog from '@/components/InfoDialog.vue'

const route = useRoute()
const mapContainer = ref(null)
const isLoading = ref(true)
const driver = ref(null)
const jobs = ref([])

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

const lastSeenLabel = computed(() => {
  if (!driver.value?.last_ping_at) return ''
  try {
    return new Date(driver.value.last_ping_at.replace(' ', 'T')).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch (error) {
    return driver.value.last_ping_at
  }
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

const renderMap = () => {
  if (!map || !L || !driver.value) return
  if (driver.value.last_lat == null || driver.value.last_lng == null) return

  const position = [Number(driver.value.last_lat), Number(driver.value.last_lng)]
  map.invalidateSize()
  map.setView(position, 15)

  if (marker) {
    marker.setLatLng(position)
  } else {
    const icon = L.divIcon({
      className: '',
      html: `
        <div style="
          width:36px;height:36px;border-radius:50%;
          background:#2563eb;
          border:3px solid white;
          box-shadow:0 2px 6px rgba(0,0,0,0.4);
          display:flex; align-items:center; justify-content:center;
          color:white; font-weight:700; font-size:13px; font-family:inherit;
        ">${initials.value}</div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    })
    marker = L.marker(position, { icon }).addTo(map)
  }

  // The container's final size can settle a beat after layout/paint
  // (route transition, PWA chrome), so re-check once more or the tile
  // grid stays sized to whatever it was at construction time.
  setTimeout(() => {
    map?.invalidateSize()
  }, 150)
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

  try {
    const data = await getDriverRouteDetail(route.params.driver)
    driver.value = data
    jobs.value = data?.jobs || []
    renderMap()
  } catch (error) {
    showDialog('Could Not Load Driver', error.message || 'Unknown error', 'error')
  } finally {
    isLoading.value = false
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>
