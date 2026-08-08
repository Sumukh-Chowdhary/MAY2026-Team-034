<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  club: {
    type: Object,
    required: true
  },
  isMyClub: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['navigate'])

const clubName = computed(() => props.club.name || props.club.clubName || props.club.club_name || 'Club')
const roleTitle = computed(() => props.club.roleTitle || props.club.role || props.club.faculty_role || 'Faculty Coordinator')
const memberCount = computed(() => {
  if (props.club.activeMembers !== undefined && props.club.activeMembers !== null) return props.club.activeMembers
  if (props.club.totalMembers !== undefined && props.club.totalMembers !== null) return props.club.totalMembers
  if (props.club.membersCount !== undefined && props.club.membersCount !== null) return props.club.membersCount
  if (Array.isArray(props.club.members)) return props.club.members.length
  return 0
})
const upcomingEventCount = computed(() => {
  if (props.club.eventsCount !== undefined && props.club.eventsCount !== null) return props.club.eventsCount
  if (Array.isArray(props.club.events)) return props.club.events.length
  return 0
})

const clubDescription = computed(() => props.club.description || props.club.club_description || props.club.clubDescription || '')

function isImageUrl(url) {
  if (!url) return false
  return url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/') || url.startsWith('data:')
}

function handleClick() {
  const clubId = props.club.id || props.club.clubId
  if (clubId) {
    router.push(`/faculty/clubs/${clubId}`)
  }
}
</script>

<template>
  <!-- Card for My Clubs (Section 1) -->
  <article v-if="isMyClub" class="faculty-club-card my-club-card" @click="handleClick">
    <div class="card-top">
      <div class="logo-box">
        <img v-if="isImageUrl(club.logo || club.club_logo)" :src="club.logo || club.club_logo" :alt="clubName" class="logo-img" />
        <span v-else-if="club.logo" class="material-symbols-rounded logo-icon">{{ club.logo }}</span>
        <span v-else class="logo-initial">{{ clubName.charAt(0) }}</span>
      </div>

      <span class="active-badge">
        <span class="dot"></span>
        Active
      </span>
    </div>

    <div class="card-body">
      <h3 class="club-title">{{ clubName }}</h3>
      
      <div class="role-chip">
        <span class="material-symbols-rounded icon-xs">verified_user</span>
        <span>{{ roleTitle }}</span>
      </div>

      <div class="metrics-row">
        <span class="metric-item">
          <span class="material-symbols-rounded icon-sm">groups</span>
          {{ memberCount }} Members
        </span>
        <span class="metric-item">
          <span class="material-symbols-rounded icon-sm">event</span>
          {{ upcomingEventCount }} Events
        </span>
      </div>
    </div>

    <div class="card-footer">
      <button type="button" class="btn-manage" @click.stop="handleClick">
        Manage Club →
      </button>
    </div>
  </article>

  <!-- Card for All Clubs (Section 2 - Matching Admin Styling) -->
  <article v-else class="club-card all-club-card" @click="handleClick">
    <div class="club-header">
      <div class="club-image">
        <img v-if="isImageUrl(club.logo || club.club_logo)" :src="club.logo || club.club_logo" :alt="clubName" class="logo-img" />
        <span v-else-if="club.logo" class="material-symbols-rounded logo-icon">{{ club.logo }}</span>
        <span v-else class="logo-initial">{{ clubName.charAt(0) }}</span>
      </div>

      <span class="category" v-if="club.category || club.club_category">
        {{ club.category || club.club_category }}
      </span>
    </div>

    <div class="club-content">
      <h3>{{ clubName }}</h3>
      <p class="description short-desc" v-if="clubDescription">{{ clubDescription }}</p>
    </div>

    <div class="club-stats d-flex align-items-center justify-content-between">
      <span class="status-chip" :class="(club.status || 'ACTIVE') === 'ACTIVE' ? 'live' : 'inactive'">
        <span class="status-badge"></span>
        {{ (club.status || 'ACTIVE') === 'ACTIVE' ? 'Live Club' : 'Legacy' }}
      </span>

      <span class="members">
        👥 {{ memberCount }} Members
      </span>
    </div>

    <div class="footer-actions">
      <button class="view-btn" @click.stop="handleClick">
        View Club
      </button>
    </div>
  </article>
</template>

<style scoped>
.faculty-club-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 16px;
  cursor: pointer;
  transition: all 0.28s ease;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
}

.faculty-club-card:hover {
  transform: translateY(-4px);
  border-color: #2563eb;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.12);
}

/* Admin Card Matching Styles for All Clubs */
.club-card {
  background: #fff;
  border: 1px solid #edf2f7;
  border-radius: 18px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 18px;
  min-height: 310px;
  transition: all .28s ease;
  box-shadow: 0 8px 24px rgba(15, 23, 42, .06);
  cursor: pointer;
}

.club-card:hover {
  transform: translateY(-6px);
  border-color: #2563eb;
  box-shadow: 0 18px 40px rgba(37, 99, 235, .12);
}

.club-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.club-image {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: #eef4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid #dbeafe;
}

.club-image .logo-icon {
  font-size: 32px;
  color: #2563eb;
}

.category {
  background: #eef4ff;
  color: #2563eb;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.club-content h3 {
  margin: 0 0 8px;
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 700;
}

.short-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
  color: #6b7280;
  line-height: 1.6;
  font-size: 0.9rem;
  min-height: 44px;
}

.club-stats {
  margin-top: 4px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.status-chip.live {
  background: #dcfce7;
  color: #15803d;
}

.status-chip.inactive {
  background: #fef9c3;
  color: #a16207;
}

.status-badge {
  width: 6px;
  height: 6px;
  min-width: 6px;
  min-height: 6px;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
  flex-shrink: 0;
}

.members {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.view-btn {
  width: 100%;
  border: none;
  border-radius: 10px;
  background: #2563eb;
  color: #fff;
  padding: 10px 18px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all .2s ease;
}

.view-btn:hover {
  background: #1d4ed8;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-box {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid #dbeafe;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-icon {
  font-size: 28px;
  color: #2563eb;
}

.logo-initial {
  font-size: 24px;
  font-weight: 800;
  color: #2563eb;
}

.active-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 999px;
  background: #dcfce7;
  color: #15803d;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.active-badge .dot {
  width: 6px;
  height: 6px;
  min-width: 6px;
  min-height: 6px;
  border-radius: 50%;
  background: #16a34a;
  display: inline-block;
  flex-shrink: 0;
}

.category-chip {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 0.78rem;
  font-weight: 600;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.club-title {
  margin: 0;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.35;
}

.role-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 10px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.82rem;
  font-weight: 600;
  width: fit-content;
}

.icon-xs {
  font-size: 16px;
}

.icon-sm {
  font-size: 18px;
}

.metrics-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 4px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 600;
}

.card-footer {
  margin-top: 6px;
}

.btn-manage {
  width: 100%;
  padding: 10px 16px;
  border-radius: 12px;
  border: none;
  background: #2563eb;
  color: #ffffff;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease;
  text-align: center;
}

.btn-manage:hover {
  background: #1d4ed8;
}

.btn-view {
  width: 100%;
  padding: 10px 16px;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #334155;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.btn-view:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}
</style>
