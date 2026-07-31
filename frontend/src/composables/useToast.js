import { ref } from 'vue'

const toasts = ref([])

export function useToast() {
  function showToast(message, type = 'success', duration = 4500) {
    const id = Date.now() + Math.random()
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }

  function removeToast(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      toasts.value.splice(idx, 1)
    }
  }

  return {
    toasts,
    showToast,
    removeToast
  }
}
