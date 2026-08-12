<template>
  <div
    v-if="show"
    class="modal fade show d-block"
    tabindex="-1"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">

        <div class="modal-header">
          <h5 class="modal-title">
            Request Details
          </h5>

          <button
            class="btn-close"
            @click="emit('close')"
          />
        </div>

        <div class="modal-body">

          <!-- General Information -->

          <div class="row g-3">

            <div class="col-md-6">
              <label class="form-label">Title</label>
              <div class="detail-box">
                {{ request.title }}
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Request Type</label>
              <div class="detail-box">
                {{ format(request.request_type) }}
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Reference</label>
              <div class="detail-box">
                {{ request.reference_name || "-" }}
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Priority</label>
              <div class="detail-box">
                {{ request.priority }}
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Status</label>

              <StatusBadge
                :status="request.workflow_status"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Raised By</label>

              <div class="detail-box">
                {{ request.requester_name || "-" }}
              </div>
            </div>

            <div v-if="parsedVenuePayload" class="col-12">
              <label class="form-label text-primary font-bold">Requested Venue Information</label>
              <div class="p-3 bg-light border border-primary-subtle rounded-3">
                <div class="row g-2 text-xs">
                  <div class="col-md-6"><strong>Venue:</strong> {{ parsedVenuePayload.venueName }}</div>
                  <div class="col-md-6"><strong>Requested Date:</strong> {{ parsedVenuePayload.date }}</div>
                  <div class="col-md-6"><strong>Time Slot:</strong> {{ parsedVenuePayload.startTime }} - {{ parsedVenuePayload.endTime }}</div>
                  <div v-if="parsedVenuePayload.reason" class="col-12 mt-1"><strong>Reason / Notes:</strong> {{ parsedVenuePayload.reason }}</div>
                </div>
              </div>
            </div>

            <div class="col-12">
              <label class="form-label">
                Description
              </label>

              <div class="detail-box description">
                {{ request.description || "No description." }}
              </div>
            </div>

          </div>

          <hr>

          <h6 class="mb-3">
            Approval Workflow
          </h6>

          <ApprovalTimeline
            :approvals="approvals"
          />

          <div
            v-if="canApprove"
            class="mt-4"
          >

            <label class="form-label">
              Remarks
            </label>

            <textarea
              v-model="remarks"
              rows="4"
              class="form-control"
              placeholder="Optional remarks..."
            />

          </div>

        </div>

        <div class="modal-footer">

          <button
            class="btn btn-secondary"
            @click="emit('close')"
          >
            Close
          </button>

          <template v-if="canApprove">

            <button
              class="btn btn-warning"
              @click="emit('requestChanges', remarks)"
            >
              Request Changes
            </button>

            <button
              class="btn btn-danger"
              @click="emit('reject', remarks)"
            >
              Reject
            </button>

            <button
              class="btn btn-success"
              @click="emit('approve')"
            >
              Approve
            </button>

          </template>

        </div>

      </div>
    </div>
  </div>

  <div
    v-if="show"
    class="modal-backdrop fade show"
  />
</template>

<script setup>
import { ref, computed } from "vue"

import StatusBadge from "./StatusBadge.vue"
import ApprovalTimeline from "./ApprovalTimeline.vue"

const props = defineProps({
  show: Boolean,
  request: Object,
  approvals: {
    type: Array,
    default: () => []
  },
  canApprove: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  "close",
  "approve",
  "reject",
  "requestChanges"
])

const remarks = ref("")

const parsedVenuePayload = computed(() => {
  if (!props.request || (props.request.request_type !== 'VENUE_REQUEST' && props.request.requestType !== 'VENUE_REQUEST')) return null
  try {
    const desc = props.request.description || ''
    if (desc.startsWith('{')) {
      return JSON.parse(desc)
    }
  } catch (e) {
    return null
  }
  return null
})

const format = value => {
  if (!value) return "-"
  const mapping = {
    'CREATE_EVENT_AS_ORGANIZER': 'Create Club Event',
    'EDIT_EVENT_AS_ORGANIZER': 'Edit Event Request',
    'BECOME_ORGANIZER': 'Club Organizer Application',
    'BECOME_VOLUNTEER': 'Volunteer Application',
    'EDIT_CLUB_AS_COORDINATOR': 'Update Club Info',
    'BECOME_FACULTY_COORDINATOR': 'Faculty Coordinator Request',
    'VENUE_REQUEST': 'Venue Reservation Request',
    'BUDGET_REQUEST': 'Budget Approval Request',
    'SCHEDULE_REQUEST': 'Schedule Request'
  }
  return mapping[value] || value.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, c => c.toUpperCase())
}
</script>

<style scoped>

.detail-box{
    padding:12px;
    background:#f8f9fa;
    border-radius:8px;
}

.description{
    min-height:110px;
    white-space:pre-wrap;
}

</style>