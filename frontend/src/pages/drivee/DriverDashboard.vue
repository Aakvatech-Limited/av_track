<template>
  <div class="min-h-[100dvh] bg-white text-slate-900">
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
          <button class="relative flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8a6 6 0 10-12 0c0 7-3 7-3 7h18s-3 0-3-7" />
              <path d="M13.73 21a2 2 0 01-3.46 0" />
            </svg>
            <span class="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500"></span>
          </button>
        </div>

        <!-- Active Status -->
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-5 mb-6">
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
        <div v-if="currentTask" class="rounded-xl overflow-hidden shadow-lg bg-white border border-slate-200">
          <div class="relative h-44 bg-gradient-to-br from-slate-200 to-slate-300">
            <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
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
            <div class="flex items-center gap-2 py-2 border-t border-slate-200">
              <svg class="h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
              <p class="text-slate-600 text-sm font-medium">
                Customer: {{ currentTask.customer_name || '—' }}
              </p>
            </div>
            <div class="flex gap-2 mt-3">
              <button class="flex-1 flex items-center justify-center rounded-lg h-12 px-4 bg-blue-500 text-white text-base font-bold">
                <svg class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                </svg>
                Navigate
              </button>
              <button class="flex size-12 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500">
          No active task right now.
        </div>

        <!-- Upcoming Stops -->
        <h2 class="text-xl font-bold mt-6 mb-3">Upcoming Stops</h2>
        <div class="space-y-3 pb-8">
          <div v-for="stop in upcomingStops" :key="stop.id" class="flex items-center gap-4 p-3 rounded-lg bg-white border border-slate-200">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-slate-500 font-bold">
              {{ stop.id }}
            </div>
            <div class="flex-1">
              <p class="text-sm font-bold">{{ stop.address }}</p>
              <p class="text-slate-500 text-xs">{{ stop.distance }} miles • {{ stop.type }}</p>
            </div>
            <svg class="h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </div>
        </div>

        <!-- Bottom Nav -->
        <DriverBottomNav />
        <div class="fixed bottom-1 left-1/2 -translate-x-1/2 w-32 h-1 bg-slate-200 rounded-full"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DriverBottomNav from '@/components/DriverBottomNav.vue'

const isActive = ref(false)
const driverName = ref('')
const driverId = ref('')
const driverInitials = ref('')
const completedDeliveries = ref(0)
const dailyGoal = ref(0)

const progressPercentage = computed(() => {
  if (!dailyGoal.value) return 0
  return Math.round((completedDeliveries.value / dailyGoal.value) * 100)
})

const remainingDeliveries = computed(() => {
  return Math.max(dailyGoal.value - completedDeliveries.value, 0)
})

const upcomingStops = ref([
  {
    id: 2,
    address: 'Marketplace Blvd, 402',
    distance: '2.4',
    type: 'Next in queue',
  },
  {
    id: 3,
    address: 'Industrial Way, 12',
    distance: '4.1',
    type: 'Standard Delivery',
  },
  {
    id: 4,
    address: 'Harbor Dr, 99',
    distance: '5.8',
    type: 'Standard Delivery',
  },
])

const currentTask = ref(null)

const getInitials = (name) => {
  if (!name) return ''
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] || ''
  const second = parts[1]?.[0] || ''
  return (first + second).toUpperCase()
}

const loadDriverProfile = async () => {
  try {
    const { getDriverProfile } = await import('@/utils/auth')
    const profile = await getDriverProfile()
    if (!profile) return
    driverName.value = profile.full_name || ''
    driverId.value = profile.driver_id || ''
    driverInitials.value = getInitials(driverName.value)
    isActive.value = Boolean(profile.is_online || profile.is_active)
  } catch (error) {
    // keep empty values if profile not available
  }
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

loadDriverProfile()

const loadDriverProgress = async () => {
  try {
    const { getDriverProgress } = await import('@/utils/auth')
    const progress = await getDriverProgress()
    if (!progress) return
    completedDeliveries.value = progress.delivered_total || 0
    dailyGoal.value = progress.goal || progress.assigned_total || 0
  } catch (error) {
    // keep defaults
  }
}

loadDriverProgress()

const loadCurrentTask = async () => {
  try {
    const { getCurrentTask } = await import('@/utils/auth')
    const task = await getCurrentTask()
    currentTask.value = task || null
  } catch (error) {
    currentTask.value = null
  }
}

loadCurrentTask()
</script>
