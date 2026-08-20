<script setup>
import { ref, computed, onMounted } from 'vue'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import { useRouter } from 'vue-router'
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import StatCard from '@/components/admin/analytics/StatCard.vue'

import { getUser, updateUser } from '@/api/users'
import { getMySupervisedClubs, getFacultyGeneralEvents } from '@/api/faculty'
import { getFacultyRequestsDashboard } from '@/api/requests'
import { getEvents } from '@/api/events'

const router = useRouter()

const userProfile = ref(null)
const managedClubs = ref([])
const generalEvents = ref([])
const pendingRequests = ref([])
const upcomingEvents = ref([])
const loading = ref(true)

// Profile Edit Modal State
const showProfileModal = ref(false)
const profileForm = ref({
  fullName: '',
  phone: '',
  designation: '',
  bio: ''
})
const savingProfile = ref(false)

const stats = computed(() => [
  { label: 'Supervised Clubs', value: managedClubs.value.length },
  { label: 'General Events', value: generalEvents.value.length },
  { label: 'Pending Approvals', value: pendingRequests.value.length },
  { label: 'Upcoming Events', value: upcomingEvents.value.length }
])

onMounted(async () => {
  await loadDashboardData()
})

async function loadDashboardData() {
  loading.value = true
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const u = JSON.parse(userStr)
      const freshUser = await getUser(u.id).catch(() => u)
      userProfile.value = freshUser
      profileForm.value = {
        fullName: freshUser.fullName || freshUser.name || '',
        phone: freshUser.phone || freshUser.phoneNumber || '',
        designation: freshUser.designation || '',
        bio: freshUser.bio || ''
      }
    }

    const clubsData = await getMySupervisedClubs().catch(() => [])
    managedClubs.value = clubsData || []

    const genEvents = await getFacultyGeneralEvents().catch(() => [])
    generalEvents.value = Array.isArray(genEvents) ? genEvents : []

    const reqData = await getFacultyRequestsDashboard().catch(() => ({ data: {} }))
    pendingRequests.value = reqData?.data?.incomingRequests || []

    const eventsData = await getEvents().catch(() => [])
    upcomingEvents.value = Array.isArray(eventsData) ? eventsData.slice(0, 5) : []
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
  } finally {
    loading.value = false
  }
}

function openEditProfile() {
  router.push('/faculty/profile')
}

async function handleSaveProfile() {
  if (!userProfile.value?.id) return
  savingProfile.value = true
  try {
    const updated = await updateUser(userProfile.value.id, {
      fullName: profileForm.value.fullName,
      phone: profileForm.value.phone,
      designation: profileForm.value.designation,
      bio: profileForm.value.bio
    })
    userProfile.value = { ...userProfile.value, ...updated }
    
    // Update local storage
    const currentStored = JSON.parse(localStorage.getItem('user') || '{}')
    localStorage.setItem('user', JSON.stringify({ ...currentStored, ...updated }))

    alert('Profile updated successfully!')
    showProfileModal.value = false
  } catch (err) {
    alert('Failed to update profile.')
    console.error(err)
  } finally {
    savingProfile.value = false
  }
}

function navigateToRoles() {
  router.push('/faculty/roles')
}

function navigateToRequests() {
  router.push('/faculty/requests')
}

function navigateToClub(clubId) {
  if (clubId) {
    router.push(`/faculty/clubs/${clubId}`)
  } else {
    router.push('/faculty/clubs')
  }
}
</script>

