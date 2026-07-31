import { onMounted, onUnmounted } from 'vue'

export function useRealtimeTickets(fetchFn, intervalMs = 10000) {
  let timer = null

  onMounted(() => {
    if (typeof fetchFn === 'function') {
      // Initial fetch
      fetchFn()

      // Polling interval
      timer = setInterval(() => {
        fetchFn()
      }, intervalMs)
    }
  })

  onUnmounted(() => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  })

  return {
    refreshNow: fetchFn
  }
}
