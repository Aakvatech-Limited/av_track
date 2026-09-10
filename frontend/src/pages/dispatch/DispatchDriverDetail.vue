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
              <p class="mt-1 break-words text-sm font-bold text-slate-900">{{ job.dropoff_address || 'Dropoff address not set' }}</p>
              <p class="mt-0.5 text-xs text-slate-500">{{ job.customer_name || 'Unknown customer' }}</p>
            </div>
            <span class="flex-shrink-0 whitespace-nowrap rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-blue-600">
              {{ job.status }}
            </span>
          </div>
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

let map = null
let marker = null
let L = null

const renderMap = () => {
  if (!map || !L || !driver.value) return
  if (driver.value.last_lat == null || driver.value.last_lng == null) return

  const position = [Number(driver.value.last_lat), Number(driver.value.last_lng)]
  map.setView(position, 15)

  if (marker) {
    marker.setLatLng(position)
  } else {
    marker = L.marker(position).addTo(map)
  }
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
