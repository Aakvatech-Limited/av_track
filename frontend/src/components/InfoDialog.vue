<template>
  <transition name="fade">
    <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center px-6">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"></div>
      <div class="relative w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
        <div class="flex items-start gap-3">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-full"
            :class="iconWrapClass"
          >
            <svg v-if="variant === 'error'" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 8v4" stroke-linecap="round" />
              <path d="M12 16h.01" stroke-linecap="round" />
              <path d="M10.29 3.86l-6.5 11.25a2 2 0 001.73 3h13a2 2 0 001.73-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            <svg v-else-if="variant === 'warning'" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 8v4" stroke-linecap="round" />
              <path d="M12 16h.01" stroke-linecap="round" />
              <path d="M10.29 3.86l-6.5 11.25a2 2 0 001.73 3h13a2 2 0 001.73-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 8h.01" stroke-linecap="round" />
              <path d="M11 12h1v4h1" stroke-linecap="round" />
              <circle cx="12" cy="12" r="9" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-base font-semibold text-slate-900">{{ title }}</h3>
            <p class="mt-1 text-sm text-slate-600">{{ message }}</p>
          </div>
        </div>
        <div class="mt-5 flex justify-end">
          <button
            type="button"
            class="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200"
            @click="$emit('update:modelValue', false)"
          >
            Okay
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'InfoDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: 'Notice',
    },
    message: {
      type: String,
      default: '',
    },
    variant: {
      type: String,
      default: 'info',
    },
  },
  computed: {
    iconWrapClass() {
      if (this.variant === 'error') {
        return 'bg-red-50 text-red-600'
      }
      if (this.variant === 'warning') {
        return 'bg-amber-50 text-amber-600'
      }
      return 'bg-blue-50 text-blue-600'
    },
  },
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
