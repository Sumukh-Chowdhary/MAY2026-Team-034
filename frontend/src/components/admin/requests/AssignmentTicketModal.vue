<script setup>
import { ref, computed, watch } from 'vue'
import { updateAssignmentTicket } from '@/api/assignmentTickets'
import UserProfileModal from '@/components/common/UserProfileModal.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  ticket: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

const actionType = ref('SUSPEND')
const remarks = ref('')
const durationType = ref('INDEFINITE')
const endsAt = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// User Profile Quick View Modal State
const showProfileModal = ref(false)

watch(() => props.ticket, (newVal) => {
  if (newVal) {
    durationType.value = newVal.durationType || 'INDEFINITE'
    endsAt.value = newVal.endsAt ? newVal.endsAt.split('T')[0] : ''
    remarks.value = ''
    errorMessage.value = ''
    successMessage.value = ''
    
    // Set default action depending on current status
    if (newVal.status === 'ACTIVE') actionType.value = 'SUSPEND'
    else if (newVal.status === 'SUSPENDED') actionType.value = 'REACTIVATE'
    else actionType.value = 'EDIT_DURATION'
  }
})

const holderName = computed(() => {
  if (!props.ticket) return 'N/A'
  return props.ticket.holder?.name || props.ticket.holder?.fullName || ('User #' + props.ticket.holderId)
})

const roleName = computed(() => (props.ticket?.assignmentRole || 'MEMBER').replace('_', ' '))
const referenceName = computed(() => props.ticket?.referenceName || ('#' + props.ticket?.referenceId))

const statusBadgeClass = computed(() => {
  switch (props.ticket?.status) {
    case 'ACTIVE': return 'badge-active'
    case 'SUSPENDED': return 'badge-suspended'
    case 'TERMINATED': return 'badge-terminated'
    case 'EXPIRED': return 'badge-expired'
    default: return 'badge-secondary'
  }
})

