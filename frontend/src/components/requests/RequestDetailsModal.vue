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
import { ref } from "vue"

import StatusBadge from "./StatusBadge.vue"
import ApprovalTimeline from "./ApprovalTimeline.vue"

defineProps({
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

const format = value =>
  value
    ?.replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase())
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