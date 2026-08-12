<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api/axios'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  eventId: { type: Number, required: true },
  event: { type: Object, required: true },
  userRole: { type: String, default: 'STUDENT' },
  isClubMember: { type: Boolean, default: true },
  isFacultyCoordinator: { type: Boolean, default: false }
})

const emit = defineEmits(['refresh'])
const { showToast } = useToast()

const positions = ref([])
const volunteerRecords = ref([])
const loading = ref(true)

// Application Modal State
const showApplyModal = ref(false)
const selectedPosition = ref(null)
const applyForm = ref({
  positionName: '',
  startDate: '',
  endDate: '',
  remarks: ''
})
const isSubmitting = ref(false)

const userStr = localStorage.getItem('user')
const currentUser = userStr ? JSON.parse(userStr) : null
const isLegacy = computed(() => currentUser?.status === 'LEGACY')

onMounted(async () => {
  await loadPositionsAndVolunteers()
})

async function loadPositionsAndVolunteers() {
  loading.value = true
  try {
    const [posRes, volRes] = await Promise.all([
      api.get(`/events/${props.eventId}/volunteer-positions`).catch(() => ({ data: [] })),
      api.get(`/events/${props.eventId}`).catch(() => ({ data: {} }))
    ])

    positions.value = posRes.data || []
    volunteerRecords.value = volRes.data?.volunteers || []
  } catch (err) {
    console.error('Failed to load volunteer data', err)
  } finally {
    loading.value = false
  }
}

function getMyStatusForPosition(posName) {
  if (!currentUser || !volunteerRecords.value.length) return null
  const record = volunteerRecords.value.find(v => Number(v.userId) === Number(currentUser.id) && (v.positionName === posName || v.position === posName))
  return record ? record.status : null
}

function openApplyModal(pos) {
  if (isLegacy.value) {
    showToast('Graduated/Legacy students cannot apply as volunteers.', 'warning')
    return
  }
  selectedPosition.value = pos
  
  // Default start date = event start date or today
  const evStart = props.event?.startDate || new Date().toISOString().split('T')[0]
  const startDateObj = new Date(evStart)
  const endDateObj = new Date(startDateObj)
  endDateObj.setDate(endDateObj.getDate() + 3) // 3-day duration

  applyForm.value = {
    positionName: pos.positionName,
    startDate: evStart,
    endDate: endDateObj.toISOString().split('T')[0],
    remarks: ''
  }
  showApplyModal.value = true
}

async function handleApplySubmit() {
  if (!applyForm.value.positionName) return
  isSubmitting.value = true
  try {
    const res = await api.post(`/events/${props.eventId}/volunteer-apply`, {
      positionName: applyForm.value.positionName,
      startDate: applyForm.value.startDate,
      endDate: applyForm.value.endDate,
      remarks: applyForm.value.remarks
    })

    showToast(res.data?.message || 'Volunteer application submitted successfully!', 'success')
    showApplyModal.value = false
    await loadPositionsAndVolunteers()
    emit('refresh')
  } catch (err) {
    const msg = err.response?.data?.error || err.message || 'Failed to submit volunteer application.'
    showToast(msg, 'error')
  } finally {
    isSubmitting.value = false
  }
}

async function handleVolunteerAction(volunteerId, newStatus) {
  try {
    await api.patch(`/events/${props.eventId}/volunteers/${volunteerId}`, { status: newStatus })
    showToast(`Volunteer application ${newStatus.toLowerCase()} successfully!`, 'success')
    await loadPositionsAndVolunteers()
    emit('refresh')
  } catch (err) {
    showToast('Failed to update volunteer application status.', 'error')
  }
}
</script>

