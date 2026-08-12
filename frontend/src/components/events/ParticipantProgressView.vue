<script setup>
import { ref, computed, onMounted } from 'vue'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import { getParticipantProgress } from '@/api/events'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  eventId: {
    type: Number,
    required: true
  }
})

const { showToast } = useToast()

const loading = ref(false)
const progressData = ref([])
const searchQuery = ref('')

async function fetchProgress() {
  loading.value = true
  try {
    const res = await getParticipantProgress(props.eventId)
    if (res && res.success) {
      progressData.value = res.data || []
    }
  } catch (err) {
    showToast('Failed to load participant progress.', 'error')
  } finally {
    loading.value = false
  }
}

const filteredProgress = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return progressData.value
  return progressData.value.filter(p => {
    const name = (p.userName || '').toLowerCase()
    const email = (p.userEmail || '').toLowerCase()
    const reg = (p.registerNumber || '').toLowerCase()
    return name.includes(q) || email.includes(q) || reg.includes(q)
  })
})

function getStatusBadgeClass(status) {
  const s = String(status || '').toUpperCase()
  if (s === 'WINNER') return 'bg-warning text-dark fw-bold border border-warning'
  if (s === 'RUNNER_UP') return 'bg-info-subtle text-info border border-info-subtle fw-bold'
  if (s === 'SHORTLISTED' || s === 'FINALIST') return 'bg-success-subtle text-success border border-success-subtle fw-bold'
  if (s === 'ELIMINATED' || s === 'DISQUALIFIED') return 'bg-danger-subtle text-danger border border-danger-subtle fw-semibold'
  return 'bg-light text-dark border'
}

onMounted(() => {
  fetchProgress()
})
</script>

<template>
  <div class="participant-progress-view container py-3">
    
    <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mb-4">
      <div>
        <h4 class="fw-bold text-dark mb-1"><i class="bi bi-person-lines-fill me-2 text-primary"></i> Participant Progress & History</h4>
        <p class="text-secondary text-xs mb-0">Track participant journeys, round shortlists, eliminations, and competition results.</p>
      </div>

      <div class="search-box position-relative" style="max-width: 380px; width: 100%;">
        <i class="bi bi-search position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"></i>
        <input v-model="searchQuery" type="text" class="form-control rounded-pill ps-5 pe-3 text-sm" placeholder="Search participant journey by name, roll no..." />
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted text-xs mt-2">Loading participant journey history...</p>
    </div>

    <div v-else-if="filteredProgress.length === 0" class="card border-0 shadow-sm p-5 text-center bg-white rounded-4">
      <i class="bi bi-person-x display-4 text-secondary mb-2"></i>
      <p class="text-muted text-sm mb-0">No participant progress records found matching your query.</p>
    </div>

    <div v-else class="row g-3">
      <div v-for="p in filteredProgress" :key="p.userId" class="col-12">
        <div class="card border-0 shadow-sm rounded-4 p-3 bg-white">
          
          <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 border-bottom pb-3 mb-3">
            
            <div class="d-flex align-items-center gap-3">
              <UserAvatar :name="p.userName" :size="42" />
              <div>
                <div class="d-flex align-items-center gap-2">
                  <h6 class="fw-bold text-dark mb-0">{{ p.userName }}</h6>
                  <span class="badge rounded-pill text-xs px-2 py-1" :class="getStatusBadgeClass(p.overallStatus)">
                    {{ p.overallStatus }}
                  </span>
                </div>
                <small class="text-muted text-xs">{{ p.userEmail }} &nbsp;•&nbsp; Roll: <strong class="text-dark">{{ p.registerNumber }}</strong> &nbsp;•&nbsp; Branch: {{ p.branch }}</small>
              </div>
            </div>

            <div class="text-md-end">
              <small class="text-muted text-xs d-block uppercase-label">Current State</small>
              <strong class="text-sm" :class="p.overallStatus === 'ELIMINATED' ? 'text-danger' : 'text-success'">
                {{ p.overallStatus }}
              </strong>
            </div>

          </div>

          <!-- Rounds Progression Stepper / Badges -->
          <div class="d-flex align-items-center flex-wrap gap-2 pt-1">
            <span class="badge bg-light text-dark border px-3 py-2 rounded-pill text-xs fw-semibold">
              <i class="bi bi-check-circle-fill text-success me-1"></i> Registration
            </span>

            <div v-for="r in p.roundsHistory" :key="r.sessionId" class="d-flex align-items-center gap-2">
              <i class="bi bi-chevron-right text-muted text-xs"></i>
              
              <div 
                class="round-history-pill p-2 px-3 rounded-pill border text-xs d-flex align-items-center gap-2"
                :class="r.status === 'SHORTLISTED' || r.status === 'FINALIST' || r.status === 'WINNER' ? 'bg-success-subtle border-success-subtle text-success-emphasis' : (r.status === 'ELIMINATED' ? 'bg-danger-subtle border-danger-subtle text-danger' : 'bg-light text-dark')"
              >
                <strong>{{ r.roundName }}:</strong>
                <span>Attended ({{ r.attendance }})</span>
                <span class="badge rounded-pill text-xs" :class="getStatusBadgeClass(r.status)">
                  {{ r.status }}
                </span>
                <small v-if="r.reason" class="fst-italic text-muted">({{ r.reason }})</small>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.uppercase-label {
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-weight: 700;
}
.round-history-pill {
  transition: all 0.2s ease;
}
</style>
