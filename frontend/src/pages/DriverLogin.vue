<template>
  <BaseShell>
      <div class="min-h-[100dvh] bg-white">
        <div class="flex items-center gap-3">
          <router-link
            to="/"
            class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-700 hover:bg-slate-50"
            aria-label="Back"
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
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </router-link>
          <h1 class="text-lg font-semibold text-slate-900">Login</h1>
        </div>

        <div class="mt-8">
          <h2 class="text-2xl font-semibold text-slate-900">Welcome Back</h2>
          <p class="mt-2 text-sm text-slate-600">
            Enter your details to track your delivery
          </p>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="goToDashboard">
          <label class="block text-sm font-semibold text-slate-900">
            Email
            <input
              type="email"
              placeholder="yourname@example.com"
              class="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>

          <label class="block text-sm font-semibold text-slate-900">
            Password
            <div class="relative mt-2">
              <input
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                class="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 pr-12 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
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

          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2 text-slate-600">
              <input type="checkbox" class="h-4 w-4 rounded border-slate-300" />
              Keep me logged in
            </label>
            <button
              type="button"
              class="font-semibold text-blue-600 transition hover:text-blue-700"
            >
              Forgot Password?
            </button>
          </div>

          <button
            type="submit"
            class="mt-2 w-full rounded-2xl bg-blue-600 py-4 text-center text-base font-semibold text-white shadow-[0_14px_28px_rgba(37,99,235,0.35)] transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200"
          >
            Log In
          </button>
        </form>

        <div class="mt-6"></div>
      </div>
  </BaseShell>
</template>

<script>
import BaseShell from '@/components/BaseShell.vue'

export default {
  name: 'DriverLogin',
  components: {
    BaseShell,
  },
  data() {
    return {
      showPassword: false,
    }
  },
  methods: {
    goToDashboard() {
      this.$router.push('/driver/dashboard')
    },
  },
}
</script>
