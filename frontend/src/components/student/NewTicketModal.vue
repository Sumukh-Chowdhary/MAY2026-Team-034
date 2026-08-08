<script setup>
import { ref, watch, onMounted } from 'vue'
import { createRequest } from '@/api/requests'
import { createActionTicket } from '@/api/actionTickets'
import { getClubs } from '@/api/clubs'
import { getUserAssignments } from '@/api/assignmentTickets'
import ApproverPicker from '@/components/common/ApproverPicker.vue'
import { useToast } from '@/composables/useToast'

const { showToast } = useToast()

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'submit'])

const isOrganizer = ref(false)
const userActiveClubs = ref([])
const clubsList = ref([])

const ticketType = ref('BECOME_VOLUNTEER')
const targetRole = ref('ORGANIZER') // 'ORGANIZER' or 'COORDINATOR'
const title = ref('')
const description = ref('')
const priority = ref('MEDIUM')
const selectedClubId = ref('')
const selectedClubName = ref('')
const taggedApprovers = ref([])

const loading = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      const res = await getUserAssignments(user.id)
      if (res.success && res.data?.active) {
        const orgGrants = res.data.active.filter(a => a.assignmentRole === 'ORGANIZER' || a.assignmentRole === 'PRESIDENT')
        if (orgGrants.length > 0) {
          isOrganizer.value = true
          userActiveClubs.value = orgGrants
          ticketType.value = 'CREATE_EVENT_AS_ORGANIZER'
        }
      }
    }
  } catch (e) {
    console.error(e)
  }
})

watch(() => props.show, async (newVal) => {
  if (newVal) {
    title.value = ''
    description.value = ''
    priority.value = 'MEDIUM'
    selectedClubId.value = ''
    taggedApprovers.value = []
    errorMessage.value = ''
    try {
      const clubs = await getClubs()
      clubsList.value = clubs || []
    } catch (e) {
      console.error('Failed to load clubs', e)
    }
  }
})

function onClubChange() {
  const club = clubsList.value.find(c => String(c.id) === String(selectedClubId.value))
  selectedClubName.value = club ? (club.name || club.club_name) : ''
}

