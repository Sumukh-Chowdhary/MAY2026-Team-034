<script setup>
// Define emits here if you need to pass the rejection reason back to the parent
const emit = defineEmits(['reject']);
</script>

<template>
  <div
    class="modal fade"
    id="rejectModal"
    tabindex="-1"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Reject Request</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <div class="modal-body">
          <label for="rejectionReason" class="form-label fw-semibold">
            Reason
          </label>
          <textarea
            id="rejectionReason"
            rows="5"
            class="form-control"
            placeholder="Enter rejection reason..."
          ></textarea>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-danger"
            data-bs-dismiss="modal"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-content {
  border-radius: 18px;
}

textarea {
  resize: none;
}
</style>