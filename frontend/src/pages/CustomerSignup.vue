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
          <h1 class="text-lg font-semibold text-slate-900">Create Account</h1>
        </div>

        <div class="mt-6 border-b border-slate-200 pb-6">
          <h2 class="text-3xl font-semibold text-slate-900">
            Join our delivery network
          </h2>
          <p class="mt-3 text-sm text-slate-600">
            Enter your details to get started with fast, reliable deliveries.
          </p>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent>
          <label class="block text-sm font-semibold text-slate-900">
            Full Name
            <div class="relative mt-2">
              <input
                type="text"
                placeholder="John Doe"
                class="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 pr-12 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
              <span class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                👤
              </span>
            </div>
          </label>

          <label class="block text-sm font-semibold text-slate-900">
            Email
            <div class="relative mt-2">
              <input
                type="email"
                placeholder="name@example.com"
                class="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 pr-12 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
              <span class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                ✉️
              </span>
            </div>
          </label>

          <label class="block text-sm font-semibold text-slate-900">
            Phone Number
            <div class="relative mt-2">
              <input
                type="tel"
                placeholder="+1 (555) 000-0000"
                class="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 pr-12 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />
              <span class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400">
                📱
              </span>
            </div>
          </label>

          <label class="block text-sm font-semibold text-slate-900">
            Create Password
            <div class="relative mt-2">
              <input
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
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

          <label class="flex items-start gap-3 text-sm text-slate-600">
            <input type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300" />
            <span>
              I agree to the
              <span class="font-semibold text-blue-600">Terms and Conditions</span>
              and Privacy Policy.
            </span>
          </label>

          <label class="flex items-start gap-3 text-sm text-slate-600">
            <input type="checkbox" class="mt-1 h-4 w-4 rounded border-slate-300" />
            <span>
              Receive order updates via WhatsApp
              <span class="text-green-500">💬</span>
            </span>
          </label>

          <button
            type="submit"
            class="mt-2 w-full rounded-2xl bg-blue-600 py-4 text-center text-base font-semibold text-white shadow-[0_14px_28px_rgba(37,99,235,0.35)] transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200"
          >
            Sign Up
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-slate-600">
          Already have an account?
          <router-link to="/driver-login" class="font-semibold text-blue-600">
            Log In
          </router-link>
        </p>
      </div>
  </BaseShell>
</template>

<script>
import BaseShell from '@/components/BaseShell.vue'

export default {
  name: 'CustomerSignup',
  components: {
    BaseShell,
  },
  data() {
    return {
      showPassword: false,
    }
  },
}
</script>