async function handleSubmit() {
  if (!title.value.trim()) {
    errorMessage.value = 'Title is required.'
    showToast('Title is required.', 'warning')
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const approversPayload = taggedApprovers.value.map(a => ({
      approverId: a.approverId || a.id,
      role: a.role || 'APPROVER'
    }))

    if (ticketType.value === 'CREATE_EVENT_FOR_CLUB' || ticketType.value === 'CREATE_EVENT_GENERAL') {
      await createActionTicket({
        ticketType: ticketType.value,
        title: title.value,
        description: description.value,
        priority: priority.value,
        referenceType: selectedClubId.value ? 'CLUB' : null,
        referenceId: selectedClubId.value ? parseInt(selectedClubId.value) : null,
        referenceName: selectedClubName.value || null,
        approvers: approversPayload
      })
      showToast('Action Ticket submitted successfully!', 'success')
    } else {
      if (['CREATE_EVENT_AS_ORGANIZER', 'VENUE_REQUEST', 'BUDGET_REQUEST', 'BECOME_VOLUNTEER', 'BECOME_ORGANIZER'].includes(ticketType.value) && !selectedClubId.value) {
        errorMessage.value = 'Please select a club.'
        showToast('Please select a club.', 'warning')
        loading.value = false
        return
      }

      await createRequest({
        requestType: ticketType.value,
        title: title.value,
        description: description.value,
        priority: priority.value,
        referenceType: 'CLUB',
        referenceId: selectedClubId.value ? parseInt(selectedClubId.value) : null,
        referenceName: selectedClubName.value || null,
        approvers: approversPayload
      })
      showToast('Request submitted successfully!', 'success')
    }

    emit('submit')
    emit('close')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to submit.'
    errorMessage.value = msg
    showToast(msg, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-backdrop-glass" @click.self="$emit('close')">
      <div class="modal-box shadow-2xl">
        
        <!-- Header -->
        <div class="modal-header-custom">
          <div>
            <h4 class="fw-bold mb-0">Raise Student Request / Ticket</h4>
            <small class="text-secondary" v-if="isOrganizer">
              <i class="bi bi-star-fill text-warning me-1"></i> Student Organizer Mode Enabled
            </small>
          </div>
          <button class="btn-close-custom" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        </div>

        <!-- Body -->
        <div class="modal-body-custom">
          
          <!-- Type Selector -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Select Purpose</label>
            <select v-model="ticketType" class="form-select custom-input">
              <optgroup label="Club Organizer Permissions" v-if="isOrganizer">
                <option value="CREATE_EVENT_AS_ORGANIZER">Create Event for My Club</option>
                <option value="BUDGET_REQUEST">Budget Approval Request</option>
                <option value="VENUE_REQUEST">Venue Booking Request</option>
                <option value="SCHEDULE_REQUEST">Schedule Modification Request</option>
              </optgroup>

              <optgroup label="General Student Applications & Requests">
                <option value="BECOME_VOLUNTEER">Apply to Become a Volunteer</option>
                <option value="BECOME_ORGANIZER">Apply to Become a Club Organizer</option>
                <option value="CREATE_EVENT_FOR_CLUB">Ask Club / Admin to Create Event</option>
                <option value="CREATE_EVENT_GENERAL">Propose General Open Event</option>
              </optgroup>
            </select>
          </div>

          <!-- Target Recipient Role (Sprint 2) -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Target Recipient</label>
            <div class="d-flex gap-2">
              <div class="form-check flex-fill p-2 border rounded-3 text-xs" :class="{ 'bg-primary-subtle border-primary': targetRole === 'ORGANIZER' }">
                <input class="form-check-input" type="radio" id="tgtOrg" value="ORGANIZER" v-model="targetRole" />
                <label class="form-check-label fw-bold" for="tgtOrg">Student Organizer</label>
              </div>
              <div class="form-check flex-fill p-2 border rounded-3 text-xs" :class="{ 'bg-primary-subtle border-primary': targetRole === 'COORDINATOR' }">
                <input class="form-check-input" type="radio" id="tgtCoord" value="COORDINATOR" v-model="targetRole" />
                <label class="form-check-label fw-bold" for="tgtCoord">Faculty Coordinator</label>
              </div>
            </div>
          </div>

          <!-- Title -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Title / Subject</label>
            <input v-model="title" type="text" class="form-control custom-input" placeholder="e.g. Budget request for Robot Wars" />
          </div>

          <!-- Select Club -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Select Club</label>
            <select v-model="selectedClubId" class="form-select custom-input" @change="onClubChange">
              <option value="">-- Choose Club --</option>
              <option v-for="c in clubsList" :key="c.id" :value="c.id">
                {{ c.name || c.club_name }} ({{ c.category || c.club_category }})
              </option>
            </select>
          </div>

          <!-- Priority -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Priority</label>
            <select v-model="priority" class="form-select custom-input">
              <option value="LOW">Low Priority</option>
              <option value="MEDIUM">Medium Priority</option>
              <option value="HIGH">High Priority</option>
            </select>
          </div>

          <!-- Description -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Description & Details</label>
            <textarea v-model="description" class="form-control custom-input" rows="3" placeholder="Provide event details, estimated budget, or volunteer motivation..."></textarea>
          </div>

          <!-- Interactive Approver Tagging Picker -->
          <div class="mb-3">
            <ApproverPicker v-model="taggedApprovers" />
          </div>

          <!-- Alerts -->
          <div v-if="errorMessage" class="alert alert-danger-custom mb-3">{{ errorMessage }}</div>
          <div v-if="successMessage" class="alert alert-success-custom mb-3">{{ successMessage }}</div>

        </div>

        <!-- Footer -->
        <div class="modal-footer-custom">
          <button class="btn btn-secondary me-2 rounded-pill px-3" @click="$emit('close')">Cancel</button>
          <button class="btn btn-warning font-semibold rounded-pill px-4" :disabled="loading" @click="handleSubmit">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Submit Request
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop-glass {
  position: fixed;
  inset: 0;
  z-index: 1060;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-box {
  width: 100%;
  max-width: 650px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.modal-header-custom {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close-custom {
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
}

.modal-body-custom {
  padding: 1.5rem;
  max-height: 75vh;
  overflow-y: auto;
}

.custom-input {
  border-radius: 12px;
  border: 1px solid #cbd5e1;
}

.alert-danger-custom { background: #fef2f2; color: #991b1b; border-radius: 12px; padding: 10px; font-size: 0.85rem; }
.alert-success-custom { background: #f0fdf4; color: #166534; border-radius: 12px; padding: 10px; font-size: 0.85rem; }

.modal-footer-custom {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}
</style>