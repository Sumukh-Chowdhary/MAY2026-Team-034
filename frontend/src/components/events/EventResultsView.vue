<script setup>
import { ref, computed } from 'vue'
import DeclareResultsModal from './DeclareResultsModal.vue'
import { announceEventWinners } from '@/api/events'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  eventId: {
    type: Number,
    required: true
  },
  prizes: {
    type: Array,
    default: () => []
  },
  canManage: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['refresh'])
const { showToast } = useToast()

const showDeclareModal = ref(false)
const showPublishConfirm = ref(false)
const publishing = ref(false)

const winner = computed(() => props.prizes.find(p => p.title?.toLowerCase().includes('winner') && !p.title?.toLowerCase().includes('second') && !p.title?.toLowerCase().includes('runner')))
const runnerUp = computed(() => props.prizes.find(p => p.title?.toLowerCase().includes('runner-up') && !p.title?.toLowerCase().includes('second')))
const secondRunnerUp = computed(() => props.prizes.find(p => p.title?.toLowerCase().includes('second runner-up')))

async function handlePublishWinners() {
  publishing.value = true
  try {
    const res = await announceEventWinners(props.eventId)
    showToast(res.message || 'Winners announced successfully!', 'success')
    showPublishConfirm.value = false
    emit('refresh')
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to announce winners.', 'error')
  } finally {
    publishing.value = false
  }
}
</script>

<template>
  <div class="event-results-view container py-3">
    
    <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mb-4">
      <div>
        <h4 class="fw-bold text-dark mb-1"><i class="bi bi-trophy-fill me-2 text-warning"></i> Competition Results & Podium</h4>
        <p class="text-secondary text-xs mb-0">Official competition leaderboard, winners, and prize distributions.</p>
      </div>

      <div v-if="canManage" class="d-flex align-items-center gap-2">
        <button class="btn btn-outline-warning rounded-pill px-3 text-xs fw-bold text-dark" @click="showDeclareModal = true">
          <i class="bi bi-pencil-square me-1"></i> Declare Results
        </button>
        <button v-if="prizes.length > 0" class="btn btn-warning rounded-pill px-3 text-xs fw-bold text-dark shadow-sm" @click="showPublishConfirm = true">
          <i class="bi bi-mega-phone-fill me-1"></i> Announce Winners
        </button>
      </div>
    </div>

    <!-- Empty State if No Results Declared Yet -->
    <div v-if="prizes.length === 0" class="card border-0 shadow-sm p-5 text-center bg-white rounded-4">
      <i class="bi bi-award display-3 text-secondary mb-3"></i>
      <h6 class="fw-bold text-dark">Results Not Yet Declared</h6>
      <p class="text-muted text-xs mb-3">The final results and winners for this competition will be published here after the Final round.</p>
      <button v-if="canManage" class="btn btn-warning rounded-pill px-4 text-xs mx-auto fw-bold text-dark" @click="showDeclareModal = true">
        <i class="bi bi-award-fill me-1"></i> Declare Results Now
      </button>
    </div>

    <!-- Podium & Results Layout -->
    <div v-else class="row g-4 align-items-end">
      
      <!-- 2nd Place Runner-Up -->
      <div v-if="runnerUp" class="col-12 col-md-4 order-2 order-md-1">
        <div class="card border-0 shadow-sm rounded-4 text-center p-4 bg-white border-top border-secondary border-4">
          <div class="podium-badge mx-auto bg-light text-secondary rounded-circle mb-3 d-flex align-items-center justify-content-center fw-bold" style="width: 56px; height: 56px; font-size: 1.5rem;">
            🥈
          </div>
          <span class="badge bg-secondary-subtle text-secondary rounded-pill text-xs fw-bold px-3 py-1 mb-2">RUNNER-UP</span>
          <h5 class="fw-bold text-dark mb-1">{{ runnerUp.winner_name || runnerUp.winnerName }}</h5>
          <p class="text-muted text-xs mb-0">{{ runnerUp.description || '2nd Place Runner-Up' }}</p>
        </div>
      </div>

      <!-- 1st Place Winner -->
      <div v-if="winner" class="col-12 col-md-4 order-1 order-md-2">
        <div class="card border-0 shadow-lg rounded-4 text-center p-4 bg-warning-subtle border-top border-warning border-4 transform-scale">
          <div class="podium-badge mx-auto bg-warning text-dark rounded-circle mb-3 d-flex align-items-center justify-content-center fw-bold shadow-sm" style="width: 68px; height: 68px; font-size: 2rem;">
            🏆
          </div>
          <span class="badge bg-warning text-dark rounded-pill text-xs fw-bold px-3 py-1 mb-2">WINNER</span>
          <h4 class="fw-bold text-dark mb-1">{{ winner.winner_name || winner.winnerName }}</h4>
          <p class="text-dark text-xs mb-0 fw-semibold">{{ winner.description || '1st Place Champion' }}</p>
        </div>
      </div>

      <!-- 3rd Place Second Runner-Up -->
      <div v-if="secondRunnerUp" class="col-12 col-md-4 order-3">
        <div class="card border-0 shadow-sm rounded-4 text-center p-4 bg-white border-top border-danger-subtle border-4">
          <div class="podium-badge mx-auto bg-light text-danger-emphasis rounded-circle mb-3 d-flex align-items-center justify-content-center fw-bold" style="width: 56px; height: 56px; font-size: 1.5rem;">
            🥉
          </div>
          <span class="badge bg-danger-subtle text-danger-emphasis rounded-pill text-xs fw-bold px-3 py-1 mb-2">2ND RUNNER-UP</span>
          <h5 class="fw-bold text-dark mb-1">{{ secondRunnerUp.winner_name || secondRunnerUp.winnerName }}</h5>
          <p class="text-muted text-xs mb-0">{{ secondRunnerUp.description || '3rd Place' }}</p>
        </div>
      </div>

    </div>

    <!-- Declare Results Modal -->
    <DeclareResultsModal 
      :show="showDeclareModal"
      :eventId="eventId"
      :prizes="prizes"
      @close="showDeclareModal = false"
      @declared="$emit('refresh')"
    />

    <!-- Announce Winners Confirmation Modal -->
    <div v-if="showPublishConfirm" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-card-custom bg-white p-4 rounded-4 shadow-lg text-center" style="max-width: 440px; width: 90%;">
        <div class="mb-3 text-warning">
          <i class="bi bi-megaphone-fill display-3"></i>
        </div>
        <h5 class="fw-bold text-dark mb-2">Publish Winner Announcement?</h5>
        <p class="text-secondary text-xs mb-4">
          Publish the final competition results to the Announcements board and send notifications to all registered participants?
        </p>

        <div class="d-flex align-items-center justify-content-center gap-2">
          <button class="btn btn-secondary rounded-pill px-4 text-xs" @click="showPublishConfirm = false">Cancel</button>
          <button class="btn btn-warning rounded-pill px-4 text-xs fw-bold text-dark shadow-sm" :disabled="publishing" @click="handlePublishWinners">
            <i v-if="publishing" class="spinner-border spinner-border-sm me-1"></i>
            Confirm & Publish
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.transform-scale {
  transform: translateY(-8px);
}
.modal-backdrop-custom {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1060;
}
</style>
