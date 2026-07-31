<script setup>
import { ref, watch } from 'vue'
import { createRequest } from '@/api/requests'
import { createActionTicket } from '@/api/actionTickets'
import { getClubs } from '@/api/clubs'
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

const ticketCategory = ref('ACTION_CREATE_CLUB') // 'ACTION_CREATE_CLUB' | 'ACTION_EVENT_GENERAL' | 'REQ_EVENT_CLUB' | 'REQ_BECOME_COORDINATOR'
const title = ref('')
const description = ref('')
const priority = ref('MEDIUM')
const selectedClubId = ref('')
const selectedClubName = ref('')
const taggedApprovers = ref([]) // Interactively managed by ApproverPicker

const clubsList = ref([])
const loading = ref(false)
const errorMessage = ref('')

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

    if (ticketCategory.value === 'ACTION_CREATE_CLUB') {
      await createActionTicket({
        ticketType: 'CREATE_CLUB',
        title: title.value,
        description: description.value,
        priority: priority.value,
        approvers: approversPayload
      })
      showToast('Action Ticket for New Club created successfully!', 'success')
    } else if (ticketCategory.value === 'ACTION_EVENT_GENERAL') {
      await createActionTicket({
        ticketType: 'CREATE_EVENT_GENERAL',
        title: title.value,
        description: description.value,
        priority: priority.value,
        approvers: approversPayload
      })
      showToast('Action Ticket for General Event created successfully!', 'success')
    } else if (ticketCategory.value === 'REQ_EVENT_CLUB') {
      if (!selectedClubId.value) {
        errorMessage.value = 'Please select a club.'
        showToast('Please select a club.', 'warning')
        loading.value = false
        return
      }
      await createRequest({
        requestType: 'CREATE_EVENT_AS_ORGANIZER',
        title: title.value,
        description: description.value,
        priority: priority.value,
        referenceType: 'CLUB',
        referenceId: parseInt(selectedClubId.value),
        referenceName: selectedClubName.value,
        approvers: approversPayload
      })
      showToast('Club Event creation request submitted successfully!', 'success')
    } else if (ticketCategory.value === 'REQ_BECOME_COORDINATOR') {
      if (!selectedClubId.value) {
        errorMessage.value = 'Please select a club.'
        showToast('Please select a club.', 'warning')
        loading.value = false
        return
      }
      await createRequest({
        requestType: 'BECOME_FACULTY_COORDINATOR',
        title: title.value,
        description: description.value,
        priority: priority.value,
        referenceType: 'CLUB',
        referenceId: parseInt(selectedClubId.value),
        referenceName: selectedClubName.value,
        approvers: approversPayload
      })
      showToast('Faculty Coordinator application submitted successfully!', 'success')
    }

    emit('submit')
    emit('close')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to submit ticket.'
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
          <h4 class="fw-bold mb-0">Raise Faculty Request / Action Ticket</h4>
          <button class="btn-close-custom" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        </div>

        <!-- Body -->
        <div class="modal-body-custom">
          
          <!-- Category Selector -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Select Request / Ticket Purpose</label>
            <select v-model="ticketCategory" class="form-select custom-input">
              <option value="ACTION_CREATE_CLUB">Action Ticket: Propose New Club Creation</option>
              <option value="ACTION_EVENT_GENERAL">Action Ticket: Propose General / Non-Club Event</option>
              <option value="REQ_EVENT_CLUB">Request: Create Club Event (As Coordinator/Organizer)</option>
              <option value="REQ_BECOME_COORDINATOR">Request: Become Faculty Coordinator for a Club</option>
            </select>
          </div>

          <!-- Title -->
          <div class="mb-3">
            <label class="form-label text-sm fw-bold">Title / Subject</label>
            <input v-model="title" type="text" class="form-control custom-input" placeholder="e.g. AI & Robotics Club Proposal" />
          </div>

          <!-- Reference Club (if needed) -->
          <div class="mb-3" v-if="ticketCategory === 'REQ_EVENT_CLUB' || ticketCategory === 'REQ_BECOME_COORDINATOR'">
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
            <label class="form-label text-sm fw-bold">Detailed Description / Justification</label>
            <textarea v-model="description" class="form-control custom-input" rows="3" placeholder="Provide background details and justification..."></textarea>
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
          <button class="btn btn-primary font-semibold rounded-pill px-4" :disabled="loading" @click="handleSubmit">
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