async function handleActionSubmit() {
  if (!props.ticket) return
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const payload = {
      action: actionType.value,
      remarks: remarks.value
    }

    if (actionType.value === 'EDIT_DURATION') {
      payload.durationType = durationType.value
      if (durationType.value === 'DATE_RANGE') {
        if (!endsAt.value) {
          errorMessage.value = 'Please specify an end date for date-range duration.'
          loading.value = false
          return
        }
        payload.endsAt = new Date(endsAt.value).toISOString()
      }
    }

    const res = await updateAssignmentTicket(props.ticket.id, payload)
    successMessage.value = res.message || 'Assignment updated successfully!'
    setTimeout(() => {
      emit('updated')
      emit('close')
    }, 800)
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Failed to update assignment ticket.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="glass-modal-overlay" @click.self="$emit('close')">
      <div class="glass-modal-container shadow-2xl">
        
        <!-- Header -->
        <div class="glass-modal-header">
          <div>
            <h4 class="modal-title-text">Manage Live Role Assignment</h4>
            <small class="text-slate-500">Ticket #{{ ticket?.id }} - {{ roleName }}</small>
          </div>
          <button class="btn-glass-close" @click="$emit('close')">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Body -->
        <div class="glass-modal-body" v-if="ticket">
          
          <!-- Assignment Ticket Meta Box -->
          <div class="assignment-meta-box mb-4">
            <div class="row g-3">
              <div class="col-md-6">
                <span class="meta-label">Role Holder</span>
                <div class="d-flex align-items-center justify-content-between">
                  <p class="meta-val fw-bold text-primary mb-0">
                    <i class="bi bi-person-circle me-1"></i> {{ holderName }}
                  </p>
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-primary rounded-pill px-2 py-0 text-xs"
                    @click="showProfileModal = true"
                  >
                    <i class="bi bi-person-badge me-1"></i> View Profile
                  </button>
                </div>
              </div>

              <div class="col-md-6">
                <span class="meta-label">Current Status</span>
                <span class="status-pill" :class="statusBadgeClass">
                  {{ ticket.status }}
                </span>
              </div>

              <div class="col-md-6">
                <span class="meta-label">Reference</span>
                <p class="meta-val text-dark">
                  {{ ticket.referenceType || 'CLUB' }}: <strong>{{ referenceName }}</strong>
                </p>
              </div>

              <div class="col-md-6">
                <span class="meta-label">Duration</span>
                <p class="meta-val">
                  <span class="badge bg-light text-dark me-1">{{ ticket.durationType }}</span>
                  <small v-if="ticket.endsAt" class="text-muted">Ends: {{ new Date(ticket.endsAt).toLocaleDateString() }}</small>
                </p>
              </div>
            </div>
          </div>

          <!-- Action Type Selector with Distinct Color Coding -->
          <div class="mb-3">
            <label class="form-label font-semibold text-slate-700">Select Admin Action</label>
            <div class="action-btn-group">
              
              <!-- Suspend Action (Amber/Warning) -->
              <button 
                v-if="ticket.status === 'ACTIVE'"
                type="button" 
                class="action-btn action-btn-warning"
                :class="{ active: actionType === 'SUSPEND' }"
                @click="actionType = 'SUSPEND'"
              >
                <i class="bi bi-pause-circle me-1"></i> Suspend
              </button>

              <!-- Reactivate Action (Green/Success) -->
              <button 
                v-if="ticket.status === 'SUSPENDED'"
                type="button" 
                class="action-btn action-btn-success"
                :class="{ active: actionType === 'REACTIVATE' }"
                @click="actionType = 'REACTIVATE'"
              >
                <i class="bi bi-play-circle me-1"></i> Reactivate
              </button>

              <!-- Terminate Action (Red/Danger) -->
              <button 
                type="button" 
                class="action-btn action-btn-danger"
                :class="{ active: actionType === 'TERMINATE' }"
                @click="actionType = 'TERMINATE'"
              >
                <i class="bi bi-x-circle me-1"></i> Terminate
              </button>

              <!-- Edit Duration Action (Blue/Primary) -->
              <button 
                type="button" 
                class="action-btn action-btn-primary"
                :class="{ active: actionType === 'EDIT_DURATION' }"
                @click="actionType = 'EDIT_DURATION'"
              >
                <i class="bi bi-calendar-event me-1"></i> Edit Duration
              </button>

            </div>
          </div>

          <!-- Duration Fields if EDIT_DURATION selected -->
          <div v-if="actionType === 'EDIT_DURATION'" class="p-3 mb-3 edit-duration-box">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label text-sm fw-medium">Duration Type</label>
                <select v-model="durationType" class="form-select glass-input">
                  <option value="INDEFINITE">Indefinite (No End Date)</option>
                  <option value="DATE_RANGE">Date Range (Set End Date)</option>
                </select>
              </div>
              <div class="col-md-6" v-if="durationType === 'DATE_RANGE'">
                <label class="form-label text-sm fw-medium">Expiration End Date</label>
                <input v-model="endsAt" type="date" class="form-control glass-input" />
              </div>
            </div>
          </div>

          <!-- Remarks -->
          <div class="mb-3">
            <label class="form-label text-sm fw-medium">Admin Remarks / Justification</label>
            <textarea 
              v-model="remarks" 
              class="form-control glass-input" 
              rows="3" 
              placeholder="Provide reason for this assignment status change..."
            ></textarea>
          </div>

          <!-- Alerts -->
          <div v-if="errorMessage" class="alert alert-danger-glass mb-3">
            <i class="bi bi-exclamation-triangle-fill me-2"></i> {{ errorMessage }}
          </div>
          <div v-if="successMessage" class="alert alert-success-glass mb-3">
            <i class="bi bi-check-circle-fill me-2"></i> {{ successMessage }}
          </div>

        </div>

        <!-- Footer -->
        <div class="glass-modal-footer">
          <button class="btn btn-glass-secondary me-2" @click="$emit('close')">
            Cancel
          </button>
          <button 
            class="btn font-semibold rounded-pill px-4" 
            :class="actionType === 'TERMINATE' ? 'btn-danger' : (actionType === 'SUSPEND' ? 'btn-warning text-dark' : 'btn-primary')"
            :disabled="loading" 
            @click="handleActionSubmit"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Apply Action
          </button>
        </div>

      </div>
    </div>
  </Teleport>

  <!-- User Profile Quick View Modal -->
  <UserProfileModal 
    :show="showProfileModal"
    :userId="ticket?.holderId"
    @close="showProfileModal = false"
  />
</template>

<style scoped>
.glass-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1055;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.glass-modal-container {
  width: 100%;
  max-width: 650px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 24px;
  overflow: hidden;
}

.glass-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.btn-glass-close {
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

.glass-modal-body {
  padding: 1.5rem;
}

.assignment-meta-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1rem;
}

.meta-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.meta-val {
  font-size: 0.9rem;
  margin: 0;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
}

.badge-active { background: #d1fae5; color: #065f46; }
.badge-suspended { background: #fef3c7; color: #92400e; }
.badge-terminated { background: #fee2e2; color: #991b1b; }
.badge-expired { background: #e2e8f0; color: #475569; }

.action-btn-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-btn {
  flex: 1;
  min-width: 120px;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  background: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Distinct Action Colors */
.action-btn-warning { color: #d97706; border-color: #fde68a; }
.action-btn-warning.active, .action-btn-warning:hover { background: #f59e0b; color: white; border-color: #f59e0b; }

.action-btn-danger { color: #dc2626; border-color: #fca5a5; }
.action-btn-danger.active, .action-btn-danger:hover { background: #ef4444; color: white; border-color: #ef4444; }

.action-btn-primary { color: #2563eb; border-color: #bfdbfe; }
.action-btn-primary.active, .action-btn-primary:hover { background: #2563eb; color: white; border-color: #2563eb; }

.action-btn-success { color: #16a34a; border-color: #bbf7d0; }
.action-btn-success.active, .action-btn-success:hover { background: #10b981; color: white; border-color: #10b981; }

.edit-duration-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 14px;
}

.glass-input {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
}

.alert-danger-glass { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; border-radius: 12px; padding: 10px 14px; }
.alert-success-glass { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 14px; }

.glass-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}

.btn-glass-secondary { background: #e2e8f0; color: #334155; border: none; border-radius: 10px; padding: 8px 18px; font-weight: 600; }
</style>
