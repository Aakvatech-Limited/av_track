<template>
  <div class="min-h-[100dvh] bg-white text-slate-900">
    <div class="min-h-[100dvh] w-full px-6 py-8 lg:px-12 lg:py-12">
      <div class="mx-0 w-full max-w-none pb-24 lg:w-[420px]">
        <div class="mt-6 flex flex-col items-center text-center">
          <div class="relative">
            <div class="h-28 w-28 overflow-hidden rounded-full border-4 border-white shadow">
              <img
                src="https://i.pravatar.cc/200?img=12"
                alt="Driver profile"
                class="h-full w-full object-cover"
              />
            </div>
            <span class="absolute bottom-2 right-2 flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 text-white">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="3">
                <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </span>
          </div>
          <h2 class="mt-4 text-2xl font-semibold">Alex Driver</h2>
          <p class="mt-2 text-sm text-slate-500">
            <span class="text-amber-500">★</span> 4.9 · Merchant ID: 5920
          </p>
        </div>

        <div class="mt-10 space-y-6">
          <div>
            <p class="text-xs font-semibold tracking-[0.2em] text-slate-400">GENERAL SETTINGS</p>
            <div class="mt-3 overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div class="flex items-center justify-between px-4 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                    <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M4 6h16" stroke-linecap="round" />
                      <path d="M7 6v12" stroke-linecap="round" />
                      <path d="M17 6v12" stroke-linecap="round" />
                      <path d="M4 18h16" stroke-linecap="round" />
                      <path d="M9 10h6" stroke-linecap="round" />
                      <path d="M9 14h6" stroke-linecap="round" />
                    </svg>
                  </span>
                  <span class="text-sm font-medium">App Language</span>
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-500">
                  English (US)
                  <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </div>
              </div>
              <div class="flex items-center justify-between border-t border-slate-200 px-4 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700">
                    <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                      <path d="M21.64 13.03A9 9 0 0 1 11 3a1 1 0 0 0-1-1 10 10 0 1 0 10 10 1 1 0 0 0-1.36-.97z" />
                    </svg>
                  </span>
                  <span class="text-sm font-medium">Dark Mode</span>
                </div>
                <label class="relative inline-flex items-center">
                  <input type="checkbox" class="peer sr-only" />
                  <span class="h-6 w-11 rounded-full bg-slate-300 peer-checked:bg-blue-600"></span>
                  <span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-white transition peer-checked:translate-x-5"></span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <p class="text-xs font-semibold tracking-[0.2em] text-slate-400">NOTIFICATIONS</p>
            <div class="mt-3 overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div class="flex items-center justify-between px-4 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-500">
                    <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M15 17h5l-1.4-1.4a2 2 0 0 1-.6-1.4V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5" stroke-linecap="round" stroke-linejoin="round" />
                      <path d="M9 17v1a3 3 0 0 0 6 0v-1" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                  </span>
                  <span class="text-sm font-medium">New Job Alerts</span>
                </div>
                <label class="relative inline-flex items-center">
                  <input type="checkbox" class="peer sr-only" checked />
                  <span class="h-6 w-11 rounded-full bg-slate-300 peer-checked:bg-blue-600"></span>
                  <span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-white transition peer-checked:translate-x-5"></span>
                </label>
              </div>
              <div class="flex items-center justify-between border-t border-slate-200 px-4 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                    <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                  </span>
                  <span class="text-sm font-medium">Chat Messages</span>
                </div>
                <label class="relative inline-flex items-center">
                  <input type="checkbox" class="peer sr-only" checked />
                  <span class="h-6 w-11 rounded-full bg-slate-300 peer-checked:bg-blue-600"></span>
                  <span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-white transition peer-checked:translate-x-5"></span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <p class="text-xs font-semibold tracking-[0.2em] text-slate-400">PRIVACY &amp; ACCESS</p>
            <div class="mt-3 overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div class="flex items-center justify-between px-4 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-500">
                    <svg viewBox="0 0 24 24" class="h-5 w-5" style="color: #22c55e" fill="currentColor">
                      <path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 12 7 12s7-6.75 7-12a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z" />
                    </svg>
                  </span>
                  <span class="text-sm font-medium">Location Permissions</span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <span class="text-emerald-500">Always</span>
                  <svg viewBox="0 0 24 24" class="h-4 w-4 text-slate-400" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </div>
              </div>
              <div class="flex items-center justify-between border-t border-slate-200 px-4 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-500">
                    <svg viewBox="0 0 24 24" class="h-5 w-5" style="color: #64748b" fill="currentColor">
                      <path d="M12 2a10 10 0 1 0 10 10A10.01 10.01 0 0 0 12 2zm0 15.2a1.2 1.2 0 1 1 1.2-1.2 1.2 1.2 0 0 1-1.2 1.2zm1.8-6a2 2 0 0 0-1.3 1.8v.3a1 1 0 0 1-2 0v-.5a4 4 0 1 1 6.7-3 3.7 3.7 0 0 1-1.4 2.9z" />
                    </svg>
                  </span>
                  <span class="text-sm font-medium">Help &amp; Support</span>
                </div>
                <svg viewBox="0 0 24 24" class="h-4 w-4 text-slate-400" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>
          </div>

          <button
            type="button"
            class="w-full rounded-2xl border border-red-200 bg-red-50 py-3 text-sm font-semibold text-red-500"
          >
            Sign Out
          </button>

          <div class="pt-4 text-center text-xs text-slate-400">
            Merchant App Version 2.4.1 (Build 890)
          </div>
        </div>
      </div>
    </div>
    <DriverBottomNav />
  </div>
</template>

<script>
import DriverBottomNav from '@/components/DriverBottomNav.vue'

export default {
  name: 'DriverAccount',
  components: {
    DriverBottomNav,
  },
}
</script>
