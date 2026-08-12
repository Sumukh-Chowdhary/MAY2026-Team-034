<script setup>
import { ref, computed, onMounted } from 'vue'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import EventShortlistModal from './EventShortlistModal.vue'
import { getEventAttendance, saveEventAttendance, createEventSession } from '@/api/events'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  eventId: {
    type: Number,
    required: true
  },
  canManageSessions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['back'])
const { showToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const eventData = ref(null)
const selectedSessionId = ref(null)
const sessionDetails = ref(null)
const sessionsList = ref([])
const summaryStats = ref({ present: 0, absent: 0, pending: 0, total: 0 })
const participants = ref([])
const searchQuery = ref('')
const saveSuccessMessage = ref('')

// Add Session & Shortlist Modal state
const showAddSessionModal = ref(false)
const showShortlistModal = ref(false)
const newSessionName = ref('')
const newSessionDate = ref('')
const newStartTime = ref('09:00 AM')
const newEndTime = ref('10:00 AM')
const newDescription = ref('')
const isCreatingSession = ref(false)

async function fetchAttendanceData(sessionId = null) {
  loading.value = true
  saveSuccessMessage.value = ''
  try {
    const res = await getEventAttendance(props.eventId, sessionId)
    if (res && res.success) {
      eventData.value = res.event
      sessionDetails.value = res.session
      sessionsList.value = res.sessions || []
      selectedSessionId.value = res.session ? res.session.id : null
      summaryStats.value = res.summary || { present: 0, absent: 0, pending: 0, total: 0 }
      participants.value = (res.participants || []).map(p => ({
        ...p,
        draftStatus: p.status || 'PENDING'
      }))
    }
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to load attendance records.', 'error')
  } finally {
    loading.value = false
  }
}

function handleSessionChange() {
  if (selectedSessionId.value) {
    fetchAttendanceData(selectedSessionId.value)
  }
}

const filteredParticipants = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return participants.value
  return participants.value.filter(p => {
    const name = (p.userName || '').toLowerCase()
    const email = (p.userEmail || '').toLowerCase()
    const reg = (p.registerNumber || '').toLowerCase()
    return name.includes(q) || email.includes(q) || reg.includes(q)
  })
})

const liveSummary = computed(() => {
  const total = participants.value.length
  const present = participants.value.filter(p => p.draftStatus === 'PRESENT').length
  const absent = participants.value.filter(p => p.draftStatus === 'ABSENT').length
  const pending = total - present - absent
  return { present, absent, pending, total }
})

function markAllPresent() {
  participants.value.forEach(p => {
    p.draftStatus = 'PRESENT'
  })
  showToast('Marked all participants as Present.', 'info')
}

function markAllAbsent() {
  participants.value.forEach(p => {
    p.draftStatus = 'ABSENT'
  })
  showToast('Marked all participants as Absent.', 'info')
}

function resetAll() {
  participants.value.forEach(p => {
    p.draftStatus = p.status || 'PENDING'
  })
  showToast('Reset attendance changes.', 'info')
}

async function handleSaveAttendance() {
  if (!selectedSessionId.value) return
  saving.value = true
  saveSuccessMessage.value = ''
  try {
    const payload = {
      sessionId: selectedSessionId.value,
      records: participants.value.map(p => ({
        userId: p.userId,
        status: p.draftStatus
      }))
    }
    await saveEventAttendance(props.eventId, payload)
    saveSuccessMessage.value = 'Attendance saved successfully!'
    showToast('Attendance records saved successfully!', 'success')
    await fetchAttendanceData(selectedSessionId.value)
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to save attendance.', 'error')
  } finally {
    saving.value = false
  }
}

async function handleCreateSession() {
  if (!newSessionName.value.trim()) return
  isCreatingSession.value = true
  try {
    const res = await createEventSession(props.eventId, {
      name: newSessionName.value,
      sessionDate: newSessionDate.value,
      startTime: newStartTime.value,
      endTime: newEndTime.value,
      description: newDescription.value
    })
    showToast(res.message || 'Session created successfully!', 'success')
    showAddSessionModal.value = false
    newSessionName.value = ''
    newDescription.value = ''
    await fetchAttendanceData(res.data.id)
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to create session.', 'error')
  } finally {
    isCreatingSession.value = false
  }
}

onMounted(() => {
  fetchAttendanceData()
})
</script>

