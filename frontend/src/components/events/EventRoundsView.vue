<script setup>
import { ref, onMounted } from 'vue'
import { getEventSessions, createEventSession, updateSessionStatus, getEventAttendance } from '@/api/events'
import EventShortlistModal from './EventShortlistModal.vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  eventId: {
    type: Number,
    required: true
  },
  canManage: {
    type: Boolean,
    default: true
  }
})

const { showToast } = useToast()

const loading = ref(false)
const sessions = ref([])
const showAddModal = ref(false)
const showShortlistModal = ref(false)

// Add round modal state
const roundName = ref('')
const roundDate = ref('')
const startTime = ref('09:00 AM')
const endTime = ref('12:00 PM')
const description = ref('')
const creating = ref(false)

// Shortlisting state
const selectedShortlistSession = ref(null)
const shortlistParticipants = ref([])

async function fetchRounds() {
  loading.value = true
  try {
    const res = await getEventSessions(props.eventId)
    if (res && res.success) {
      sessions.value = res.data || []
    }
  } catch (err) {
    showToast('Failed to load competition rounds.', 'error')
  } finally {
    loading.value = false
  }
}

async function handleCreateRound() {
  if (!roundName.value.trim()) return
  creating.value = true
  try {
    const nextRoundNo = sessions.value.length + 1
    const res = await createEventSession(props.eventId, {
      name: roundName.value,
      roundNumber: nextRoundNo,
      sessionDate: roundDate.value,
      startTime: startTime.value,
      endTime: endTime.value,
      description: description.value,
      status: 'UPCOMING'
    })
    showToast(res.message || 'Round created successfully!', 'success')
    showAddModal.value = false
    roundName.value = ''
    description.value = ''
    await fetchRounds()
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to create round.', 'error')
  } finally {
    creating.value = false
  }
}

async function toggleRoundStatus(session, targetStatus) {
  try {
    await updateSessionStatus(props.eventId, session.id, targetStatus)
    showToast(`Round "${session.name}" status updated to ${targetStatus}.`, 'success')
    await fetchRounds()
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to update round status.', 'error')
  }
}

async function openShortlistModal(session) {
  selectedShortlistSession.value = session
  try {
    const res = await getEventAttendance(props.eventId, session.id)
    if (res && res.success) {
      shortlistParticipants.value = res.participants || []
      showShortlistModal.value = true
    }
  } catch (err) {
    showToast('Failed to fetch participant list for shortlisting.', 'error')
  }
}

function handleShortlistCompleted() {
  fetchRounds()
}

onMounted(() => {
  fetchRounds()
})
</script>

