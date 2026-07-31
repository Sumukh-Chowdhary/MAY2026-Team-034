<script setup>
import { ref, computed, watch } from 'vue'
import UserProfileModal from '@/components/common/UserProfileModal.vue'
import { approveRequest, rejectRequest, requestChanges, resubmitRequest } from '@/api/requests'
import { approveActionTicket, rejectActionTicket, requestChangesActionTicket, updateTaskStatus, resubmitActionTicket } from '@/api/actionTickets'
import ApproverPicker from '@/components/common/ApproverPicker.vue'
import { useToast } from '@/composables/useToast'

const showProfileModal = ref(false)
const selectedProfileUserId = ref(null)

function openUserProfile(id) {
  if (!id) return
  selectedProfileUserId.value = id
  showProfileModal.value = true
}

const { showToast } = useToast()

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  item: {
    type: Object,
    default: null
  },
  currentUserRole: {
    type: String,
    default: ''
  },
  currentUserId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close', 'updated'])

// Reactive states
const remarks = ref('')
const actionLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Resubmit Form State
const resubmitMode = ref(false)
const editTitle = ref('')
const editDescription = ref('')
const editPriority = ref('MEDIUM')
const editApprovers = ref([])

watch(() => props.item, (newVal) => {
  remarks.value = ''
  errorMessage.value = ''
  successMessage.value = ''
  resubmitMode.value = false
  if (newVal) {
    editTitle.value = newVal.title || newVal.subject || ''
    editDescription.value = newVal.description || ''
    editPriority.value = newVal.priority || 'MEDIUM'
    if (newVal.approvals && Array.isArray(newVal.approvals)) {
      editApprovers.value = newVal.approvals.map(a => ({
        approverId: a.approverId,
        role: a.approvalRole || 'APPROVER',
        name: a.approver?.name || 'Approver #' + a.approverId,
        email: a.approver?.email || '',
        designation: a.approver?.designation || ''
      }))
    } else {
      editApprovers.value = []
    }
  }
})

// Helper checks
const isActionTicket = computed(() => {
  if (!props.item) return false
  return 'ticketType' in props.item || 'approvalStatus' in props.item
})

const itemTitle = computed(() => props.item?.title || props.item?.subject || 'Request Details')
const itemDescription = computed(() => props.item?.description || 'No detailed description provided.')
const itemType = computed(() => props.item?.requestType || props.item?.ticketType || 'REQUEST')
const itemPriority = computed(() => (props.item?.priority || 'MEDIUM').toUpperCase())
const itemStatus = computed(() => props.item?.workflowStatus || props.item?.approvalStatus || props.item?.status || 'PENDING')
const itemVersion = computed(() => props.item?.version || 1)
const isRequester = computed(() => {
  if (!props.item || !props.currentUserId) return false
  const reqId = props.item.requesterId || props.item.raisedById
  return String(reqId) === String(props.currentUserId)
})

const createdAt = computed(() => {
  if (!props.item?.createdAt && !props.item?.date) return 'N/A'
  const val = props.item.createdAt || props.item.date
  return new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
})

// Tagged Approvers list
const approvalsList = computed(() => {
  if (!props.item) return []
  if (props.item.approvals && Array.isArray(props.item.approvals)) {
    return props.item.approvals
  }
  return []
})

// Current user approval step check
const myPendingApproval = computed(() => {
  if (!approvalsList.value.length || !props.currentUserId) return null
  return approvalsList.value.find(
    a => String(a.approverId) === String(props.currentUserId) && a.status === 'PENDING'
  ) || null
})

// Task status execution check (for ActionTickets)
const isTaskAssignedToMe = computed(() => {
  if (!isActionTicket.value || !props.item) return false
  if (itemStatus.value !== 'APPROVED') return false
  if (props.currentUserRole === 'ADMIN') return true
  return String(props.item.assignedToId) === String(props.currentUserId)
})