<template>
  <div class="event-attendance-system container py-4">
    
    <!-- Top Bar Navigation & Header -->
    <div class="d-flex align-items-center justify-content-between mb-4 pb-3 border-bottom">
      <div class="d-flex align-items-center gap-3">
        <button class="btn btn-outline-secondary rounded-pill px-3 py-2 text-sm fw-bold d-flex align-items-center gap-2" @click="$emit('back')">
          <i class="bi bi-arrow-left"></i> Back to Event
        </button>
        <div>
          <span class="badge bg-primary-subtle text-primary rounded-pill text-xs fw-semibold px-2 py-1 mb-1 d-inline-block">
            {{ eventData?.club || 'Institutional Event' }}
          </span>
          <h3 class="fw-bold mb-0 text-dark">{{ eventData?.name || 'Event Attendance' }}</h3>
        </div>
      </div>

      <button v-if="canManageSessions" class="btn btn-primary rounded-pill px-3 text-xs fw-semibold" @click="showAddSessionModal = true">
        <i class="bi bi-plus-circle me-1"></i> Add Session / Round
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted text-xs mt-2">Loading attendance records...</p>
    </div>

    <div v-else>

      <!-- Session Selection & Details Bar -->
      <div class="card border-0 shadow-sm rounded-4 p-4 mb-4 bg-white">
        <div class="row align-items-center g-3">
          <div class="col-md-5">
            <label class="form-label text-xs fw-bold text-uppercase text-secondary mb-1">SELECT ATTENDANCE SESSION / ROUND</label>
            <select v-model="selectedSessionId" class="form-select custom-select-lg fw-bold text-dark" @change="handleSessionChange">
              <option v-for="s in sessionsList" :key="s.id" :value="s.id">
                {{ s.name }} ({{ s.sessionDate || 'TBD' }}) — {{ s.presentCount }}/{{ s.totalCount }} Present
              </option>
            </select>
          </div>

          <div class="col-md-7">
            <div class="d-flex flex-wrap align-items-center gap-4 pt-3 pt-md-0 border-start-md ps-md-4">
              <div>
                <span class="text-xs text-muted d-block uppercase-label">Date</span>
                <span class="fw-bold text-dark text-sm"><i class="bi bi-calendar-event me-1 text-primary"></i> {{ sessionDetails?.sessionDate || 'Today' }}</span>
              </div>
              <div>
                <span class="text-xs text-muted d-block uppercase-label">Time Window</span>
                <span class="fw-bold text-dark text-sm"><i class="bi bi-clock me-1 text-info"></i> {{ sessionDetails?.startTime || '09:00 AM' }} - {{ sessionDetails?.endTime || '05:00 PM' }}</span>
              </div>
              <div v-if="sessionDetails?.description">
                <span class="text-xs text-muted d-block uppercase-label">Round Scope</span>
                <span class="fw-bold text-dark text-sm"><i class="bi bi-info-circle me-1 text-secondary"></i> {{ sessionDetails.description }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Attendance Summary Cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="stat-box p-3 rounded-4 bg-success-subtle border border-success-subtle text-center">
            <span class="text-success-emphasis fw-bold text-uppercase text-xs d-block">Present</span>
            <span class="display-6 fw-bold text-success">{{ liveSummary.present }}</span>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="stat-box p-3 rounded-4 bg-danger-subtle border border-danger-subtle text-center">
            <span class="text-danger-emphasis fw-bold text-uppercase text-xs d-block">Absent</span>
            <span class="display-6 fw-bold text-danger">{{ liveSummary.absent }}</span>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="stat-box p-3 rounded-4 bg-warning-subtle border border-warning-subtle text-center">
            <span class="text-warning-emphasis fw-bold text-uppercase text-xs d-block">Pending</span>
            <span class="display-6 fw-bold text-warning-emphasis">{{ liveSummary.pending }}</span>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="stat-box p-3 rounded-4 bg-light border text-center">
            <span class="text-secondary fw-bold text-uppercase text-xs d-block">Total Registrants</span>
            <span class="display-6 fw-bold text-dark">{{ liveSummary.total }}</span>
          </div>
        </div>
      </div>

      <!-- Participants List & Marking Controls -->
      <div class="card border-0 shadow-sm rounded-4 p-4 mb-4 bg-white">
        
        <!-- Controls Bar -->
        <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3 mb-4">
          <div class="search-box position-relative flex-grow-1" style="max-width: 400px;">
            <i class="bi bi-search position-absolute top-50 start-0 translate-middle-y ms-3 text-muted"></i>
            <input v-model="searchQuery" type="text" class="form-control rounded-pill ps-5 pe-3 text-sm" placeholder="Search participants by name, email, roll no..." />
          </div>

          <div class="d-flex align-items-center gap-2 flex-wrap">
            <button class="btn btn-outline-success rounded-pill px-3 text-xs fw-semibold" @click="markAllPresent">
              <i class="bi bi-check-all me-1"></i> Mark All Present
            </button>
            <button class="btn btn-outline-danger rounded-pill px-3 text-xs fw-semibold" @click="markAllAbsent">
              <i class="bi bi-x-circle me-1"></i> Mark All Absent
            </button>
            <button class="btn btn-outline-secondary rounded-pill px-3 text-xs fw-semibold" @click="resetAll">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
            <button class="btn btn-primary rounded-pill px-4 text-xs fw-bold shadow-sm" :disabled="saving" @click="handleSaveAttendance">
              <i v-if="saving" class="spinner-border spinner-border-sm me-1"></i>
              <i v-else class="bi bi-floppy me-1"></i>
              Save Attendance
            </button>
            <button v-if="canManageSessions" class="btn btn-success rounded-pill px-3 text-xs fw-bold shadow-sm" @click="showShortlistModal = true">
              <i class="bi bi-check-square me-1"></i> Shortlist Participants
            </button>
          </div>
        </div>

        <div v-if="saveSuccessMessage" class="alert alert-success py-2 px-3 text-xs rounded-3 mb-3 d-flex align-items-center justify-content-between">
          <span><i class="bi bi-check-circle-fill me-2"></i> {{ saveSuccessMessage }}</span>
          <button class="btn-close btn-close-xs" @click="saveSuccessMessage = ''"></button>
        </div>

        <!-- Participants Table / List -->
        <div v-if="filteredParticipants.length === 0" class="text-center py-5 text-muted">
          <i class="bi bi-people display-5 d-block mb-2 text-secondary"></i>
          <p class="mb-0 text-sm">No registered participants found matching your query.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light text-xs text-uppercase text-secondary">
              <tr>
                <th>Participant</th>
                <th>Register / ID No.</th>
                <th>Branch</th>
                <th class="text-center" style="width: 320px;">Attendance Control</th>
                <th class="text-end">Last Updated</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filteredParticipants" :key="p.userId">
                <td>
                  <div class="d-flex align-items-center gap-3">
                    <UserAvatar :name="p.userName" :size="36" />
                    <div>
                      <h6 class="fw-bold text-dark mb-0 text-sm">{{ p.userName }}</h6>
                      <small class="text-muted text-xs">{{ p.userEmail }}</small>
                    </div>
                  </div>
                </td>

                <td>
                  <span class="badge bg-light text-dark font-monospace px-2 py-1 border text-xs">{{ p.registerNumber }}</span>
                </td>

                <td>
                  <span class="text-xs text-secondary">{{ p.branch }}</span>
                </td>

                <td>
                  <div class="btn-group w-100 rounded-pill p-1 bg-light border" role="group">
                    <button 
                      type="button" 
                      class="btn btn-sm text-xs rounded-pill border-0 transition-all"
                      :class="p.draftStatus === 'PRESENT' ? 'btn-success fw-bold text-white shadow-sm' : 'btn-light text-muted'"
                      @click="p.draftStatus = 'PRESENT'"
                    >
                      <i class="bi bi-check-lg me-1"></i> Present
                    </button>

                    <button 
                      type="button" 
                      class="btn btn-sm text-xs rounded-pill border-0 transition-all"
                      :class="p.draftStatus === 'ABSENT' ? 'btn-danger fw-bold text-white shadow-sm' : 'btn-light text-muted'"
                      @click="p.draftStatus = 'ABSENT'"
                    >
                      <i class="bi bi-x-lg me-1"></i> Absent
                    </button>

                    <button 
                      type="button" 
                      class="btn btn-sm text-xs rounded-pill border-0 transition-all"
                      :class="p.draftStatus === 'PENDING' ? 'btn-warning text-dark fw-bold shadow-sm' : 'btn-light text-muted'"
                      @click="p.draftStatus = 'PENDING'"
                    >
                      <i class="bi bi-dash-circle me-1"></i> Pending
                    </button>
                  </div>
                </td>

                <td class="text-end">
                  <span v-if="p.markedByName" class="d-block text-xs fw-semibold text-dark">By: {{ p.markedByName }}</span>
                  <small v-if="p.updatedAt" class="text-muted text-xs d-block">{{ new Date(p.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</small>
                  <small v-else class="text-muted text-xs italic">Not saved yet</small>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Attendance History Section -->
      <div class="card border-0 shadow-sm rounded-4 p-4 bg-white">
        <h5 class="fw-bold text-dark mb-3"><i class="bi bi-clock-history me-2 text-primary"></i> Attendance Rounds History</h5>
        <div class="row g-3">
          <div v-for="s in sessionsList" :key="s.id" class="col-md-4">
            <div 
              class="history-card p-3 rounded-4 border transition-all cursor-pointer"
              :class="selectedSessionId === s.id ? 'border-primary bg-primary-subtle' : 'bg-light'"
              @click="selectedSessionId = s.id; handleSessionChange()"
            >
              <div class="d-flex align-items-center justify-content-between mb-2">
                <h6 class="fw-bold mb-0 text-dark">{{ s.name }}</h6>
                <span class="badge bg-primary text-white text-xs rounded-pill px-2 py-1">
                  {{ s.presentCount }} / {{ s.totalCount }} Present
                </span>
              </div>
              <small class="text-muted d-block text-xs mb-1"><i class="bi bi-calendar-event me-1"></i> {{ s.sessionDate || 'Date TBD' }}</small>
              <small class="text-muted d-block text-xs"><i class="bi bi-clock me-1"></i> {{ s.startTime }} - {{ s.endTime }}</small>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Modal for Adding New Attendance Session -->
    <div v-if="showAddSessionModal" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-card-custom bg-white p-4 rounded-4 shadow-lg" style="max-width: 480px; width: 90%;">
        <div class="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
          <h5 class="fw-bold text-dark mb-0">Create Attendance Round / Session</h5>
          <button class="btn-close" @click="showAddSessionModal = false"></button>
        </div>

        <div class="mb-3">
          <label class="form-label text-xs fw-bold">Session Name / Round</label>
          <input v-model="newSessionName" type="text" class="form-control rounded-3 text-sm" placeholder="e.g. Round 2 - Shortlisted Participants" />
        </div>

        <div class="mb-3">
          <label class="form-label text-xs fw-bold">Session Date</label>
          <input v-model="newSessionDate" type="date" class="form-control rounded-3 text-sm" />
        </div>

        <div class="row g-2 mb-3">
          <div class="col-6">
            <label class="form-label text-xs fw-bold">Start Time</label>
            <input v-model="newStartTime" type="text" class="form-control rounded-3 text-sm" placeholder="09:00 AM" />
          </div>
          <div class="col-6">
            <label class="form-label text-xs fw-bold">End Time</label>
            <input v-model="newEndTime" type="text" class="form-control rounded-3 text-sm" placeholder="11:00 AM" />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label text-xs fw-bold">Scope / Description (Optional)</label>
          <textarea v-model="newDescription" class="form-control rounded-3 text-sm" rows="2" placeholder="e.g. Morning round for tech track..."></textarea>
        </div>

        <div class="d-flex justify-content-end gap-2 pt-2 border-top">
          <button class="btn btn-secondary rounded-pill px-3 text-xs" @click="showAddSessionModal = false">Cancel</button>
          <button class="btn btn-primary rounded-pill px-4 text-xs fw-bold" :disabled="isCreatingSession" @click="handleCreateSession">
            <i v-if="isCreatingSession" class="spinner-border spinner-border-sm me-1"></i>
            Create Session
          </button>
        </div>
      </div>
    </div>

    <!-- Shortlist Modal -->
    <EventShortlistModal
      :show="showShortlistModal"
      :eventId="eventId"
      :session="sessionDetails"
      :participants="participants"
      @close="showShortlistModal = false"
      @completed="fetchAttendanceData(selectedSessionId)"
    />

  </div>
</template>

<style scoped>
.event-attendance-system {
  font-family: inherit;
}
.custom-select-lg {
  font-size: 1.05rem;
  padding: 0.65rem 1rem;
  border-radius: 0.75rem;
  border-color: #cbd5e1;
}
.uppercase-label {
  font-size: 0.68rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-weight: 700;
}
.history-card {
  cursor: pointer;
}
.history-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
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
.transition-all {
  transition: all 0.2s ease-in-out;
}
</style>
