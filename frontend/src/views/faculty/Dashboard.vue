<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import StatCard from '@/components/admin/analytics/StatCard.vue'

import { getUser, updateUser } from '@/api/users'
import { getMySupervisedClubs } from '@/api/faculty'
import { getFacultyRequestsDashboard } from '@/api/requests'
import { getEvents } from '@/api/events'

const router = useRouter()

const userProfile = ref(null)
const managedClubs = ref([])
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
  { label: 'Pending Approvals', value: pendingRequests.value.length },
  { label: 'Upcoming Events', value: upcomingEvents.value.length },
  { label: 'Active Coordinators', value: managedClubs.value.reduce((acc, c) => acc + (c.assignedStudents?.length || 0), 0) }
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
            <i class="bi bi-person-gear me-1"></i> View / Edit Profile
          </button>
        </div>
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

        <!-- Managed Clubs Card -->
        <div class="col-12 col-lg-6">
          <div class="dashboard-card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div>
                <h5>Supervised Clubs</h5>
                <p>Clubs you currently manage or advise.</p>
              </div>
              <button class="btn btn-sm btn-link text-decoration-none fw-semibold" @click="navigateToRoles">View All Roles →</button>
            </div>

            <div class="card-content">
              <div v-if="managedClubs.length === 0" class="py-4 text-center text-muted">
                No supervised clubs assigned.
              </div>

              <div
                v-for="club in managedClubs"
                :key="club.id"
                class="club-item"
              >
                <div class="club-info">
                  <div class="club-icon">
                    {{ club.emoji || '📌' }}
                  </div>

                  <div>
                    <h6>{{ club.clubName }}</h6>
                    <span>{{ club.roleTitle }} · {{ club.totalMembers }} members</span>
                  </div>
                </div>

                <button class="view-btn" @click="navigateToRoles">Manage</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Events Card -->
        <div class="col-12 col-lg-6">
          <div class="dashboard-card">
            <div class="card-header">
              <h5>Upcoming Events</h5>
              <p>Upcoming events from your clubs.</p>
            </div>

            <div class="card-content">
              <div v-if="upcomingEvents.length === 0" class="py-4 text-center text-muted">
                No upcoming events scheduled.
              </div>

              <div
                v-for="event in upcomingEvents"
                :key="event.id"
                class="event-item"
              >
                <div>
                  <h6>{{ event.name || event.title }}</h6>
                  <span>{{ event.clubName || 'Campus Event' }}</span>
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
                <div class="avatar-lg bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 48px; height: 48px; font-size: 1.25rem;">
                  {{ (userProfile.fullName || userProfile.name || 'F').charAt(0).toUpperCase() }}
                </div>
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
</style>