const taskStatus = computed(() => props.item?.taskStatus || 'OPEN')

// Status Badge Styling
function priorityBadgeClass(priority) {
  switch (priority) {
    case 'HIGH': return 'badge-priority-high'
    case 'MEDIUM': return 'badge-priority-medium'
    case 'LOW': return 'badge-priority-low'
    default: return 'badge-secondary'
  }
}

function statusBadgeClass(status) {
  switch (status) {
    case 'APPROVED':
    case 'COMPLETED':
    case 'ACTIVE':
      return 'badge-status-approved'
    case 'REJECTED':
    case 'TERMINATED':
      return 'badge-status-rejected'
    case 'IN_PROGRESS':
    case 'CHANGES_REQUESTED':
      return 'badge-status-warning'
    case 'PENDING':
    case 'OPEN':
      return 'badge-status-pending'
    default:
      return 'badge-secondary'
  }
}

function roleBadgeClass(role) {
  if (!role) return 'bg-slate'
  if (role.includes('FACULTY')) return 'role-tag-faculty'
  if (role.includes('ADMIN')) return 'role-tag-admin'
  if (role.includes('PRINCIPAL') || role.includes('DEAN')) return 'role-tag-executive'
  return 'role-tag-default'
}

// Approval Actions
async function handleApprove() {
  actionLoading.value = true
  errorMessage.value = ''
  try {
    if (isActionTicket.value) {
      await approveActionTicket(props.item.id)
    } else {
      await approveRequest(props.item.id, remarks.value)
    }
    showToast('Request approved successfully!', 'success')
    emit('updated')
    emit('close')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to approve request.'
    errorMessage.value = msg
    showToast(msg, 'error')
  } finally {
    actionLoading.value = false
  }
}

async function handleReject() {
  if (!remarks.value.trim()) {
    errorMessage.value = 'Please provide remarks explaining the rejection.'
    showToast('Please provide remarks explaining the rejection.', 'warning')
    return
  }
  actionLoading.value = true
  errorMessage.value = ''
  try {
    if (isActionTicket.value) {
      await rejectActionTicket(props.item.id, remarks.value)
    } else {
      await rejectRequest(props.item.id, remarks.value)
    }
    showToast('Request rejected.', 'info')
    emit('updated')
    emit('close')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to reject request.'
    errorMessage.value = msg
    showToast(msg, 'error')
  } finally {
    actionLoading.value = false
  }
}

async function handleRequestChanges() {
  if (!remarks.value.trim()) {
    errorMessage.value = 'Please specify the changes required.'
    showToast('Please specify the changes required.', 'warning')
    return
  }
  actionLoading.value = true
  errorMessage.value = ''
  try {
    if (isActionTicket.value) {
      await requestChangesActionTicket(props.item.id, remarks.value)
    } else {
      await requestChanges(props.item.id, remarks.value)
    }
    showToast('Changes requested from requester.', 'warning')
    emit('updated')
    emit('close')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to request changes.'
    errorMessage.value = msg
    showToast(msg, 'error')
  } finally {
    actionLoading.value = false
  }
}

async function handleResubmitSubmit() {
  if (!editTitle.value.trim()) {
    errorMessage.value = 'Title is required.'
    showToast('Title is required.', 'warning')
    return
  }
  actionLoading.value = true
  errorMessage.value = ''
  try {
    const approversPayload = editApprovers.value.map(a => ({
      approverId: a.approverId || a.id,
      role: a.role || 'APPROVER'
    }))

    const payload = {
      title: editTitle.value,
      description: editDescription.value,
      priority: editPriority.value,
      approvers: approversPayload
    }
    if (isActionTicket.value) {
      await resubmitActionTicket(props.item.id, payload)
    } else {
      await resubmitRequest(props.item.id, payload)
    }
    showToast(`Request resubmitted successfully! Version updated to v${itemVersion.value + 1}.`, 'success')
    emit('updated')
    emit('close')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to resubmit.'
    errorMessage.value = msg
    showToast(msg, 'error')
  } finally {
    actionLoading.value = false
  }
}

