<template>
  <div class="approval-timeline">
    <div
      v-for="(approval, index) in approvals"
      :key="approval.id ?? index"
      class="timeline-item"
    >
      <div class="timeline-icon" :class="statusClass(approval.status)">
        <i :class="statusIcon(approval.status)"></i>
      </div>

      <div class="timeline-content">
        <div class="timeline-header">
          <h6>{{ approval.approval_role }}</h6>
          <StatusBadge :status="approval.status" />
        </div>

        <small class="text-muted">
          {{ approval.approver_name || "Awaiting Assignment" }}
        </small>

        <p
          v-if="approval.remarks"
          class="remarks"
        >
          {{ approval.remarks }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "./StatusBadge.vue"

defineProps({
  approvals: {
    type: Array,
    default: () => []
  }
})

const statusClass = status => {
  switch (status) {
    case "APPROVED":
      return "approved"

    case "REJECTED":
      return "rejected"

    case "CHANGES_REQUESTED":
      return "changes"

    case "PENDING":
      return "pending"

    default:
      return ""
  }
}

const statusIcon = status => {
  switch (status) {
    case "APPROVED":
      return "bi bi-check-circle-fill"

    case "REJECTED":
      return "bi bi-x-circle-fill"

    case "CHANGES_REQUESTED":
      return "bi bi-pencil-fill"

    case "PENDING":
      return "bi bi-clock-fill"

    default:
      return "bi bi-circle"
  }
}
</script>

<style scoped>
.approval-timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 18px;
  position: relative;
  padding-bottom: 28px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item:not(:last-child)::after {
  content: "";
  position: absolute;
  left: 15px;
  top: 36px;
  width: 2px;
  height: calc(100% - 10px);
  background: #dee2e6;
}

.timeline-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.timeline-header h6 {
  margin: 0;
  font-weight: 600;
}

.remarks {
  margin-top: 8px;
  margin-bottom: 0;
  font-size: 0.9rem;
}

.approved {
  background: #198754;
}

.pending {
  background: #ffc107;
}

.rejected {
  background: #dc3545;
}

.changes {
  background: #0d6efd;
}
</style>