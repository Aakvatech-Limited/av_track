<template>
  <div class="h-[100dvh] overflow-hidden bg-slate-100 text-[#111418]">
    <div class="h-[100dvh] w-full px-6 py-6 lg:px-12 lg:py-10">
      <div class="relative mx-0 flex h-full w-full max-w-none flex-col overflow-hidden rounded-[28px] bg-white shadow-[0_24px_60px_rgba(15,23,42,0.16)] lg:w-[430px]">
        <div class="sticky top-0 z-10 flex items-center justify-between border-b border-[#dbe0e6] bg-white px-4 py-4">
          <router-link
            to="/driver/navigate"
            class="flex h-10 w-10 items-center justify-center text-[#111418] hover:bg-slate-100"
            aria-label="Back"
          >
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 18l-6-6 6-6" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </router-link>
          <h2 class="flex-1 pr-10 text-center text-lg font-bold leading-tight tracking-[-0.015em] text-[#111418]">
            Complete Delivery
          </h2>
        </div>

        <div class="flex-1 overflow-y-auto scrollbar-hide">
          <div class="px-4 pt-6 pb-2">
            <p class="text-xs font-bold uppercase tracking-wider text-blue-600">Order #4492-BX</p>
            <h1 class="text-2xl font-extrabold leading-tight text-[#111418]">Drop-off: Sarah Jenkins</h1>
          </div>

          <div class="px-4">
            <h3 class="flex items-center gap-2 pt-6 pb-3 text-lg font-bold leading-tight tracking-[-0.015em] text-[#111418]">
              <svg class="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 7h4l2-2h6l2 2h4v12H3z" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="12" cy="13" r="3" />
              </svg>
              Package Photo
            </h3>
            <div class="relative flex aspect-[4/3] w-full flex-col items-center justify-center overflow-hidden rounded-xl border-2 border-dashed border-[#dbe0e6] bg-gray-100">
              <div class="flex flex-col items-center text-gray-400">
                <svg class="mb-2 h-12 w-12" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M4 6.5A2.5 2.5 0 0 1 6.5 4h2.1l1.2 1.6c.3.4.8.6 1.2.6h2.9c.5 0 .9-.2 1.2-.6l1.2-1.6h1.7A2.5 2.5 0 0 1 20 6.5v10A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5v-10Z"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linejoin="round"
                  />
                  <circle cx="12" cy="12" r="3.25" stroke="currentColor" stroke-width="1.5" />
                  <circle cx="8.2" cy="9" r="0.9" fill="currentColor" />
                </svg>
                <p class="text-sm font-medium">Place package in frame</p>
              </div>
            </div>
            <div class="flex items-center justify-center gap-6 py-6">
              <button class="flex h-12 w-12 items-center justify-center rounded-full border border-gray-100 bg-white text-[#111418] shadow-lg">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="5" width="18" height="14" rx="2.5" stroke="currentColor" stroke-width="2" />
                  <circle cx="9" cy="10" r="2" stroke="currentColor" stroke-width="2" />
                  <path d="M4 17l5-5 4 4 3-3 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
              <button class="flex h-20 w-20 items-center justify-center rounded-full bg-blue-600 text-white shadow-xl">
                <svg class="h-10 w-10" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="7" width="18" height="12" rx="2.5" fill="currentColor" />
                  <path d="M8 7l2-2h4l2 2" fill="currentColor" />
                  <circle cx="12" cy="13" r="3" fill="white" />
                </svg>
              </button>
              <button class="flex h-12 w-12 items-center justify-center rounded-full border border-gray-100 bg-white text-[#111418] shadow-lg">
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M13 2L7 13h5l-1 9 6-11h-5l1-9Z"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div class="px-4">
            <h3 class="flex items-center gap-2 pt-2 pb-3 text-lg font-bold leading-tight tracking-[-0.015em] text-[#111418]">
              <svg class="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9" stroke-linecap="round" />
                <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              Customer Signature
            </h3>
            <div class="rounded-2xl border border-[#e3e8ef] bg-white p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-semibold text-[#111418]">Sign here</p>
                  <p class="text-xs text-[#64748b]">Please have the customer sign within the box</p>
                </div>
                <button
                  type="button"
                  class="rounded-full bg-[#f0f2f4] px-3 py-1 text-xs font-semibold text-slate-600"
                  @click="clearSignature"
                >
                  Clear Signature
                </button>
              </div>
              <div class="mt-4">
                <div class="relative h-40 w-full overflow-hidden rounded-xl border-2 border-dashed border-[#dbe0e6] bg-[#f8fafc]">
                  <canvas
                    ref="signatureCanvas"
                    class="h-full w-full"
                    aria-label="Signature canvas"
                  ></canvas>
                  <div
                    v-if="!hasSignature"
                    class="pointer-events-none absolute inset-0 flex items-center justify-center text-slate-400"
                  >
                    <div class="flex flex-col items-center gap-1 text-sm">
                      <span class="font-medium">Tap and draw to sign</span>
                      <span class="text-xs">Use finger or stylus</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="px-4 pb-32">
            <h3 class="flex items-center gap-2 pt-6 pb-3 text-lg font-bold leading-tight tracking-[-0.015em] text-[#111418]">
              <svg class="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 6h16M4 12h16M4 18h10" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              Delivery Notes
            </h3>
            <textarea
              rows="3"
              class="w-full rounded-xl border-2 border-[#dbe0e6] bg-white p-4 text-sm text-[#111418] focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder="Add details about the drop-off location (e.g., behind the gate, with neighbor...)"
            ></textarea>
          </div>
        </div>

        <div class="shrink-0 border-t border-[#dbe0e6] bg-white/80 px-4 py-4 backdrop-blur-md">
          <router-link
            to="/driver/dashboard"
            class="flex h-14 w-full items-center justify-center rounded-xl bg-blue-600 text-base font-bold text-white shadow-lg transition active:scale-[0.98]"
          >
            Complete Delivery
          </router-link>
        </div>
        <div class="h-6 bg-white"></div>
      </div>
    </div>
  </div>
