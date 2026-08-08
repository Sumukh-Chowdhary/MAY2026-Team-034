<script setup>
const props = defineProps({
  role: {
    type: String,
    default: 'STUDENT'
  },
  clubs: {
    type: Array,
    default: () => []
  },
  coordinatorRoles: {
    type: Array,
    default: () => []
  },
  organizerRoles: {
    type: Array,
    default: () => []
  }
})
</script>

<template>
  <div class="role-badge-list d-flex flex-column gap-4">
    <!-- System & Club Memberships -->
    <div>
      <h5 class="fw-bold text-dark mb-2 pb-2 border-bottom d-flex align-items-center gap-2">
        <span class="material-symbols-rounded text-primary">groups</span>
        Current Clubs & Memberships
      </h5>
      <div v-if="clubs && clubs.length > 0" class="d-flex flex-wrap gap-2 pt-1">
        <span v-for="c in clubs" :key="c" class="badge bg-primary-subtle text-primary border px-3 py-1.5 rounded-pill text-xs fw-bold">
          🏛️ {{ c }}
        </span>
      </div>
      <p v-else class="text-muted text-xs m-0 py-1">No active club memberships assigned.</p>
    </div>

    <!-- Faculty Coordinator Roles -->
    <div v-if="role === 'FACULTY' || (coordinatorRoles && coordinatorRoles.length > 0)">
      <h5 class="fw-bold text-dark mb-2 pb-2 border-bottom d-flex align-items-center gap-2">
        <span class="material-symbols-rounded text-primary">supervisor_account</span>
        Faculty Coordinator Roles
      </h5>
      <div v-if="coordinatorRoles && coordinatorRoles.length > 0" class="d-flex flex-column gap-2 pt-1">
        <div v-for="cr in coordinatorRoles" :key="cr.club" class="p-2.5 bg-light rounded-3 border d-flex justify-content-between align-items-center">
          <div>
            <span class="fw-bold text-dark text-xs d-block">{{ cr.club }}</span>
            <small class="text-muted text-xs">{{ cr.role || 'Faculty Advisor' }}</small>
          </div>
          <span class="badge bg-success-subtle text-success border px-2 py-0.5 text-xs">Active</span>
        </div>
      </div>
      <p v-else class="text-muted text-xs m-0 py-1">No faculty coordinator assignments.</p>
    </div>

    <!-- General Event Organizer Roles -->
    <div>
      <h5 class="fw-bold text-dark mb-2 pb-2 border-bottom d-flex align-items-center gap-2">
        <span class="material-symbols-rounded text-primary">event_seat</span>
        Event Organizer Responsibilities
      </h5>
      <div v-if="organizerRoles && organizerRoles.length > 0" class="d-flex flex-column gap-2 pt-1">
        <div v-for="ev in organizerRoles" :key="ev.title" class="p-2.5 bg-light rounded-3 border d-flex justify-content-between align-items-center">
          <div>
            <span class="fw-bold text-dark text-xs d-block">{{ ev.title }}</span>
            <small class="text-muted text-xs">{{ ev.role }} {{ ev.club ? '· ' + ev.club : '' }}</small>
          </div>
          <span class="badge bg-info-subtle text-info border px-2 py-0.5 text-xs">Assigned</span>
        </div>
      </div>
      <p v-else class="text-muted text-xs m-0 py-1">No event organizer responsibilities.</p>
    </div>
  </div>
</template>
