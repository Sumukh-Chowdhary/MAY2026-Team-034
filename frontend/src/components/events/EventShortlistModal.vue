<script setup>
import { ref, computed, watch } from 'vue'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import { shortlistSessionParticipants } from '@/api/events'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  show: Boolean,
  eventId: Number,
  session: Object,
  participants: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'completed'])
const { showToast } = useToast()

const selectedUserIds = ref(new Set())
const eliminationReason = ref('Not shortlisted')
const showConfirmStep = ref(false)
const submitting = ref(false)

watch(() => props.show, (newVal) => {
  if (newVal) {
    // Pre-select participants who are present or already shortlisted
    const initialSelected = new Set()
    props.participants.forEach(p => {
      if (p.status === 'PRESENT' || p.competitionStatus === 'SHORTLISTED') {
        initialSelected.add(p.userId)
      }
    })
    selectedUserIds.value = initialSelected
    showConfirmStep.value = false
  }
})

const totalParticipantsCount = computed(() => props.participants.length)
const selectedCount = computed(() => selectedUserIds.value.size)
const eliminatedCount = computed(() => Math.max(0, totalParticipantsCount.value - selectedCount.value))

function toggleSelectAll() {
  if (selectedUserIds.value.size === props.participants.length) {
    selectedUserIds.value.clear()
  } else {
    selectedUserIds.value = new Set(props.participants.map(p => p.userId))
  }
}

function toggleUser(userId) {
  const s = new Set(selectedUserIds.value)
  if (s.has(userId)) {
    s.delete(userId)
  } else {
    s.add(userId)
  }
  selectedUserIds.value = s
}

async function handleConfirmShortlist() {
  if (!props.eventId || !props.session) return
  submitting.value = true
  try {
    const payload = {
      selectedUserIds: Array.from(selectedUserIds.value),
      reason: eliminationReason.value.trim() || 'Not shortlisted'
    }
    const res = await shortlistSessionParticipants(props.eventId, props.session.id, payload)
    showToast(res.message || 'Round completed and participants shortlisted!', 'success')
    emit('completed', res.data)
    emit('close')
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to complete shortlisting.', 'error')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
    
    <!-- STEP 1: Participant Selection -->
    <div v-if="!showConfirmStep" class="modal-card-custom bg-white p-4 rounded-4 shadow-lg" style="max-width: 650px; width: 95%; max-height: 90vh; display: flex; flex-direction: column;">
      
      <div class="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
        <div>
          <span class="badge bg-primary-subtle text-primary rounded-pill text-xs fw-bold px-2 py-1 mb-1 d-inline-block">
            ROUND {{ session?.roundNumber || 1 }} SHORTLISTING
          </span>
          <h5 class="fw-bold text-dark mb-0">Shortlist Participants for {{ session?.name }}</h5>
        </div>
        <button class="btn-close" @click="$emit('close')"></button>
      </div>

      <div class="d-flex align-items-center justify-content-between mb-3 bg-light p-3 rounded-3 border">
        <div class="d-flex align-items-center gap-3">
          <span class="badge bg-primary rounded-pill text-sm px-3 py-2">
            Selected: <strong>{{ selectedCount }}</strong> / {{ totalParticipantsCount }}
          </span>
          <small class="text-muted text-xs">
            Unselected participants will be marked as <strong>ELIMINATED</strong>.
          </small>
        </div>
        <button class="btn btn-sm btn-outline-secondary rounded-pill text-xs fw-semibold" @click="toggleSelectAll">
          {{ selectedUserIds.size === participants.length ? 'Deselect All' : 'Select All' }}
        </button>
      </div>

      <div class="table-responsive flex-grow-1 overflow-auto pe-1 mb-3" style="max-height: 380px;">
        <table class="table table-hover align-middle text-sm mb-0">
          <thead class="table-light sticky-top text-xs text-uppercase text-secondary">
            <tr>
              <th style="width: 40px;" class="text-center">Select</th>
              <th>Participant</th>
              <th>Register No.</th>
              <th>Attendance</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="p in participants" 
              :key="p.userId" 
              class="cursor-pointer"
              :class="selectedUserIds.has(p.userId) ? 'table-success-subtle' : ''"
              @click="toggleUser(p.userId)"
            >
              <td class="text-center" @click.stop>
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  :checked="selectedUserIds.has(p.userId)" 
                  @change="toggleUser(p.userId)"
                />
              </td>
              <td>
                <div class="d-flex align-items-center gap-2">
                  <UserAvatar :name="p.userName" :size="32" />
                  <div>
                    <h6 class="fw-bold text-dark mb-0 text-sm">{{ p.userName }}</h6>
                    <small class="text-muted text-xs">{{ p.userEmail }}</small>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge bg-light text-dark border font-monospace text-xs">{{ p.registerNumber }}</span>
              </td>
              <td>
                <span 
                  class="badge text-xs px-2 py-1 rounded-pill"
                  :class="p.status === 'PRESENT' ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-danger-subtle text-danger border border-danger-subtle'"
                >
                  {{ p.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="d-flex align-items-center justify-content-between pt-3 border-top">
        <button class="btn btn-secondary rounded-pill px-4 text-xs" @click="$emit('close')">Cancel</button>
        <button 
          class="btn btn-primary rounded-pill px-4 text-xs fw-bold" 
          :disabled="selectedCount === 0"
          @click="showConfirmStep = true"
        >
          Shortlist Selected ({{ selectedCount }}) <i class="bi bi-arrow-right ms-1"></i>
        </button>
      </div>
    </div>

    <!-- STEP 2: Confirmation Dialog -->
    <div v-else class="modal-card-custom bg-white p-4 rounded-4 shadow-lg text-center" style="max-width: 480px; width: 90%;">
      <div class="icon-circle bg-warning-subtle text-warning-emphasis mb-3 mx-auto rounded-circle d-flex align-items-center justify-content-center" style="width: 60px; height: 60px; font-size: 1.8rem;">
        <i class="bi bi-exclamation-triangle-fill"></i>
      </div>

      <h5 class="fw-bold text-dark mb-2">Confirm Round Shortlisting</h5>
      <p class="text-secondary text-sm mb-4">
        <strong>{{ selectedCount }}</strong> participant(s) will advance to the next round.<br/>
        The remaining <strong>{{ eliminatedCount }}</strong> eligible participant(s) will be marked <strong>ELIMINATED</strong>.
      </p>

      <div class="mb-4 text-start">
        <label class="form-label text-xs fw-bold text-muted">Elimination Reason (Optional)</label>
        <input 
          v-model="eliminationReason" 
          type="text" 
          class="form-control rounded-3 text-sm" 
          placeholder="e.g. Not shortlisted in Round 1 cut-off"
        />
      </div>

      <div class="d-flex justify-content-center gap-3">
        <button class="btn btn-outline-secondary rounded-pill px-4 text-xs" @click="showConfirmStep = false">
          Back
        </button>
        <button 
          class="btn btn-success rounded-pill px-4 text-xs fw-bold shadow-sm d-flex align-items-center gap-2" 
          :disabled="submitting"
          @click="handleConfirmShortlist"
        >
          <i v-if="submitting" class="spinner-border spinner-border-sm"></i>
          <i v-else class="bi bi-check-circle-fill"></i>
          Confirm & Complete Round
        </button>
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
.table-success-subtle {
  background-color: #f0fdf4 !important;
}
</style>
