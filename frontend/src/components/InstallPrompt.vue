<template>
  <Dialog v-model="showDialog">
    <template #body-title>
      <h2 class="text-lg font-bold">Install AVTrack</h2>
    </template>
    <template #body-content>
      <p>Get the app on your device for easy access &amp; a better experience!</p>
    </template>
    <template #actions>
      <Button variant="solid" @click="install" class="w-full py-5">
        <template #prefix>
          <FeatherIcon name="download" class="h-4 w-4" />
        </template>
        Install
      </Button>
    </template>
  </Dialog>

  <Popover :show="iosInstallMessage" placement="bottom">
    <template #body>
      <div
        class="mx-2 mt-[calc(100vh-15rem)] flex flex-col gap-3 rounded bg-blue-100 py-5 drop-shadow-xl"
      >
        <div class="flex items-center justify-between px-3 text-center">
          <span class="text-base font-bold text-gray-900">
            Install AVTrack
          </span>
          <span class="inline-flex items-baseline">
            <FeatherIcon
              name="x"
              class="ml-auto h-4 w-4 text-gray-700"
              @click="iosInstallMessage = false"
            />
          </span>
        </div>
        <div class="px-3 text-xs text-gray-800">
          <span class="flex flex-col gap-2">
            <span>
              Get the app on your iPhone for easy access &amp; a better experience
            </span>
            <span class="inline-flex items-start whitespace-nowrap">
              <span>Tap&nbsp;</span>
              <FeatherIcon name="share" class="h-4 w-4 text-blue-600" />
              <span>&nbsp;and then "Add to Home Screen"</span>
            </span>
          </span>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import { ref } from "vue"
import { Dialog, Popover, FeatherIcon, Button } from "frappe-ui"

const deferredPrompt = ref(null)
const showDialog = ref(false)
const iosInstallMessage = ref(false)

const isIos = () => {
  const userAgent = window.navigator.userAgent.toLowerCase()
  return /iphone|ipad|ipod/.test(userAgent)
}

const isInStandaloneMode = () =>
  "standalone" in window.navigator && window.navigator.standalone

if (isIos() && !isInStandaloneMode()) {
  iosInstallMessage.value = true
}

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault()
  deferredPrompt.value = e
  if (isIos() && !isInStandaloneMode()) {
    iosInstallMessage.value = true
  } else {
    showDialog.value = true
  }
})

window.addEventListener("appinstalled", () => {
  showDialog.value = false
  deferredPrompt.value = null
})

async function install() {
  if (!deferredPrompt.value) return
  deferredPrompt.value.prompt()
  showDialog.value = false
}
</script>
