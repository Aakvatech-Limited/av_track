<template>
  <div class="min-h-[100dvh] bg-slate-100 text-slate-900">
    <div class="h-[100dvh] w-full px-6 py-6 lg:px-12 lg:py-10">
      <div class="relative mx-0 h-full w-full max-w-none overflow-hidden rounded-[32px] bg-white shadow-[0_24px_60px_rgba(15,23,42,0.16)] lg:w-[420px]">
        <div class="absolute inset-0 bg-[url('https://lh3.googleusercontent.com/aida-public/AB6AXuCwFoQ7JdpWvqnf2-O2IXPqDedCmkaGS2d1n7D2f6w4agoek55TkZBXL8BN6CZNwCnql7S8qNQ0lLNtswDYxHO7rZFZRdEnJZIpDM_8wMK8OcfdZQ0bZdQiy_E-Ek5MthV7wfKATQmOF9WlAEvYDMo3RT_99EmxACQi7i11DqX7M2pwZME0jNtaeOq4KDJoNYtW6dpd-zTAf54nh-ElIw1J-u8c9aoz-KokilEI9TM9GTQAbVuXIWvkH8WmRZdZUnj-EG60MYFf0hE1')] bg-cover bg-center"></div>
        <div class="absolute inset-0 bg-black/10"></div>

        <div class="relative z-10 p-4 pt-10">
          <div class="rounded-2xl border border-white/15 bg-blue-600/95 p-4 text-white shadow-xl backdrop-blur">
            <div class="flex items-center gap-4">
              <div class="flex flex-col items-center">
                <svg class="h-9 w-9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 20l8-8-8-8" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M18 12H6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span class="mt-1 text-[10px] font-bold">400 ft</span>
              </div>
              <div class="flex flex-col border-l border-white/25 pl-4">
                <p class="text-xs font-medium text-blue-100">Turn right onto</p>
                <h2 class="text-lg font-bold leading-tight">Marketplace Blvd</h2>
              </div>
            </div>
          </div>
        </div>

        <div class="absolute right-4 top-1/2 z-10 flex -translate-y-1/2 flex-col gap-3">
          <button class="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-slate-900 shadow-lg backdrop-blur">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9" />
              <circle cx="12" cy="12" r="2" />
              <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke-linecap="round" />
            </svg>
          </button>
          <button class="flex h-12 w-12 items-center justify-center rounded-full bg-white/90 text-slate-900 shadow-lg backdrop-blur">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="absolute bottom-0 left-0 right-0 z-20 px-4 pb-8">
          <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-2xl">
            <div class="mb-6 flex items-start justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-red-500"></span>
                  <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Arriving In</p>
                </div>
                <div class="mt-1 flex items-baseline gap-2">
                  <h3 class="text-3xl font-bold text-slate-900">8</h3>
                  <span class="text-lg font-bold text-slate-900">min</span>
                  <span class="text-sm font-medium text-slate-400">(1.2 miles)</span>
                </div>
              </div>
              <div class="rounded-xl bg-slate-100 p-2">
                <svg class="h-7 w-7 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>

            <div class="mb-8 space-y-4">
              <div class="flex items-start gap-4">
                <svg class="mt-1 h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 21s7-4.4 7-11a7 7 0 1 0-14 0c0 6.6 7 11 7 11z" stroke-linecap="round" stroke-linejoin="round" />
                  <circle cx="12" cy="10" r="2.5" />
                </svg>
                <div>
                  <p class="text-lg font-bold text-slate-900">123 Delivery Ln, Apt 4B</p>
                  <p class="text-sm text-slate-500">Westside Neighborhood</p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <svg class="h-5 w-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                </svg>
                <p class="text-base font-semibold text-slate-700">John Doe</p>
              </div>
            </div>

            <div class="flex gap-3">
              <router-link
                to="/driver/dashboard"
                class="flex flex-1 items-center justify-center rounded-2xl bg-red-50 py-4 text-sm font-bold text-red-600 transition active:scale-95"
              >
                <svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                Exit
              </router-link>
              <router-link
                to="/driver/complete"
                class="flex flex-1 items-center justify-center rounded-2xl bg-blue-600 py-4 text-sm font-bold text-white shadow-lg shadow-blue-600/30 transition active:scale-95"
              >
                <svg class="mr-2 h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                Arrived
              </router-link>
              <button class="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-700 transition active:scale-95">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div class="pointer-events-none absolute bottom-3 left-1/2 z-30 h-1 w-32 -translate-x-1/2 rounded-full bg-slate-300"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DriverNavigate',
}
</script>
