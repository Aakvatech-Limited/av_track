import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.mount('#app')

const registerServiceWorker = () => {
  if (!('serviceWorker' in navigator)) return
  const swUrl = import.meta.env.DEV
    ? '/sw.js'
    : '/assets/av_track/frontend/sw.js'
  navigator.serviceWorker.register(swUrl, { type: 'classic' }).catch((err) => {
    console.error('Failed to register service worker', err)
  })
}

registerServiceWorker()
