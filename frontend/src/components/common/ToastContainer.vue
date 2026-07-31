<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, removeToast } = useToast()

function iconClass(type) {
  switch (type) {
    case 'success': return 'bi-check-circle-fill text-success'
    case 'error': return 'bi-exclamation-octagon-fill text-danger'
    case 'warning': return 'bi-exclamation-triangle-fill text-warning'
    default: return 'bi-info-circle-fill text-primary'
  }
}

function cardBorderClass(type) {
  switch (type) {
    case 'success': return 'toast-card-success'
    case 'error': return 'toast-card-error'
    case 'warning': return 'toast-card-warning'
    default: return 'toast-card-info'
  }
}
</script>

<template>
  <div class="toast-container-fixed">
    <TransitionGroup name="toast-slide">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="toast-card-glass shadow-lg"
        :class="cardBorderClass(toast.type)"
      >
        <div class="d-flex align-items-center gap-3">
          <i class="bi text-lg" :class="iconClass(toast.type)"></i>
          <span class="toast-message-text">{{ toast.message }}</span>
        </div>

        <button type="button" class="btn-close-toast" @click="removeToast(toast.id)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container-fixed {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
}

.toast-card-glass {
  pointer-events: auto;
  min-width: 320px;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 14px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 6px solid #2563eb;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.14);
}

.toast-card-success { border-left-color: #10b981; }
.toast-card-error { border-left-color: #ef4444; }
.toast-card-warning { border-left-color: #f59e0b; }
.toast-card-info { border-left-color: #3b82f6; }

.toast-message-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.btn-close-toast {
  background: transparent;
  border: none;
  font-size: 1.3rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0 4px;
  display: flex;
  align-items: center;
}

.btn-close-toast:hover {
  color: #0f172a;
}

/* Toast Slide Animation */
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(60px) scale(0.92);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.88);
}
</style>
