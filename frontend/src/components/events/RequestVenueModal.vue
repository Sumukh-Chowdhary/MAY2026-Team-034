<script setup>
import { ref, watch, onMounted } from 'vue'
import { getVenues } from '@/api/venues'
import { createRequest } from '@/api/requests'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  show: Boolean,
  event: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'submitted'])
const { showToast } = useToast()

const loadingVenues = ref(false)
const submitting = ref(false)
const venues = ref([])

const selectedVenueId = ref('')
const requestDate = ref('')
const startTime = ref('09:00 AM')
const endTime = ref('05:00 PM')
const reason = ref('')

async function fetchVenuesList() {
  loadingVenues.value = true
  try {
    const res = await getVenues()
    venues.value = Array.isArray(res) ? res : (res.data || [])
  } catch (err) {
    showToast('Failed to load available venues.', 'error')
  } finally {
    loadingVenues.value = false
  }
}

watch(() => props.show, (val) => {
  if (val && props.event) {
    selectedVenueId.value = props.event.venueId || ''
    requestDate.value = props.event.startDate || props.event.start_date || ''
    startTime.value = props.event.startTime || '09:00 AM'
    endTime.value = props.event.endTime || '05:00 PM'
    reason.value = ''
    fetchVenuesList()
  }
})

onMounted(() => {
  if (props.show && props.event) {
    fetchVenuesList()
  }
})

async function handleSubmitRequest() {
  if (!selectedVenueId.value) {
    showToast('Please select a venue.', 'warning')
    return
  }
  if (!props.event?.id) return

  submitting.value = true
  try {
    const targetVenue = venues.value.find(v => v.id === Number(selectedVenueId.value))
    const venueName = targetVenue ? targetVenue.name : 'Selected Venue'

    const payloadDesc = JSON.stringify({
      venueId: Number(selectedVenueId.value),
      venueName: venueName,
      date: requestDate.value,
      startTime: startTime.value,
      endTime: endTime.value,
      reason: reason.value.trim()
    })

    const payload = {
      title: `Venue Request: ${venueName} for ${props.event.name}`,
      description: payloadDesc,
      requestType: 'VENUE_REQUEST',
      priority: 'MEDIUM',
      referenceType: 'EVENT',
      referenceId: props.event.id,
      referenceName: props.event.name
    }

    await createRequest(payload)
    showToast('Venue request submitted for admin approval!', 'success')
    emit('submitted')
    emit('close')
  } catch (err) {
    showToast(err.response?.data?.error || 'Failed to submit venue request.', 'error')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-backdrop-custom d-flex align-items-center justify-content-center" @mousedown.self="$emit('close')">
    <div class="modal-card-custom bg-white p-4 rounded-4 shadow-lg" style="max-width: 480px; width: 90%;">
      
      <div class="d-flex align-items-center justify-content-between border-bottom pb-3 mb-3">
        <div>
          <h5 class="fw-bold text-dark mb-0">
            <i class="bi bi-geo-alt-fill text-primary me-2"></i>
            {{ event?.venueId ? 'Request Venue Change' : 'Request Venue' }}
          </h5>
          <small class="text-muted text-xs">{{ event?.name }}</small>
        </div>
        <button class="btn-close" @click="$emit('close')"></button>
      </div>

      <div class="mb-3">
        <label class="form-label text-xs fw-bold text-slate-700">Select Venue</label>
        <select v-model="selectedVenueId" class="form-select rounded-3 text-sm" :disabled="loadingVenues">
          <option value="">Choose a venue</option>
          <option v-for="v in venues" :key="v.id" :value="v.id">
            {{ v.name }} — {{ v.location }} (Cap: {{ v.capacity || 'N/A' }})
          </option>
        </select>
        <span v-if="loadingVenues" class="text-xs text-muted mt-1 d-block">Loading venues...</span>
      </div>

      <div class="mb-3">
        <label class="form-label text-xs fw-bold text-slate-700">Requested Date</label>
        <input v-model="requestDate" type="date" class="form-control rounded-3 text-sm" />
      </div>

      <div class="row g-2 mb-3">
        <div class="col-6">
          <label class="form-label text-xs fw-bold text-slate-700">Start Time</label>
          <input v-model="startTime" type="text" class="form-control rounded-3 text-sm" placeholder="09:00 AM" />
        </div>
        <div class="col-6">
          <label class="form-label text-xs fw-bold text-slate-700">End Time</label>
          <input v-model="endTime" type="text" class="form-control rounded-3 text-sm" placeholder="05:00 PM" />
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label text-xs fw-bold text-slate-700">Reason / Notes (Optional)</label>
        <textarea v-model="reason" class="form-control rounded-3 text-sm" rows="3" placeholder="Explain why this venue is required for the event..."></textarea>
      </div>

      <div class="d-flex justify-content-end gap-2 pt-3 border-top">
        <button class="btn btn-secondary rounded-3 px-3 text-xs" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary rounded-3 px-4 text-xs fw-bold" :disabled="submitting" @click="handleSubmitRequest">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
          Submit Venue Request
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
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  z-index: 1060;
}
</style>