</template>

<script>
import SignaturePad from 'signature_pad'

export default {
  name: 'DriverDeliveryComplete',
  data() {
    return {
      hasSignature: false,
      signaturePad: null,
    }
  },
  mounted() {
    this.setupSignatureCanvas()
    window.addEventListener('resize', this.resizeSignatureCanvas)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeSignatureCanvas)
    this.destroySignaturePad()
  },
  methods: {
    setupSignatureCanvas() {
      const canvas = this.$refs.signatureCanvas
      if (!canvas) return
      this.resizeSignatureCanvas()
      this.signaturePad = new SignaturePad(canvas, {
        minWidth: 1.6,
        maxWidth: 2.4,
        penColor: '#0f172a',
        backgroundColor: 'rgba(0,0,0,0)',
      })
      this.signaturePad.onBegin = () => {
        this.hasSignature = true
      }
      this.signaturePad.onEnd = () => {
        this.hasSignature = !this.signaturePad.isEmpty()
      }
      canvas.addEventListener('pointerdown', this.handleSignatureStart)
      canvas.addEventListener('touchstart', this.handleSignatureStart, { passive: true })
    },
    resizeSignatureCanvas() {
      const canvas = this.$refs.signatureCanvas
      if (!canvas) return
      const rect = canvas.getBoundingClientRect()
      const ratio = window.devicePixelRatio || 1
      const wasEmpty = this.signaturePad ? this.signaturePad.isEmpty() : true
      canvas.width = rect.width * ratio
      canvas.height = rect.height * ratio
      canvas.style.width = `${rect.width}px`
      canvas.style.height = `${rect.height}px`
      if (this.signaturePad) {
        this.signaturePad.clear()
        this.signaturePad._resizeCanvas()
        if (!wasEmpty) {
          this.hasSignature = false
        }
      }
    },
    clearSignature() {
      if (this.signaturePad) {
        this.signaturePad.clear()
      }
      this.hasSignature = false
    },
    handleSignatureStart() {
      this.hasSignature = true
    },
    destroySignaturePad() {
      if (this.signaturePad) {
        this.signaturePad.off()
        this.signaturePad = null
      }
    },
  },
}
</script>

<style scoped>
.scrollbar-hide {
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  width: 0;
  height: 0;
}
</style>
