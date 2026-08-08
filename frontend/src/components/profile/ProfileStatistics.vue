<script setup>
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      totalRequests: 0,
      pendingRequests: 0,
      approvedRequests: 0,
      notificationsCount: 0
    })
  }
})
</script>

<template>
  <div class="row g-3 profile-statistics-row">
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm rounded-4 p-3 text-center bg-white h-100">
        <span class="material-symbols-rounded text-primary fs-3 mb-1">send</span>
        <h4 class="fw-bold text-dark m-0">{{ stats.totalRequests || 0 }}</h4>
        <span class="text-xs text-muted">Submitted Requests</span>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm rounded-4 p-3 text-center bg-white h-100">
        <span class="material-symbols-rounded text-amber fs-3 mb-1" style="color: #f59e0b;">pending_actions</span>
        <h4 class="fw-bold text-dark m-0">{{ stats.pendingRequests || 0 }}</h4>
        <span class="text-xs text-muted">Pending Approvals</span>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm rounded-4 p-3 text-center bg-white h-100">
        <span class="material-symbols-rounded text-success fs-3 mb-1">task_alt</span>
        <h4 class="fw-bold text-dark m-0">{{ stats.approvedRequests || 0 }}</h4>
        <span class="text-xs text-muted">Approved Requests</span>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm rounded-4 p-3 text-center bg-white h-100">
        <span class="material-symbols-rounded text-indigo fs-3 mb-1" style="color: #6366f1;">notifications_active</span>
        <h4 class="fw-bold text-dark m-0">{{ stats.notificationsCount || 0 }}</h4>
        <span class="text-xs text-muted">Notifications Received</span>
      </div>
    </div>
  </div>
</template>