<template>
  <div class="event-rounds-view container py-3">
    
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div>
        <h4 class="fw-bold text-dark mb-1"><i class="bi bi-diagram-3-fill me-2 text-primary"></i> Competition Rounds Timeline</h4>
        <p class="text-secondary text-xs mb-0">Manage competition stages, progress participants through rounds, and shortlist candidates.</p>
      </div>

      <button v-if="canManage" class="btn btn-primary rounded-pill px-3 text-xs fw-bold shadow-sm" @click="showAddModal = true">
        <i class="bi bi-plus-circle me-1"></i> Add Round
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted text-xs mt-2">Loading rounds timeline...</p>
    </div>

    <div v-else-if="sessions.length === 0" class="card border-0 shadow-sm p-5 text-center bg-white rounded-4">
      <i class="bi bi-trophy display-4 text-secondary mb-2"></i>
      <h6 class="fw-bold text-dark">No Competition Rounds Configured</h6>
      <p class="text-muted text-xs mb-3">Add competition rounds (e.g. Preliminary, Semi Final, Final) to begin tracking participant progress.</p>
      <button v-if="canManage" class="btn btn-primary rounded-pill px-4 text-xs mx-auto" @click="showAddModal = true">
        <i class="bi bi-plus-circle me-1"></i> Add First Round
      </button>
    </div>

    <!-- Vertical Timeline of Competition Rounds -->
    <div v-else class="timeline-container ps-md-2">
      <div v-for="(s, index) in sessions" :key="s.id" class="timeline-item d-flex gap-3 gap-md-4 mb-4 position-relative">
        
        <!-- Dedicated Left Timeline Column (Marker + Connector) -->
        <div class="timeline-column d-flex flex-column align-items-center position-relative">
          <div class="round-number-badge rounded-circle bg-primary text-white fw-bold d-flex align-items-center justify-content-center flex-shrink-0">
            {{ s.roundNumber }}
          </div>
          <!-- Vertical Connector Line inside timeline column only -->
          <div v-if="index < sessions.length - 1" class="timeline-connector"></div>
        </div>

        <!-- Right Content Round Card -->
        <div class="card round-card border-0 shadow-sm rounded-4 p-4 bg-white flex-grow-1 position-relative">
          <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mb-3">
            
            <div>
              <div class="d-flex align-items-center gap-2 mb-1">
                <h5 class="fw-bold text-dark mb-0">{{ s.name }}</h5>
                <span 
                  class="badge rounded-pill text-xs px-3 py-1"
                  :class="{
                    'bg-success-subtle text-success border border-success-subtle': s.status === 'ACTIVE',
                    'bg-primary-subtle text-primary border border-primary-subtle': s.status === 'COMPLETED',
                    'bg-secondary-subtle text-secondary border border-secondary-subtle': s.status === 'UPCOMING'
                  }"
                >
                  ● {{ s.status }}
                </span>
              </div>
              <small class="text-muted text-xs d-block">
                <i class="bi bi-calendar-event me-1"></i> {{ s.sessionDate || 'Date TBD' }} &nbsp;•&nbsp; 
                <i class="bi bi-clock me-1"></i> {{ s.startTime }} - {{ s.endTime }}
              </small>
            </div>

            <!-- Stats Pill Summary -->
            <div class="d-flex align-items-center gap-3 bg-light px-3 py-2 rounded-pill border">
              <div>
                <small class="text-muted text-xs d-block">Participants</small>
                <strong class="text-dark text-xs">{{ s.totalCount }}</strong>
              </div>
              <div class="border-start ps-3">
                <small class="text-muted text-xs d-block">Shortlisted</small>
                <strong class="text-success text-xs">{{ s.shortlistedCount }}</strong>
              </div>
              <div class="border-start ps-3">
                <small class="text-muted text-xs d-block">Eliminated</small>
                <strong class="text-danger text-xs">{{ s.eliminatedCount }}</strong>
              </div>
            </div>

          </div>

          <p v-if="s.description" class="text-secondary text-sm mb-3 ps-1">
            <i class="bi bi-info-circle me-1 text-primary"></i> {{ s.description }}
          </p>

          <!-- Organizer Action Bar -->
          <div v-if="canManage" class="d-flex align-items-center justify-content-end gap-2 pt-3 border-top">
            <button 
              v-if="s.status === 'UPCOMING'" 
              class="btn btn-outline-success rounded-pill px-3 text-xs fw-semibold"
              @click="toggleRoundStatus(s, 'ACTIVE')"
            >
              <i class="bi bi-play-circle me-1"></i> Set Active
            </button>

            <button 
              v-if="s.status === 'ACTIVE' || s.status === 'COMPLETED'"
              class="btn btn-primary rounded-pill px-3 text-xs fw-bold shadow-sm"
              @click="openShortlistModal(s)"
            >
              <i class="bi bi-check-square me-1"></i> Shortlist Participants
            </button>

            <button 
              v-if="s.status === 'ACTIVE'"
              class="btn btn-outline-secondary rounded-pill px-3 text-xs fw-semibold"
              @click="toggleRoundStatus(s, 'COMPLETED')"
            >
              <i class="bi bi-check-circle me-1"></i> Complete Round
            </button>
          </div>

        </div>

      </div>
    </div>

    <!-- Modal to Add New Competition Round -->
    <div v-if="showAddModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-card-custom bg-white p-4 rounded-4 shadow-lg" style="max-width: 480px; width: 90%;">
        <div class="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
          <h5 class="fw-bold text-dark mb-0">Add Competition Round</h5>
          <button class="btn-close" @click="showAddModal = false"></button>
        </div>

        <div class="mb-3">
          <label class="form-label text-xs fw-bold">Round Name</label>
          <input v-model="roundName" type="text" class="form-control rounded-3 text-sm" placeholder="e.g. Semi Final / Coding Sprint 2" />
        </div>

        <div class="mb-3">
          <label class="form-label text-xs fw-bold">Date</label>
          <input v-model="roundDate" type="date" class="form-control rounded-3 text-sm" />
        </div>

        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label text-xs fw-bold">Start Time</label>
            <input v-model="startTime" type="text" class="form-control rounded-3 text-sm" placeholder="02:00 PM" />
          </div>
          <div class="col-6">
            <label class="form-label text-xs fw-bold">End Time</label>
            <input v-model="endTime" type="text" class="form-control rounded-3 text-sm" placeholder="05:00 PM" />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label text-xs fw-bold">Description / Scope (Optional)</label>
          <textarea v-model="description" class="form-control rounded-3 text-sm" rows="2" placeholder="e.g. Top 20 shortlisted candidates competing..."></textarea>
        </div>

        <div class="d-flex justify-content-end gap-2 pt-2 border-top">
          <button class="btn btn-secondary rounded-pill px-3 text-xs" @click="showAddModal = false">Cancel</button>
          <button class="btn btn-primary rounded-pill px-4 text-xs fw-bold" :disabled="creating" @click="handleCreateRound">
            <i v-if="creating" class="spinner-border spinner-border-sm me-1"></i>
            Create Round
          </button>
        </div>
      </div>
    </div>

    <!-- Shortlist Modal -->
    <EventShortlistModal 
      :show="showShortlistModal"
      :eventId="eventId"
      :session="selectedShortlistSession"
      :participants="shortlistParticipants"
      @close="showShortlistModal = false"
      @completed="handleShortlistCompleted"
    />

  </div>
</template>

<style scoped>
.timeline-item {
  margin-bottom: 1.75rem !important;
}

.timeline-column {
  width: 44px;
  flex-shrink: 0;
}

.round-number-badge {
  width: 44px;
  height: 44px;
  font-size: 1.05rem;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  position: relative;
  z-index: 2;
}

.timeline-connector {
  position: absolute;
  top: 44px;
  bottom: -28px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  background-color: #cbd5e1;
  z-index: 1;
}

.round-card {
  min-width: 0;
}

.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1050;
}
</style>
