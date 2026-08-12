<script setup>
import { ref, watch, onMounted } from 'vue'
import { getEventAttendance, declareEventResults } from '@/api/events'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  show: Boolean,
  eventId: Number,
  prizes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'declared'])
const { showToast } = useToast()

const loading = ref(false)
const declaring = ref(false)
const finalists = ref([])
const winnerUserId = ref('')
const runnerUpUserId = ref('')
const secondRunnerUpUserId = ref('')

async function fetchFinalists() {
  if (!props.eventId) return
  loading.value = true
  try {
    const res = await getEventAttendance(props.eventId)
    if (res && res.success) {
      finalists.value = res.participants || []
    }
  } catch (err) {
    showToast('Failed to load final round participants.', 'error')
  } finally {
    loading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchFinalists()
  }
})

async function handleDeclare() {
  if (!props.eventId) return
  declaring.value = true
  try {
    const payload = {
      winnerUserId: winnerUserId.value ? Number(winnerUserId.value) : null,
      runnerUpUserId: runnerUpUserId.value ? Number(runnerUpUserId.value) : null,
      secondRunnerUpUserId: secondRunnerUpUserId.value ? Number(secondRunnerUpUserId.value) : null
    }
    const res = await declareEventResults(props.eventId, payload)
    showToast(res.message || 'Results declared successfully!', 'success')
    emit('declared', res)
    emit('close')
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to declare results.', 'error')
  } finally {
    declaring.value = false
  }
}

onMounted(() => {
  if (props.show) fetchFinalists()
})
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
    <div class="modal-card-custom bg-white p-4 rounded-4 shadow-lg" style="max-width: 520px; width: 90%;">
      
      <div class="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
        <div>
          <span class="badge bg-warning-subtle text-warning-emphasis rounded-pill text-xs fw-bold px-2 py-1 mb-1 d-inline-block">
            🏆 COMPETITION RESULTS
          </span>
          <h5 class="fw-bold text-dark mb-0">Declare Event Winners</h5>
        </div>
        <button class="btn-close" @click="$emit('close')"></button>
      </div>

      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted text-xs mt-2">Loading finalist candidates...</p>
      </div>

      <div v-else>
        <p class="text-secondary text-xs mb-3">
          Assign competition position winners from the final round participants. Positions are optional.
        </p>

        <!-- 1st Place / Winner -->
        <div class="mb-3 p-3 bg-light rounded-3 border border-warning-subtle">
          <label class="form-label text-xs fw-bold text-warning-emphasis text-uppercase d-flex align-items-center gap-1">
            <span>🏆 Winner (1st Place)</span>
          </label>
          <select v-model="winnerUserId" class="form-select rounded-3 text-sm">
            <option value="">Select Winner...</option>
            <option v-for="f in finalists" :key="f.userId" :value="f.userId">
              {{ f.userName }} ({{ f.registerNumber }}) — {{ f.userEmail }}
            </option>
          </select>
        </div>

        <!-- 2nd Place / Runner-up -->
        <div class="mb-3 p-3 bg-light rounded-3 border">
          <label class="form-label text-xs fw-bold text-secondary text-uppercase d-flex align-items-center gap-1">
            <span>🥈 Runner-up (2nd Place)</span>
          </label>
          <select v-model="runnerUpUserId" class="form-select rounded-3 text-sm">
            <option value="">Select Runner-up (Optional)...</option>
            <option v-for="f in finalists" :key="f.userId" :value="f.userId" :disabled="f.userId === Number(winnerUserId)">
              {{ f.userName }} ({{ f.registerNumber }})
            </option>
          </select>
        </div>

        <!-- 3rd Place / Second Runner-up -->
        <div class="mb-4 p-3 bg-light rounded-3 border">
          <label class="form-label text-xs fw-bold text-secondary text-uppercase d-flex align-items-center gap-1">
            <span>🥉 Second Runner-up (3rd Place)</span>
          </label>
          <select v-model="secondRunnerUpUserId" class="form-select rounded-3 text-sm">
            <option value="">Select Second Runner-up (Optional)...</option>
            <option v-for="f in finalists" :key="f.userId" :value="f.userId" :disabled="f.userId === Number(winnerUserId) || f.userId === Number(runnerUpUserId)">
              {{ f.userName }} ({{ f.registerNumber }})
            </option>
          </select>
        </div>

        <div class="d-flex justify-content-end gap-2 pt-2 border-top">
          <button class="btn btn-secondary rounded-pill px-4 text-xs" @click="$emit('close')">Cancel</button>
          <button 
            class="btn btn-warning rounded-pill px-4 text-xs fw-bold shadow-sm text-dark d-flex align-items-center gap-2" 
            :disabled="declaring"
            @click="handleDeclare"
          >
            <i v-if="declaring" class="spinner-border spinner-border-sm"></i>
            <i v-else class="bi bi-award-fill"></i>
            Save Results
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1060;
}
</style>