<template>
  <FacultyLayout>
    <section class="dashboard-page">
      <!-- Dashboard Header -->
      <div class="dashboard-header">
        <div>
          <h2>Faculty Dashboard</h2>
          <p>Welcome back, {{ userProfile?.fullName || userProfile?.name || 'Faculty Coordinator' }}. Manage clubs, events, and profile.</p>
        </div>
        <div class="dashboard-actions">
          <button class="request-btn" @click="openEditProfile">
            <i class="bi bi-person-gear me-1"></i> View Profile
          </button>
        </div>
      </div>

      <!-- Quick Nav Shortcuts -->
      <div class="quick-nav-bar d-flex align-items-center gap-2 mb-4 overflow-x-auto pb-1">
        <button class="quick-chip active" @click="router.push('/faculty')">
          <i class="bi bi-speedometer2 me-1"></i> Overview
        </button>
        <button class="quick-chip" @click="router.push('/faculty/clubs')">
          <i class="bi bi-collection-fill me-1 text-primary"></i> Supervised Clubs
        </button>
        <button class="quick-chip" @click="router.push('/faculty/roles')">
          <i class="bi bi-shield-check me-1 text-warning"></i> Role Details
        </button>
        <button class="quick-chip" @click="router.push('/faculty/events')">
          <i class="bi bi-calendar-event-fill me-1 text-success"></i> Events
        </button>
        <button class="quick-chip" @click="router.push('/faculty/requests')">
          <i class="bi bi-inbox-fill me-1 text-info"></i> Approvals & Requests
        </button>
      </div>

      <!-- Stat Cards -->
      <div class="row g-4">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="col-12 col-sm-6 col-xl-3"
        >
          <StatCard
            :label="stat.label"
            :value="stat.value"
          />
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="row g-4 mt-1">

        <!-- Supervised Clubs Section (Modern Management Cards) -->
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h4 class="fw-bold m-0 text-dark">Supervised Clubs</h4>
              <p class="text-muted text-sm m-0">Clubs you currently manage or advise.</p>
            </div>
            <button class="btn btn-sm btn-link text-decoration-none fw-semibold text-primary" @click="navigateToRoles">View All Roles →</button>
          </div>

          <div v-if="managedClubs.length === 0" class="py-5 text-center text-muted bg-white rounded-4 border">
            <span class="material-symbols-rounded fs-1 text-muted mb-2">groups</span>
            <h5>No supervised clubs assigned</h5>
            <p class="text-sm">You are currently not assigned to any club coordinator role.</p>
          </div>

          <div v-else class="row g-4">
            <div
              v-for="club in managedClubs"
              :key="club.id"
              class="col-12 col-md-6 col-xl-4"
            >
              <div class="modern-management-card">
                <div class="card-top">
                  <div class="club-brand">
                    <div class="club-icon-avatar">
                      <span class="material-symbols-rounded">groups</span>
                    </div>
                    <div>
                      <h5 
                        class="club-title cursor-pointer text-primary-hover" 
                        @click="navigateToClub(club.id)"
                        :title="`Open ${club.clubName} page`"
                      >
                        {{ club.clubName }}
                        <i class="bi bi-box-arrow-up-right text-xs ms-1"></i>
                      </h5>
                      <div class="badges-row">
                        <span class="role-badge">
                          <span class="material-symbols-rounded icon-xs">workspace_premium</span>
                          {{ club.roleTitle || 'Faculty Coordinator' }}
                        </span>
                        <span class="status-pill" :class="(club.status || 'ACTIVE').toLowerCase()">
                          <span class="status-dot"></span>
                          {{ (club.status || 'ACTIVE').toUpperCase() }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Read-Only Venue & Event Details (STEP 7) -->
                <div class="p-2.5 rounded-3 bg-light border text-xs my-2">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="text-secondary">🏛️ <strong>Primary Venue:</strong> {{ club.primaryVenue || 'Innovation Lab' }}</span>
                    <span class="badge bg-success-subtle text-success border">RESERVED</span>
                  </div>
                  <div class="text-secondary text-truncate">
                    <span>📅 <strong>Next Event:</strong> {{ club.events?.[0]?.name || 'AI Hack Sprint' }}</span>
                  </div>
                </div>

                <!-- Management Metrics Grid -->
                <div class="metrics-grid">
                  <div class="metric-item">
                    <span class="material-symbols-rounded metric-icon">group</span>
                    <div>
                      <span class="metric-value">{{ club.memberCount || club.totalMembers || 1 }}</span>
                      <span class="metric-label">Members</span>
                    </div>
                  </div>

                  <div class="metric-item">
                    <span class="material-symbols-rounded metric-icon">event</span>
                    <div>
                      <span class="metric-value">{{ club.eventCount || (club.events ? club.events.length : 0) }}</span>
                      <span class="metric-label">Events</span>
                    </div>
                  </div>

                  <div class="metric-item" :class="{ 'has-pending': (club.pendingRequestsCount || 0) > 0 }">
                    <span class="material-symbols-rounded metric-icon">pending_actions</span>
                    <div>
                      <span class="metric-value">{{ club.pendingRequestsCount || 0 }}</span>
                      <span class="metric-label">Pending</span>
                    </div>
                  </div>
                </div>

                <!-- Card Action Footer -->
                <div class="card-footer-action">
                  <button class="btn-manage-club" @click="navigateToClub(club.id)">
                    Manage Club
                    <span class="material-symbols-rounded icon-sm">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- General Event Organization Section -->
        <div class="col-12 mt-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h4 class="fw-bold m-0 text-dark">
                <span class="material-symbols-rounded text-primary align-middle me-2">account_balance</span>
                General Event Organization
              </h4>
              <p class="text-muted text-sm m-0">College-wide institutional events (Orientation, Convocation, Placement Drive, Blood Donation Camp).</p>
            </div>
          </div>

          <div v-if="generalEvents.length === 0" class="py-5 text-center text-muted bg-white rounded-4 border">
            <span class="material-symbols-rounded fs-1 text-muted mb-2">event_available</span>
            <h5>No General College Events Organized</h5>
            <p class="text-sm">General campus events managed by faculty will appear here.</p>
          </div>

          <div v-else class="row g-4">
            <div
              v-for="event in generalEvents"
              :key="event.id"
              class="col-12 col-md-6 col-xl-3"
            >
              <div class="general-event-card">
                <div class="general-card-header">
                  <span class="general-type-badge">
                    <span class="material-symbols-rounded icon-xs">campaign</span>
                    General Event
                  </span>
                  <span class="status-pill" :class="(event.status || 'Scheduled').toLowerCase()">
                    <span class="status-dot"></span>
                    {{ event.status }}
                  </span>
                </div>

                <div class="general-card-body">
                  <h5 
                    class="general-event-title cursor-pointer text-primary-hover" 
                    @click="router.push(`/faculty/events/${event.id}`)"
                    :title="`Open ${event.name} details`"
                  >
                    {{ event.name }}
                  </h5>
                  <p class="general-event-desc">{{ event.description || 'Institutional college event.' }}</p>

                  <div class="general-meta-list">
                    <div class="meta-item">
                      <span class="material-symbols-rounded meta-icon">location_on</span>
                      <span>{{ event.venueName || 'Campus Venue' }}</span>
                    </div>

                    <div class="meta-item">
                      <span class="material-symbols-rounded meta-icon">calendar_today</span>
                      <span>{{ event.startDate }}</span>
                    </div>
                  </div>
                </div>

                <div class="general-card-footer">
                  <span class="capacity-chip">
                    <span class="material-symbols-rounded icon-xs">groups</span>
                    Capacity: {{ event.capacity || 'Unlimited' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Events Card -->
        <div class="col-12 col-lg-6">
          <div class="dashboard-card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div>
                <h5>Upcoming Events</h5>
                <p>Upcoming events from your clubs.</p>
              </div>
              <RouterLink to="/faculty/events" class="btn btn-sm btn-link text-decoration-none fw-semibold text-primary">See All →</RouterLink>
            </div>

            <div class="card-content">
              <div v-if="upcomingEvents.length === 0" class="py-4 text-center text-muted">
                No upcoming events scheduled.
              </div>

              <div
                v-for="event in upcomingEvents"
                :key="event.id"
                class="event-item cursor-pointer"
                @click="router.push(`/faculty/events/${event.id}`)"
                :title="`Open ${event.name || event.title} details`"
              >
                <div>
                  <h6 class="mb-1 text-primary-hover">{{ event.name || event.title }}</h6>
                  <span class="text-secondary text-xs">{{ event.clubName || 'Campus Event' }}</span>
                </div>

                <div class="event-date">
                  {{ event.startDate || 'Scheduled' }}
                </div>
              </div>
            </div>
          </div>
        </div>



        <!-- Profile & Summary Card (Sprint 1 Feature) -->
        <div class="col-12 col-lg-6">
          <div class="dashboard-card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div>
                <h5>Faculty Profile Card</h5>
                <p>Your current coordinator profile details.</p>
              </div>
              <button class="btn btn-sm btn-outline-primary rounded-pill px-3" @click="openEditProfile">
                Edit Details
              </button>
            </div>

            <div class="card-content py-3">
              <div v-if="userProfile" class="d-flex align-items-center gap-3 mb-3 p-3 bg-light rounded-3">
                <UserAvatar size="card" :user="userProfile" />
                <div>
                  <h6 class="mb-0 fw-bold">{{ userProfile.fullName || userProfile.name }}</h6>
                  <small class="text-muted">{{ userProfile.email }}</small>
                  <div class="badge bg-primary-subtle text-primary border ms-2 text-xs">
                    {{ userProfile.designation || 'Faculty Member' }}
                  </div>
                </div>
              </div>

              <div class="row g-2 text-sm" v-if="userProfile">
                <div class="col-6">
                  <span class="text-muted text-xs d-block">Department</span>
                  <strong>{{ userProfile.department || 'N/A' }}</strong>
                </div>
                <div class="col-6">
                  <span class="text-muted text-xs d-block">Phone Number</span>
                  <strong>{{ userProfile.phone || userProfile.phoneNumber || 'N/A' }}</strong>
                </div>
                <div class="col-12 mt-2" v-if="userProfile.bio">
                  <span class="text-muted text-xs d-block">Bio</span>
                  <p class="mb-0 text-secondary bg-white p-2 border rounded-2 text-xs">{{ userProfile.bio }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- Profile Edit Modal -->
    <div v-if="showProfileModal" class="modal-backdrop" @click.self="showProfileModal = false">
      <div class="modal-dialog-custom">
        <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
          <h4 class="fw-bold m-0 text-dark">
            <i class="bi bi-person-badge text-primary me-2"></i>Edit Faculty Profile
          </h4>
          <button class="btn-close" @click="showProfileModal = false"></button>
        </div>

        <form @submit.prevent="handleSaveProfile">
          <div class="mb-3">
            <label class="form-label font-semibold">Full Name</label>
            <input v-model="profileForm.fullName" type="text" class="form-control" required />
          </div>

          <div class="mb-3">
            <label class="form-label font-semibold">Phone Number</label>
            <input v-model="profileForm.phone" type="text" class="form-control" placeholder="+91 XXXXX XXXXX" />
          </div>

          <div class="mb-3">
            <label class="form-label font-semibold">Designation</label>
            <input v-model="profileForm.designation" type="text" class="form-control" placeholder="e.g. Associate Professor / Faculty Advisor" />
          </div>

          <div class="mb-3">
            <label class="form-label font-semibold">Bio / Notes</label>
            <textarea v-model="profileForm.bio" class="form-control" rows="3" placeholder="Enter bio..."></textarea>
          </div>

          <div class="d-flex justify-content-end gap-2 pt-2 border-top">
            <button type="button" class="btn btn-secondary rounded-pill px-4" @click="showProfileModal = false">Cancel</button>
            <button type="submit" class="btn btn-success rounded-pill px-4" :disabled="savingProfile">
              {{ savingProfile ? 'Saving...' : 'Save Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </FacultyLayout>
</template>

<style scoped>
.dashboard-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  gap: 20px;
}

.dashboard-header h2 {
  margin: 0;
  color: #1E293B;
  font-size: 1.75rem;
  font-weight: 700;
}

.dashboard-header p {
  margin: 7px 0 0;
  color: #64748B;
  font-size: 0.95rem;
}

.dashboard-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.request-btn {
  padding: 12px 22px;
  background: #fff;
  border: 2px solid #22C55E;
  color: #22C55E;
  border-radius: 14px;
  font-weight: 600;
  transition: 0.25s;
}

.request-btn:hover {
  background: #22C55E;
  color: #fff;
}

.notification-btn {
  padding: 12px 22px;
  background: #fff;
  border: 2px solid #2563EB;
  color: #2563EB;
  border-radius: 14px;
  font-weight: 600;
  transition: 0.25s;
}

.notification-btn:hover {
  background: #2563EB;
  color: #fff;
}

.dashboard-card {
  height: 100%;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
  overflow: hidden;
}

.card-header {
  padding: 22px 24px;
  border-bottom: 1px solid #E2E8F0;
}

.card-header h5 {
  margin: 0;
  color: #1E293B;
  font-size: 1.15rem;
  font-weight: 700;
}

.card-header p {
  margin: 5px 0 0;
  color: #64748B;
  font-size: 0.9rem;
}

/* Modern Management Cards */
.modern-management-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20px;
  box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
  transition: all 0.28s ease;
  height: 100%;
}

.modern-management-card:hover {
  transform: translateY(-4px);
  border-color: #3b82f6;
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.1);
}

.club-brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.club-icon-avatar {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
}

.club-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px;
  letter-spacing: -0.01em;
}

.badges-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f1f5f9;
  color: #334155;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 700;
}

.icon-xs {
  font-size: 14px;
  color: #2563eb;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.status-pill.active {
  background: #dcfce7;
  color: #15803d;
}

.status-pill.inactive {
  background: #f1f5f9;
  color: #64748b;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 14px;
  padding: 14px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-icon {
  color: #3b82f6;
  font-size: 22px;
}

.metric-item.has-pending .metric-icon {
  color: #d97706;
}

.metric-value {
  display: block;
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}

.metric-label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.card-footer-action {
  margin-top: 4px;
}

.btn-manage-club {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 700;
  font-size: 0.92rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* General Event Organization Cards */
.general-event-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 14px;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  transition: all 0.25s ease;
  height: 100%;
}

.general-event-card:hover {
  transform: translateY(-3px);
  border-color: #3b82f6;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.08);
}

.general-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.general-type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}

.general-event-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
  margin: 8px 0 6px;
  line-height: 1.3;
}