<template>
  <div class="volunteer-section">
    <!-- 1. Available Positions Grid/Table -->
    <div class="mb-4">
      <h6 class="fw-bold text-dark mb-3 d-flex align-items-center justify-content-between">
        <span><i class="bi bi-people-fill text-primary me-2"></i> Available Volunteer Positions</span>
        <span class="badge bg-light text-dark border fw-normal text-xs">
          Club: {{ event.clubName || event.club || 'Organizing Club' }}
        </span>
      </h6>

      <div v-if="loading" class="text-center py-4 text-muted">
        <span class="spinner-border spinner-border-sm me-2"></span> Loading positions...
      </div>

      <div v-else-if="positions.length === 0" class="text-center py-4 text-muted border rounded-3 bg-light">
        No volunteer positions posted for this event.
      </div>

      <div v-else class="table-responsive">
        <table class="table align-middle border rounded-3 overflow-hidden shadow-sm">
          <thead class="bg-light">
            <tr>
              <th>Position</th>
              <th class="text-center">Capacity</th>
              <th class="text-center">Filled</th>
              <th class="text-center">Remaining</th>
              <th class="text-end">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pos in positions" :key="pos.id">
              <td class="fw-semibold text-dark">
                <i class="bi bi-briefcase me-2 text-primary"></i> {{ pos.positionName }}
              </td>
              <td class="text-center"><span class="badge bg-secondary text-white">{{ pos.maxCapacity }}</span></td>
              <td class="text-center"><span class="badge bg-info text-dark">{{ pos.filledCount }}</span></td>
              <td class="text-center">
                <span :class="pos.isFull ? 'badge bg-danger' : 'badge bg-success'">
                  {{ pos.isFull ? '0' : (pos.maxCapacity - pos.filledCount) }}
                </span>
              </td>
              <td class="text-end">
                <!-- Status & Action Buttons -->
                <template v-if="userRole === 'STUDENT'">
                  <span v-if="getMyStatusForPosition(pos.positionName) === 'PENDING'" class="badge bg-warning text-dark px-3 py-2">
                    <i class="bi bi-clock me-1"></i> Pending Approval
                  </span>
                  <span v-else-if="getMyStatusForPosition(pos.positionName) === 'ACTIVE' || getMyStatusForPosition(pos.positionName) === 'APPROVED'" class="badge bg-success px-3 py-2">
                    <i class="bi bi-check-circle me-1"></i> Assigned
                  </span>
                  <span v-else-if="getMyStatusForPosition(pos.positionName) === 'EXPIRED'" class="badge bg-secondary me-2">
                    Previous Assignment
                  </span>
                  
                  <button 
                    v-if="!['PENDING', 'ACTIVE', 'APPROVED'].includes(getMyStatusForPosition(pos.positionName))"
                    class="btn btn-sm btn-primary rounded-pill px-3 fw-semibold"
                    :disabled="pos.isFull || isLegacy || !isClubMember"
                    @click="openApplyModal(pos)"
                  >
                    <span v-if="pos.isFull" class="text-uppercase text-xs fw-bold">FULL</span>
                    <span v-else-if="isLegacy" class="text-xs">Legacy User</span>
                    <span v-else-if="!isClubMember" class="text-xs">Club Members Only</span>
                    <span v-else><i class="bi bi-pencil-square me-1"></i> Apply</span>
                  </button>
                </template>

                <template v-else>
                  <span v-if="pos.isFull" class="badge bg-danger">FULL</span>
                  <span v-else class="badge bg-success">Available</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 2. Faculty / Admin Management View -->
    <div v-if="userRole === 'ADMIN' || isFacultyCoordinator" class="mt-4 border-top pt-4">
      <h6 class="fw-bold text-dark mb-3">
        <i class="bi bi-clipboard-check me-2 text-success"></i> Applications & Assigned Roster
      </h6>

      <div v-if="volunteerRecords.length === 0" class="text-muted text-xs">
        No volunteer applications submitted yet.
      </div>

      <div v-else class="table-responsive">
        <table class="table align-middle table-hover border rounded-3">
          <thead class="bg-light">
            <tr>
              <th>Applicant</th>
              <th>Registration ID</th>
              <th>Position</th>
              <th>Duration</th>
              <th>Status</th>
              <th v-if="isFacultyCoordinator || userRole === 'ADMIN'" class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="vol in volunteerRecords" :key="vol.id">
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px; font-size: 13px;">
                    {{ (vol.userName || 'U')[0] }}
                  </div>
                  <div>
                    <div class="fw-semibold text-dark text-sm">{{ vol.userName }}</div>
                    <small class="text-muted text-xs">{{ vol.userEmail || '' }}</small>
                  </div>
                </div>
              </td>
              <td><code class="text-primary fw-semibold">{{ vol.registerNumber || vol.rollNumber || 'N/A' }}</code></td>
              <td class="fw-semibold text-sm">{{ vol.positionName || vol.position || 'General Volunteer' }}</td>
              <td class="text-xs text-muted">
                <span v-if="vol.startDate">{{ vol.startDate.split('T')[0] }} to {{ vol.endDate ? vol.endDate.split('T')[0] : 'End' }}</span>
                <span v-else>3-day event duration</span>
              </td>
              <td>
                <span class="badge" :class="{
                  'bg-warning text-dark': vol.status === 'PENDING',
                  'bg-success': vol.status === 'ACTIVE' || vol.status === 'APPROVED',
                  'bg-secondary': vol.status === 'EXPIRED',
                  'bg-danger': vol.status === 'REJECTED'
                }">
                  {{ vol.status }}
                </span>
              </td>
              <td v-if="isFacultyCoordinator || userRole === 'ADMIN'" class="text-end">
                <div v-if="vol.status === 'PENDING'" class="btn-group btn-group-sm">
                  <button class="btn btn-sm btn-success rounded-start-pill px-3" @click="handleVolunteerAction(vol.id, 'APPROVED')">
                    <i class="bi bi-check me-1"></i> Approve
                  </button>
                  <button class="btn btn-sm btn-outline-danger rounded-end-pill px-3" @click="handleVolunteerAction(vol.id, 'REJECTED')">
                    <i class="bi bi-x me-1"></i> Reject
                  </button>
                </div>
                <span v-else class="text-xs text-muted">Processed</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Application Modal -->
    <div v-if="showApplyModal" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4">
          <div class="modal-header border-0 pb-0">
            <h5 class="modal-title fw-bold text-dark">
              <i class="bi bi-hand-thumbs-up me-2 text-primary"></i> Volunteer Application
            </h5>
            <button type="button" class="btn-close" @click="showApplyModal = false"></button>
          </div>
          <div class="modal-body py-3">
            <div class="alert alert-light border rounded-3 mb-3 text-xs text-muted">
              Applying for <strong>{{ applyForm.positionName }}</strong> under <strong>{{ event.clubName || event.club || 'Organizing Club' }}</strong>.
              Your application ticket will be submitted to the Faculty Coordinator for review.
            </div>

            <div class="mb-3">
              <label class="form-label text-xs fw-semibold">Target Position</label>
              <input type="text" class="form-control" :value="applyForm.positionName" readonly disabled />
            </div>

            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label text-xs fw-semibold">Start Date</label>
                <input v-model="applyForm.startDate" type="date" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label text-xs fw-semibold">End Date (3-Day Duration)</label>
                <input v-model="applyForm.endDate" type="date" class="form-control" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label text-xs fw-semibold">Optional Message / Remarks</label>
              <textarea v-model="applyForm.remarks" class="form-control" rows="2" placeholder="Briefly state your motivation or experience..."></textarea>
            </div>
          </div>
          <div class="modal-footer border-0 pt-0">
            <button class="btn btn-secondary rounded-pill px-4" @click="showApplyModal = false">Cancel</button>
            <button class="btn btn-primary rounded-pill px-4 fw-semibold" :disabled="isSubmitting" @click="handleApplySubmit">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
              <span v-else>Submit Ticket</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
