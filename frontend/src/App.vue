<template>
  <div>
    <InstallPrompt />
    <router-view />
    
    <!-- Global Notification Toast -->
    <transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="notification" class="fixed top-4 right-4 left-4 sm:left-auto z-50 overflow-hidden rounded-lg bg-white shadow-xl ring-1 ring-black ring-opacity-5">
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p class="text-sm font-bold text-slate-900">{{ notification.title }}</p>
              <p class="mt-1 text-sm font-medium text-slate-600">{{ notification.message }}</p>
            </div>
            <div class="ml-4 flex flex-shrink-0">
              <button @click="notification = null" type="button" class="inline-flex rounded-md bg-white text-slate-400 hover:text-slate-500 focus:outline-none">
                <span class="sr-only">Close</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import InstallPrompt from "./components/InstallPrompt.vue"
import { io } from 'socket.io-client'

const notification = ref(null)
let socket = null
let timeoutId = null

const showNotification = (title, message) => {
  notification.value = { title, message }
  
  // Play alert sound (built into Frappe)
  try {
    const audio = new Audio('/assets/frappe/sounds/alert.mp3')
    audio.play().catch(e => console.warn('Audio play failed:', e))
  } catch(e) {}
  
  if (timeoutId) clearTimeout(timeoutId)
  timeoutId = setTimeout(() => {
    notification.value = null
  }, 6000)
}

onMounted(() => {
  const host = window.location.hostname
  const port = window.location.port ? ':9000' : ''
  const protocol = window.location.port ? 'http' : 'https'
  
  const url = `${protocol}://${host}${port}/${host}`
  
  socket = io(url, { 
    withCredentials: true,
    reconnectionAttempts: 5
  })
  
  socket.on('new_delivery_job', (data) => {
    showNotification(data.title || 'New Job', `Job ${data.job} has been assigned to you.`)
  })
  
  socket.on('job_cancelled', (data) => {
    showNotification(data.title || 'Job Cancelled', `Job ${data.job} was cancelled.`)
  })
})

onUnmounted(() => {
  if (socket) {
    socket.disconnect()
  }
})
</script>
