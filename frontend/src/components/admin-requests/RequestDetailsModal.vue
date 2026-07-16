<script setup>
defineProps({
  request: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <div
    class="modal fade"
    id="requestModal"
    tabindex="-1"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">Request Details</h4>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <div class="modal-body" v-if="request">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="fw-semibold">Requested By</label>
              <p>{{ request.requestedBy }}</p>
            </div>

            <div class="col-md-6 mb-3">
              <label class="fw-semibold">Register Number</label>
              <p>{{ request.registerNumber }}</p>
            </div>

            <div class="col-md-6 mb-3">
              <label class="fw-semibold">Club</label>
              <p>{{ request.club }}</p>
            </div>

            <div class="col-md-6 mb-3">
              <label class="fw-semibold">Date</label>
              <p>{{ request.date }}</p>
            </div>

            <div class="col-12 mb-3">
              <label class="fw-semibold">Subject</label>
              <p>{{ request.subject }}</p>
            </div>

            <div class="col-12">
              <label class="fw-semibold">Description</label>
              <p>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                This is placeholder text until backend integration.
              </p>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-danger"
            data-bs-target="#rejectModal"
            data-bs-toggle="modal"
          >
            Reject
          </button>
          <button
            type="button"
            class="btn btn-success"
            data-bs-dismiss="modal"
          >
            Approve
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
</style>