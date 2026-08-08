<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { getUser } from '@/api/users'
import { getMyClubs } from '@/api/student'
import { getEvents } from '@/api/events'

const router = useRouter()

const userProfile = ref(null)
const myClubs = ref([])
const upcomingEvents = ref([])
const loading = ref(true)

const avatarInitials = computed(() => {
  const name = userProfile.value?.fullName || userProfile.value?.name || 'S'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const stats = computed(() => [
  { label: 'Clubs Joined', value: myClubs.value.length, icon: 'bi-collection-fill', color: '#2563eb', bg: '#eff6ff' },
  { label: 'Upcoming Events', value: upcomingEvents.value.length, icon: 'bi-calendar-event-fill', color: '#7c3aed', bg: '#f3f0ff' },
  { label: 'Active Roles', value: myClubs.value.filter(c => c.membershipRole && c.membershipRole !== 'MEMBER').length, icon: 'bi-star-fill', color: '#d97706', bg: '#fffbeb' },
  { label: 'Account Status', value: userProfile.value?.status || 'ACTIVE', icon: 'bi-shield-fill-check', color: '#059669', bg: '#f0fdf4' }
])

const categoryEmojis = { TECHNICAL: '💻', CULTURAL: '🎭', SPORTS: '⚽', ARTS: '🎨', MUSIC: '🎵', DEFAULT: '🏛️' }

function getClubEmoji(cat) {
  return categoryEmojis[(cat || '').toUpperCase()] || categoryEmojis.DEFAULT
}

function formatDate(dateStr) {
  if (!dateStr) return 'TBD'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

onMounted(async () => {
  loading.value = true
  try {
    const stored = JSON.parse(localStorage.getItem('user') || '{}')
    if (stored.id) {
      userProfile.value = await getUser(stored.id).catch(() => stored)
    } else {
      userProfile.value = stored
    }

    const [clubs, events] = await Promise.allSettled([
      getMyClubs(),
      getEvents()
    ])

    myClubs.value = clubs.status === 'fulfilled' && Array.isArray(clubs.value) ? clubs.value : []
    const allEvents = events.status === 'fulfilled' && Array.isArray(events.value) ? events.value : []
    upcomingEvents.value = allEvents
      .filter(e => e.startDate ? new Date(e.startDate) >= new Date() : true)
      .slice(0, 5)
  } catch (err) {
    console.error('Dashboard load error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <StudentLayout>
    <section class="dashboard-page">

      <!-- HEADER -->
      <div class="dashboard-header">
        <div class="header-left">
          <h2 class="header-title">
            Welcome back{{ userProfile?.fullName ? ', ' + userProfile.fullName.split(' ')[0] : '' }}! 👋
          </h2>
          <p class="header-sub">Discover clubs, manage your roles, and stay updated with campus events.</p>
        </div>
        <div class="header-right">
          <div class="profile-quick-card" @click="router.push('/student/profile')">
            <div class="quick-avatar">{{ avatarInitials }}</div>
            <div class="quick-info">
              <span class="quick-name">{{ userProfile?.fullName || userProfile?.name || 'Student' }}</span>
              <span class="quick-role">View Profile →</span>
            </div>
          </div>
        </div>
      </div>

      <!-- LOADING -->
      <div v-if="loading" class="loading-row">
        <div v-for="i in 4" :key="i" class="stat-skeleton"></div>
      </div>

      <template v-else>

        <!-- STATS -->
        <div class="stats-row">
          <div v-for="stat in stats" :key="stat.label" class="stat-card" :style="`--c:${stat.color}; --bg:${stat.bg}`">
            <div class="stat-icon"><i :class="['bi', stat.icon]"></i></div>
            <div class="stat-body">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>

        <!-- MAIN GRID -->
        <div class="main-grid">

          <!-- My Clubs -->
          <div class="dashboard-card">
            <div class="card-head">
              <div>
                <h5 class="card-title">My Clubs</h5>
                <p class="card-sub">Clubs you are currently part of.</p>
              </div>
              <RouterLink to="/student/clubs" class="card-action">Browse All</RouterLink>
            </div>
            <div class="card-body">
              <div v-if="myClubs.length === 0" class="empty-state">
                <span>🎭</span>
                <p>You haven't joined any clubs yet.</p>
                <RouterLink to="/student/clubs" class="empty-link">Explore Clubs →</RouterLink>
              </div>
              <div v-else>
                <div v-for="club in myClubs.slice(0, 5)" :key="club.id" class="list-item">
                  <div class="item-left">
                    <div class="item-icon">{{ getClubEmoji(club.category) }}</div>
                    <div>
                      <h6 class="item-title">{{ club.name }}</h6>
                      <span class="item-sub">{{ club.membershipRole || 'MEMBER' }}</span>
                    </div>
                  </div>
                  <RouterLink :to="`/student/clubs/${club.id}`" class="view-btn">View</RouterLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Upcoming Events -->
          <div class="dashboard-card">
            <div class="card-head">
              <div>
                <h5 class="card-title">Upcoming Events</h5>
                <p class="card-sub">Events you may be interested in.</p>
              </div>
              <RouterLink to="/student/events" class="card-action">See All</RouterLink>
            </div>
            <div class="card-body">
              <div v-if="upcomingEvents.length === 0" class="empty-state">
                <span>📅</span>
                <p>No upcoming events found.</p>
              </div>
              <div v-else>
                <div v-for="event in upcomingEvents" :key="event.id" class="list-item">
                  <div class="item-left">
                    <div class="event-date-badge">
                      <span>{{ formatDate(event.startDate) }}</span>
                    </div>
                    <div>
                      <h6 class="item-title">{{ event.eventName || event.title }}</h6>
                      <span class="item-sub">{{ event.clubName || event.club || 'Campus Event' }}</span>
                    </div>
                  </div>
                  <RouterLink :to="`/student/events/${event.id}`" class="view-btn">View</RouterLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Club Details Quick Panel -->
          <div class="dashboard-card full-width-card">
            <div class="card-head">
              <div>
                <h5 class="card-title">My Club Memberships</h5>
                <p class="card-sub">Overview of all your club roles and memberships.</p>
              </div>
              <RouterLink to="/student/profile" class="card-action">Full Profile</RouterLink>
            </div>
            <div class="card-body">
              <div v-if="myClubs.length === 0" class="empty-state">
                <span>🏆</span>
                <p>Join clubs to see them here.</p>
              </div>
              <div v-else class="club-chips-grid">
                <div v-for="club in myClubs" :key="club.id" class="club-chip">
                  <div class="chip-emoji">{{ getClubEmoji(club.category) }}</div>
                  <div class="chip-info">
                    <span class="chip-name">{{ club.name }}</span>
                    <span class="chip-role">{{ club.membershipRole || 'MEMBER' }}</span>
                  </div>
                  <div class="chip-members">
                    <i class="bi bi-people-fill"></i> {{ club.activeMembers || club.totalMembers || 0 }}
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </template>

    </section>
  </StudentLayout>
</template>

<style scoped>
.dashboard-page { width:100%; max-width:1600px; margin:0 auto; padding-bottom:40px; }

/* Header */
.dashboard-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:28px; gap:20px; flex-wrap:wrap; }
.header-title { margin:0; color:#1e293b; font-size:1.75rem; font-weight:800; }
.header-sub { margin:6px 0 0; color:#64748b; font-size:0.95rem; }
.profile-quick-card {
  display:flex; align-items:center; gap:14px;
  padding:14px 20px; background:white; border-radius:16px;
  box-shadow:0 4px 20px rgba(15,23,42,0.08); cursor:pointer;
  border:1.5px solid #e2e8f0; transition:all 0.2s;
}
.profile-quick-card:hover { border-color:#2563eb; box-shadow:0 6px 24px rgba(37,99,235,0.12); transform:translateY(-1px); }
.quick-avatar {
  width:42px; height:42px; border-radius:50%;
  background:linear-gradient(135deg,#2563eb,#1d4ed8);
  color:white; font-weight:800; font-size:1rem;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.quick-name { font-size:0.9rem; font-weight:700; color:#1e293b; display:block; }
.quick-role { font-size:0.75rem; color:#2563eb; font-weight:600; }

/* Loading skeletons */
.loading-row { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-bottom:24px; }
.stat-skeleton { height:90px; background:linear-gradient(90deg,#f1f5f9 25%,#e2e8f0 50%,#f1f5f9 75%); border-radius:16px; animation:shimmer 1.5s infinite; background-size:200% 100%; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* Stats */
.stats-row { display:grid; grid-template-columns:repeat(4,1fr); gap:18px; margin-bottom:24px; }
.stat-card {
  background:white; border-radius:16px; padding:20px 22px;
  display:flex; align-items:center; gap:16px;
  box-shadow:0 4px 16px rgba(15,23,42,0.06);
  border:1.5px solid #e2e8f0; transition:all 0.2s;
}
.stat-card:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(15,23,42,0.1); }
.stat-icon {
  width:46px; height:46px; border-radius:12px;
  background:var(--bg); color:var(--c);
  display:flex; align-items:center; justify-content:center;
  font-size:1.2rem; flex-shrink:0;
}
.stat-value { font-size:1.4rem; font-weight:800; color:#1e293b; line-height:1; }
.stat-label { font-size:0.75rem; color:#94a3b8; font-weight:500; margin-top:3px; }

/* Main grid */
.main-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.full-width-card { grid-column:1 / -1; }

/* Dashboard cards */
.dashboard-card { background:white; border-radius:20px; box-shadow:0 4px 20px rgba(15,23,42,0.06); overflow:hidden; border:1px solid #f1f5f9; }
.card-head { display:flex; justify-content:space-between; align-items:center; padding:20px 24px; border-bottom:1px solid #f1f5f9; }
.card-title { margin:0; color:#1e293b; font-size:1rem; font-weight:700; }
.card-sub { margin:4px 0 0; color:#64748b; font-size:0.82rem; }
.card-action { font-size:0.8rem; color:#2563eb; font-weight:700; text-decoration:none; padding:6px 14px; border-radius:8px; background:#eff6ff; border:1px solid #bfdbfe; transition:all 0.2s; white-space:nowrap; }
.card-action:hover { background:#2563eb; color:white; }
.card-body { padding:8px 24px 20px; }

/* List items */
.list-item { display:flex; align-items:center; justify-content:space-between; padding:14px 0; border-bottom:1px solid #f8fafc; gap:12px; }
.list-item:last-child { border-bottom:none; }
.item-left { display:flex; align-items:center; gap:14px; min-width:0; flex:1; }
.item-icon { width:40px; height:40px; border-radius:10px; background:#f1f5f9; display:flex; align-items:center; justify-content:center; font-size:1.25rem; flex-shrink:0; }
.item-title { font-size:0.88rem; font-weight:700; color:#1e293b; margin:0 0 3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.item-sub { font-size:0.75rem; color:#94a3b8; }
.view-btn { padding:6px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; color:#2563eb; font-size:0.78rem; font-weight:700; text-decoration:none; flex-shrink:0; transition:all 0.2s; }
.view-btn:hover { background:#2563eb; color:white; border-color:#2563eb; }

/* Event date badge */
.event-date-badge { width:44px; height:44px; border-radius:10px; background:#eff6ff; border:1px solid #bfdbfe; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.event-date-badge span { font-size:0.65rem; font-weight:800; color:#2563eb; text-align:center; line-height:1.2; }

/* Empty state */
.empty-state { text-align:center; padding:30px 20px; color:#94a3b8; }
.empty-state span { font-size:2.5rem; display:block; margin-bottom:10px; }
.empty-state p { font-size:0.85rem; margin:0 0 12px; }
.empty-link { font-size:0.82rem; color:#2563eb; font-weight:700; text-decoration:none; }

/* Club chips grid */
.club-chips-grid { display:flex; flex-wrap:wrap; gap:12px; padding-top:8px; }
.club-chip {
  display:flex; align-items:center; gap:12px;
  padding:12px 16px; border-radius:14px;
  background:#f8fafc; border:1.5px solid #e2e8f0;
  transition:all 0.2s; min-width:200px; flex:1;
}
.club-chip:hover { border-color:#2563eb; background:#eff6ff; }
.chip-emoji { font-size:1.4rem; }
.chip-info { flex:1; min-width:0; }
.chip-name { font-size:0.85rem; font-weight:700; color:#1e293b; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.chip-role { font-size:0.72rem; color:#64748b; font-weight:500; }
.chip-members { font-size:0.75rem; color:#94a3b8; font-weight:500; white-space:nowrap; }

/* Responsive */
@media (max-width:1100px) { .stats-row { grid-template-columns:repeat(2,1fr); } }
@media (max-width:768px) {
  .dashboard-header { flex-direction:column; align-items:flex-start; }
  .main-grid { grid-template-columns:1fr; }
  .stats-row { grid-template-columns:repeat(2,1fr); }
  .loading-row { grid-template-columns:repeat(2,1fr); }
}
@media (max-width:480px) {
  .stats-row { grid-template-columns:1fr 1fr; }
  .club-chips-grid { flex-direction:column; }
}
</style>