// Task execution actions
async function handleTaskAction(actionType) {
  actionLoading.value = true
  errorMessage.value = ''
  try {
    await updateTaskStatus(props.item.id, actionType, remarks.value)
    successMessage.value = `Task marked as ${actionType === 'START' ? 'In Progress' : 'Completed'}.`
    setTimeout(() => {
      emit('updated')
      emit('close')
    }, 800)
  } catch (err) {
    errorMessage.value = err.response?.data?.error || 'Failed to update task status.'
  } finally {
    actionLoading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="glass-modal-overlay" @click.self="$emit('close')">
      <div class="glass-modal-container shadow-2xl">
        
        <!-- Header -->
        <div class="glass-modal-header">
          <div class="header-left">
            <div class="title-row">
              <h3 class="modal-title-text">{{ itemTitle }}</h3>
              <span class="version-pill">v{{ itemVersion }}</span>
              <span class="badge-pill" :class="statusBadgeClass(itemStatus)">
                {{ itemStatus.replace('_', ' ') }}
              </span>
            </div>
            <div class="meta-row">
              <span class="meta-item">
                <i class="bi bi-tag-fill me-1 text-primary"></i>
                <strong>Type:</strong> {{ itemType }}
              </span>
              <span class="meta-item">
                <i class="bi bi-flag-fill me-1"></i>
                <span class="badge-priority" :class="priorityBadgeClass(itemPriority)">
                  {{ itemPriority }} Priority
                </span>
              </span>
              <span class="meta-item">
                <i class="bi bi-calendar3 me-1 text-secondary"></i>
                {{ createdAt }}
              </span>
            </div>
          </div>
          <button class="btn-glass-close" @click="$emit('close')" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Body -->
        <div class="glass-modal-body">
          
          <!-- Resubmit Edit Mode with Interactive ApproverPicker -->
          <div v-if="resubmitMode" class="resubmit-form-card mb-4 p-3 border rounded-3 bg-light">
            <h5 class="fw-bold text-primary mb-3">
              <i class="bi bi-pencil-square me-1"></i> Edit & Resubmit Request (Version Upgrade to v{{ itemVersion + 1 }})
            </h5>
            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Title</label>
              <input v-model="editTitle" type="text" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Priority</label>
              <select v-model="editPriority" class="form-select">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label text-sm fw-bold">Description</label>
              <textarea v-model="editDescription" class="form-control" rows="3"></textarea>
            </div>

            <!-- Tagged Approvers Chain Editor -->
            <div class="mb-3">
              <ApproverPicker v-model="editApprovers" />
            </div>

            <div class="d-flex justify-content-end gap-2">
              <button class="btn btn-sm btn-secondary" @click="resubmitMode = false">Cancel</button>
              <button class="btn btn-sm btn-primary" :disabled="actionLoading" @click="handleResubmitSubmit">
                Submit Resubmission (Re-send to All Tagged Approvers)
              </button>
            </div>
          </div>

          <!-- Reference / Requester Info Card -->
          <div v-else class="info-card mb-4">
            <div class="row g-3">
              <div class="col-md-6" v-if="item?.requester || item?.raisedBy">
                <span class="info-label">Raised By</span>
                <div class="d-flex align-items-center justify-content-between">
                  <p class="info-val mb-0">
                    <i class="bi bi-person-circle me-1 text-primary"></i>
                    {{ item.requester?.name || item.raisedBy?.name || 'User #' + (item.requesterId || item.raisedById) }}
                    <small v-if="item.requester?.email" class="text-muted d-block">{{ item.requester.email }}</small>
                  </p>
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-primary rounded-pill px-3 py-1 text-xs" 
                    @click="openUserProfile(item.requesterId || item.raisedById)"
                  >
                    <i class="bi bi-person-badge me-1"></i> View Profile
                  </button>
                </div>
              </div>
              <div class="col-md-6" v-if="item?.referenceName">
                <span class="info-label">Reference</span>
                <p class="info-val">
                  <i class="bi bi-building me-1 text-indigo-500"></i>
                  {{ item.referenceType || 'CLUB' }}: <strong>{{ item.referenceName }}</strong>
                </p>
              </div>
              <div class="col-12">
                <span class="info-label">Description</span>
                <p class="description-text">{{ itemDescription }}</p>
              </div>
            </div>
          </div>

          <!-- Tagged People / Horizontal Scroll Approvers Chain -->
          <div class="approvers-section mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h5 class="section-heading mb-0">
                <i class="bi bi-people-fill me-2 text-primary"></i>
                Tagged Approvers & Workflow Chain
              </h5>
              <span class="text-xs text-slate-500" v-if="approvalsList.length > 0">
                Scroll horizontally <i class="bi bi-arrow-right me-1"></i>
              </span>
            </div>

            <div v-if="approvalsList.length === 0" class="empty-approvers-box">
              <i class="bi bi-info-circle me-2"></i> No individual approvers tagged for this request.
            </div>

            <!-- Horizontal Scroll Container -->
            <div v-else class="horizontal-scroll-chain">
              <div 
                v-for="(appr, index) in approvalsList" 
                :key="appr.id || index"
                class="approver-card-wrapper"
              >
                <div v-if="index > 0" class="step-connector">
                  <i class="bi bi-chevron-right"></i>
                </div>

                <div class="approver-glass-card shadow-sm" :class="{ 'card-active-step': appr.status === 'PENDING' }">
                  <div class="approver-card-header">
                    <span class="step-badge">Step {{ appr.approvalOrder || index + 1 }}</span>
                    <span class="role-badge" :class="roleBadgeClass(appr.approvalRole)">
                      {{ (appr.approvalRole || 'APPROVER').replace('_', ' ') }}
                    </span>
                  </div>

                  <div class="approver-user-info">
                    <div class="user-avatar">
                      {{ (appr.approver?.name || 'A').charAt(0).toUpperCase() }}
                    </div>
                    <div class="user-details">
                      <p class="user-name mb-0">{{ appr.approver?.name || 'Approver #' + (appr.approverId || index + 1) }}</p>
                      <small class="text-muted d-block text-xs">{{ appr.approver?.designation || (appr.approvalRole ? appr.approvalRole.replace('_', ' ') : 'Faculty') }}</small>
                      <small class="text-secondary text-xs" v-if="appr.approver?.email">{{ appr.approver.email }}</small>
                    </div>
                  </div>

                  <div class="approver-status-row">
                    <span class="status-pill" :class="statusBadgeClass(appr.status)">
                      <i v-if="appr.status === 'APPROVED'" class="bi bi-check-circle-fill me-1"></i>
                      <i v-else-if="appr.status === 'REJECTED'" class="bi bi-x-circle-fill me-1"></i>
                      <i v-else-if="appr.status === 'PENDING'" class="bi bi-clock-history me-1"></i>
                      <i v-else-if="appr.status === 'CHANGES_REQUESTED'" class="bi bi-pencil-square me-1"></i>
                      {{ appr.status }}
                    </span>
                    <small v-if="appr.approvedAt" class="text-xs text-secondary ms-auto">
                      {{ new Date(appr.approvedAt).toLocaleDateString() }}
                    </small>
                  </div>

                  <!-- Vertical Scroll Remarks Box inside each Approver Card -->
                  <div class="vertical-remarks-box">
                    <span class="remarks-label">Remarks:</span>
                    <div class="remarks-scroll-content">
                      <p v-if="appr.remarks" class="remarks-text mb-0">{{ appr.remarks }}</p>
                      <span v-else class="text-muted italic-text">No remarks recorded.</span>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <!-- Alert Feedback -->
          <div v-if="errorMessage" class="alert alert-danger-glass d-flex align-items-center mb-3">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <div>{{ errorMessage }}</div>
          </div>
          <div v-if="successMessage" class="alert alert-success-glass d-flex align-items-center mb-3">
            <i class="bi bi-check-circle-fill me-2"></i>
            <div>{{ successMessage }}</div>
          </div>

          <!-- Resubmit Button for Requester when Changes Requested -->
          <div v-if="itemStatus === 'CHANGES_REQUESTED' && isRequester && !resubmitMode" class="alert alert-warning-glass d-flex justify-content-between align-items-center mb-3">
            <div>
              <i class="bi bi-exclamation-circle-fill me-2"></i>
              <strong>Changes Requested!</strong> Review feedback and edit request details or tag additional approvers.
            </div>
            <button class="btn btn-warning font-semibold btn-sm rounded-pill" @click="resubmitMode = true">
              <i class="bi bi-pencil-square me-1"></i> Edit & Resubmit
            </button>
          </div>

          <!-- Action Controls for Approver / Task Assignee -->
          <div v-if="myPendingApproval || isTaskAssignedToMe" class="action-panel-glass">
            <h6 class="action-panel-title">
              <i class="bi bi-lightning-charge-fill me-2 text-warning"></i>
              Action Required
            </h6>
            
            <div class="mb-3">
              <label class="form-label text-sm fw-medium">Add Remarks / Feedback Comments</label>
              <textarea 
                v-model="remarks" 
                class="form-control glass-input" 
                rows="2" 
                placeholder="Enter remarks or justification for your decision..."
              ></textarea>
            </div>

            <!-- Approval Controls -->
            <div v-if="myPendingApproval" class="d-flex flex-wrap gap-2 justify-content-end">
              <button 
                class="btn btn-glass-warning" 
                :disabled="actionLoading" 
                @click="handleRequestChanges"
              >
                <i class="bi bi-arrow-counterclockwise me-1"></i> Request Changes
              </button>
              <button 
                class="btn btn-glass-danger" 
                :disabled="actionLoading" 
                @click="handleReject"
              >
                <i class="bi bi-x-lg me-1"></i> Reject
              </button>
              <button 
                class="btn btn-glass-success" 
                :disabled="actionLoading" 
                @click="handleApprove"
              >
                <span v-if="actionLoading" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-check-lg me-1"></i> Approve
              </button>
            </div>

            <!-- Task Execution Controls -->
            <div v-else-if="isTaskAssignedToMe" class="d-flex flex-wrap gap-2 justify-content-end">
              <button 
                v-if="taskStatus === 'OPEN'" 
                class="btn btn-glass-primary" 
                :disabled="actionLoading" 
                @click="handleTaskAction('START')"
              >
                <i class="bi bi-play-fill me-1"></i> Start Execution
              </button>
              <button 
                v-if="taskStatus === 'IN_PROGRESS' || taskStatus === 'OPEN'" 
                class="btn btn-glass-success" 
                :disabled="actionLoading" 
                @click="handleTaskAction('COMPLETE')"
              >
                <i class="bi bi-check2-all me-1"></i> Complete & Close Ticket
              </button>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="glass-modal-footer">
          <button class="btn btn-glass-secondary" @click="$emit('close')">
            Close
          </button>
        </div>

      </div>
    </div>

    <!-- User Profile Quick View Modal -->
    <UserProfileModal 
      :show="showProfileModal"
      :userId="selectedProfileUserId"
      @close="showProfileModal = false"
    />
  </Teleport>
</template>

<style scoped>
.glass-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1050;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.glass-modal-container {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.glass-modal-header {
  padding: 1.5rem 1.75rem 1rem 1.75rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.modal-title-text {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.version-pill {
  font-size: 0.75rem;
  font-weight: 700;
  background: #3b82f6;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
}

.meta-row {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  font-size: 0.85rem;
  color: #475569;
  flex-wrap: wrap;
}

.btn-glass-close {
  background: rgba(241, 245, 249, 0.8);
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
}

.glass-modal-body {
  padding: 1.5rem 1.75rem;
  overflow-y: auto;
  flex: 1;
}

.info-card {
  background: rgba(248, 250, 252, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 16px;
  padding: 1.25rem;
}

.info-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.info-val {
  font-size: 0.95rem;
  font-weight: 500;
  color: #1e293b;
  margin: 0;
}

.description-text {
  font-size: 0.9rem;
  color: #334155;
  margin: 0;
  line-height: 1.5;
  white-space: pre-line;
}

.horizontal-scroll-chain {
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  gap: 16px;
  padding: 12px 4px 16px 4px;
  scrollbar-width: thin;
  scrollbar-color: #94a3b8 #f1f5f9;
}

.approver-card-wrapper {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.step-connector {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 1.2rem;
  padding: 0 4px;
}

.approver-glass-card {
  width: 270px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(203, 213, 225, 0.8);
  border-radius: 18px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-active-step {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

.approver-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-badge {
  font-size: 0.7rem;
  font-weight: 700;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 8px;
  border-radius: 12px;
}

.role-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
}

.role-tag-faculty { background: #dbeafe; color: #1e40af; }
.role-tag-admin { background: #fce7f3; color: #9d174d; }
.role-tag-executive { background: #fef3c7; color: #92400e; }
.role-tag-default { background: #e0e7ff; color: #3730a3; }

.approver-user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
}

.approver-status-row {
  display: flex;
  align-items: center;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}

.vertical-remarks-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px 10px;
}

.remarks-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.remarks-scroll-content {
  max-height: 90px;
  overflow-y: auto;
  scrollbar-width: thin;
}

.remarks-text {
  font-size: 0.8rem;
  color: #334155;
}

.italic-text {
  font-style: italic;
  font-size: 0.75rem;
}

.action-panel-glass {
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(203, 213, 225, 0.8);
  border-radius: 18px;
  padding: 1.25rem;
  margin-top: 1rem;
}

.glass-input {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.btn-glass-success { background: #10b981; color: white; border: none; border-radius: 10px; padding: 8px 18px; font-weight: 600; }
.btn-glass-danger { background: #ef4444; color: white; border: none; border-radius: 10px; padding: 8px 18px; font-weight: 600; }
.btn-glass-warning { background: #f59e0b; color: white; border: none; border-radius: 10px; padding: 8px 18px; font-weight: 600; }
.btn-glass-primary { background: #3b82f6; color: white; border: none; border-radius: 10px; padding: 8px 18px; font-weight: 600; }
.btn-glass-secondary { background: #e2e8f0; color: #334155; border: none; border-radius: 10px; padding: 8px 20px; font-weight: 600; }

.glass-modal-footer {
  padding: 1rem 1.75rem;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  justify-content: flex-end;
}

.badge-status-approved { background: #d1fae5; color: #065f46; }
.badge-status-rejected { background: #fee2e2; color: #991b1b; }
.badge-status-warning { background: #fef3c7; color: #92400e; }
.badge-status-pending { background: #e0f2fe; color: #075985; }

.badge-priority-high { background: #ef4444; color: white; border-radius: 8px; padding: 2px 8px; font-size: 0.75rem; font-weight: 700; }
.badge-priority-medium { background: #f59e0b; color: white; border-radius: 8px; padding: 2px 8px; font-size: 0.75rem; font-weight: 700; }
.badge-priority-low { background: #10b981; color: white; border-radius: 8px; padding: 2px 8px; font-size: 0.75rem; font-weight: 700; }

.alert-danger-glass { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; border-radius: 12px; padding: 10px 14px; }
.alert-success-glass { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 14px; }
.alert-warning-glass { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; border-radius: 12px; padding: 10px 14px; }
</style>
