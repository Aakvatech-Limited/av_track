<template>
  <div class="min-h-[100dvh] bg-white lg:flex lg:items-stretch">
    <div class="min-h-[100dvh] w-full px-0 py-0 lg:px-12 lg:py-12">
      <div
        class="w-full min-h-[100dvh] bg-white px-6 py-10 sm:px-8 sm:py-12 lg:min-h-0 lg:w-[400px] lg:px-6 lg:py-12"
      >
      <div class="flex flex-col items-center text-center">
        <div class="flex h-20 w-20 items-center justify-center rounded-2xl bg-blue-100">
          <img
            src="@/assets/avtrack-logo.png"
            alt="AVTrack"
            class="h-12 w-12 object-contain"
          />
        </div>
        <h1 class="mt-6 text-2xl font-semibold text-slate-900">
          AV Track
        </h1>
        <p class="mt-2 text-sm text-slate-500">
          Dispatch • Track • Deliver
        </p>
      </div>

      <form class="mt-8 space-y-5" @submit.prevent>
        <label class="block text-sm font-semibold text-slate-900">
          Email or Phone Number
          <input
            type="text"
            placeholder="Enter your credentials"
            class="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-4 focus:ring-blue-100"
          />
        </label>

        <label class="block text-sm font-semibold text-slate-900">
          Password
          <div class="relative mt-2">
            <input
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
              class="w-full rounded-xl border border-slate-200 px-4 py-3 pr-12 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-4 focus:ring-blue-100"
            />
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-slate-400 transition hover:text-slate-600"
              @click="showPassword = !showPassword"
              aria-label="Toggle password visibility"
            >
              <svg
                viewBox="0 0 24 24"
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M1.5 12s4-7 10.5-7 10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </button>
          </div>
        </label>

        <div class="flex justify-end">
          <button
            type="button"
            class="text-sm font-semibold text-blue-600 transition hover:text-blue-700"
          >
            Forgot Password?
          </button>
        </div>

        <button
          type="submit"
          class="mt-2 w-full rounded-2xl bg-blue-600 py-3.5 text-center text-base font-semibold text-white shadow-[0_12px_24px_rgba(37,99,235,0.35)] transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200"
        >
          Log In
        </button>
      </form>

      <div class="my-8 h-px w-full bg-slate-200" />

      <div class="text-center text-sm text-slate-500">
        <p class="font-semibold text-slate-900">
          Don&apos;t have an account??
        </p>
        <div class="mt-3 space-y-2">
          <button
            type="button"
            class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 hover:shadow-md"
          >
            Create an account as Customer
          </button>
          <button
            type="button"
            class="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 hover:shadow-md"
          >
            Login as Driver
          </button>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      showPassword: false,
    }
  },
}
</script>
