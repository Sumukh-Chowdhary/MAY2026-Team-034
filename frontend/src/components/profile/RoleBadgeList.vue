<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

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

const rolePrefix = computed(() => {
  const r = (props.role || '').toUpperCase()
  if (r === 'ADMIN') return '/admin'
  if (r === 'FACULTY') return '/faculty'
  return '/student'
})

function getClubRoute(club) {
  if (typeof club === 'object' && club?.id) {
    return `${rolePrefix.value}/clubs/${club.id}`
  }
  return `${rolePrefix.value}/clubs`
}

function getClubName(club) {
  if (typeof club === 'object' && club) {
    return club.name || club.clubName || 'Club'
  }
  return String(club)
}

function navigateToClub(club) {
  router.push(getClubRoute(club))
}
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
        <RouterLink 
          v-for="c in clubs" 
          :key="getClubName(c)" 
          :to="getClubRoute(c)"
          class="badge bg-primary-subtle text-primary border px-3 py-2 rounded-pill text-xs fw-bold text-decoration-none club-badge-link d-inline-flex align-items-center gap-1"
          :title="`View ${getClubName(c)} details`"
        >
          <span>🏛️ {{ getClubName(c) }}</span>
          <i class="bi bi-box-arrow-up-right ms-1" style="font-size: 10px;"></i>
        </RouterLink>
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
        <div 
          v-for="cr in coordinatorRoles" 
          :key="getClubName(cr.club)" 
          class="p-2.5 bg-light rounded-3 border d-flex justify-content-between align-items-center cursor-pointer hover-tile"
          @click="navigateToClub(cr.clubObj || cr.clubId ? { id: cr.clubId } : cr.club)"
          :title="`Open ${getClubName(cr.club)} club page`"
        >
          <div>
            <span class="fw-bold text-primary text-xs d-block">
              {{ getClubName(cr.club) }}
              <i class="bi bi-arrow-right-short ms-1"></i>
            </span>
            <small class="text-muted text-xs">{{ cr.role || 'Faculty Coordinator' }}</small>
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
        <div 
          v-for="ev in organizerRoles" 
          :key="ev.title + (ev.club || '')" 
          class="p-2.5 bg-light rounded-3 border d-flex justify-content-between align-items-center"
          :class="ev.clubId || ev.club ? 'cursor-pointer hover-tile' : ''"
          @click="ev.clubId || ev.club ? navigateToClub(ev.clubId ? { id: ev.clubId } : ev.club) : null"
        >
          <div>
            <span class="fw-bold text-dark text-xs d-block">
              {{ ev.title }}
              <i v-if="ev.club" class="bi bi-arrow-right-short text-primary ms-1"></i>
            </span>
            <small class="text-muted text-xs">{{ ev.role }} {{ ev.club ? '· ' + getClubName(ev.club) : '' }}</small>
          </div>
          <span class="badge bg-info-subtle text-info border px-2 py-0.5 text-xs">Assigned</span>
        </div>
      </div>
      <p v-else class="text-muted text-xs m-0 py-1">No event organizer responsibilities.</p>
    </div>
  </div>
</template>

<style scoped>
.club-badge-link {
  transition: all 0.2s ease;
}
.club-badge-link:hover {
  background-color: #2563eb !important;
  color: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.hover-tile {
  transition: all 0.2s ease;
}
.hover-tile:hover {
  background-color: #eff6ff !important;
  border-color: #bfdbfe !important;
  transform: translateY(-1px);
}
</style>