.general-event-desc {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.general-meta-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: #475569;
  font-weight: 600;
}

.meta-icon {
  font-size: 16px;
  color: #3b82f6;
}

.general-card-footer {
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
}

.capacity-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #475569;
  background: #f8fafc;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.card-content {
  padding: 8px 24px;
}

.club-item,
.event-item,
.request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 0;
  border-bottom: 1px solid #F1F5F9;
}

.club-item:last-child,
.event-item:last-child,
.request-item:last-child {
  border-bottom: none;
}

.club-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.club-icon {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F1F5F9;
  border-radius: 12px;
  font-size: 1.4rem;
}

.club-item h6,
.event-item h6,
.request-item h6 {
  margin: 0 0 4px;
  color: #1E293B;
  font-weight: 600;
}

.club-item span,
.event-item span,
.request-item span {
  color: #64748B;
  font-size: 0.85rem;
}

.view-btn,
.review-btn {
  flex-shrink: 0;
  padding: 7px 16px;
  border: none;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: 0.2s;
}

.view-btn {
  background: #EFF6FF;
  color: #2563EB;
}

.view-btn:hover {
  background: #2563EB;
  color: #fff;
}

.review-btn {
  background: #F0FDF4;
  color: #16A34A;
}

.review-btn:hover {
  background: #16A34A;
  color: #fff;
}

.event-date {
  flex-shrink: 0;
  padding: 7px 12px;
  background: #F8FAFC;
  border-radius: 8px;
  color: #475569;
  font-size: 0.85rem;
  font-weight: 500;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-dialog-custom {
  background: #fff;
  border-radius: 20px;
  width: 90%;
  max-width: 520px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.quick-chip {
  padding: 6px 14px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-chip:hover,
.quick-chip.active {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #2563eb;
}

.cursor-pointer {
  cursor: pointer;
}

.text-primary-hover {
  transition: color 0.2s ease;
}

.text-primary-hover:hover {
  color: #2563eb !important;
}
</style>