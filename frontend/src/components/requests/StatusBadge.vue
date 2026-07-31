<template>
  <span class="status-badge" :class="badgeClass">
    <i :class="iconClass"></i>
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  status: {
    type: String,
    required: true
  }
})

const normalizedStatus = computed(() =>
  props.status?.toUpperCase() || ""
)

const label = computed(() =>
  normalizedStatus.value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase())
)

const badgeClass = computed(() => {
  switch (normalizedStatus.value) {
    case "APPROVED":
      return "approved"

    case "PENDING":
      return "pending"

    case "REJECTED":
      return "rejected"

    case "CHANGES_REQUESTED":
      return "changes"

    case "ACTIVE":
      return "active"

    case "SUSPENDED":
      return "suspended"

    case "COMPLETED":
      return "completed"

    default:
      return "default"
  }
})

const iconClass = computed(() => {
  switch (normalizedStatus.value) {
    case "APPROVED":
      return "bi bi-check-circle-fill"

    case "PENDING":
      return "bi bi-clock-fill"

    case "REJECTED":
      return "bi bi-x-circle-fill"

    case "CHANGES_REQUESTED":
      return "bi bi-pencil-square"

    case "ACTIVE":
      return "bi bi-play-circle-fill"

    case "SUSPENDED":
      return "bi bi-pause-circle-fill"

    case "COMPLETED":
      return "bi bi-check2-all"

    default:
      return "bi bi-circle-fill"
  }
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 50px;
  font-size: 0.82rem;
  font-weight: 600;
}

.status-badge i {
  font-size: 0.9rem;
}

.approved {
  background: #d1fae5;
  color: #047857;
}

.pending {
  background: #fef3c7;
  color: #b45309;
}

.rejected {
  background: #fee2e2;
  color: #b91c1c;
}

.changes {
  background: #dbeafe;
  color: #1d4ed8;
}

.active {
  background: #dcfce7;
  color: #166534;
}

.suspended {
  background: #f3f4f6;
  color: #4b5563;
}

.completed {
  background: #ede9fe;
  color: #6d28d9;
}

.default {
  background: #e5e7eb;
  color: #374151;
}
</style>