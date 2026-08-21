<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'

import StatCard from '@/components/admin/analytics/StatCard.vue'
import UserDistributionChart from '@/components/admin/analytics/UserDistributionChart.vue'
import ClubMembershipChart from '@/components/admin/analytics/ClubMembershipChart.vue'
import PlatformActivityChart from '@/components/admin/analytics/PlatformActivityChart.vue'

import { getAdminAnalytics } from '@/api/admin'
import {
  dashboardStats as defaultStats,
  userDistribution as defaultUserDistribution,
  clubMembership as defaultClubMembership,
  platformActivity as defaultPlatformActivity,
  departmentDistribution as defaultDeptDistribution,
  recentActivities as defaultRecentActivities
} from '@/data/analytics.js'

const router = useRouter()

const stats = ref([...defaultStats])
const userDist = ref({ ...defaultUserDistribution })
const clubMem = ref({ ...defaultClubMembership })
const platformAct = ref({ ...defaultPlatformActivity })
const deptDist = ref({ ...defaultDeptDistribution })
const recentActs = ref([...defaultRecentActivities])
const loading = ref(false)

async function fetchLiveAnalytics() {
  try {
    loading.value = true
    const data = await getAdminAnalytics()
    if (data) {
      if (data.dashboardStats) stats.value = data.dashboardStats
      if (data.userDistribution) userDist.value = data.userDistribution
      if (data.clubMembership) clubMem.value = data.clubMembership
      if (data.platformActivity) platformAct.value = data.platformActivity
      if (data.departmentDistribution) deptDist.value = data.departmentDistribution
      if (data.recentActivities && data.recentActivities.length) recentActs.value = data.recentActivities
    }
  } catch (e) {
    // Graceful fallback to rich seed defaults
    console.info('Using seed analytics data')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLiveAnalytics()
})
</script>

<template>
  <AdminLayout>
    <section class="dashboard-page">

      <div class="dashboard-header d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
        <div>
          <h2>Admin Analytics Dashboard</h2>
          <p>
            Monitor platform engagement, active clubs, registrations, and member distribution.
          </p>
        </div>
        <div class="d-flex align-items-center gap-2">
          <button 
            class="btn btn-outline-primary btn-sm px-3 rounded-pill fw-semibold shadow-xs" 
            :disabled="loading"
            @click="fetchLiveAnalytics"
          >
            <i class="bi" :class="loading ? 'bi-arrow-clockwise spin' : 'bi-arrow-clockwise'"></i>
            {{ loading ? 'Refreshing...' : 'Refresh Analytics' }}
          </button>
        </div>
      </div>

      <!-- Quick Nav Shortcuts -->
      <div class="quick-nav-bar d-flex align-items-center gap-2 mb-4 overflow-x-auto pb-1">
        <button class="quick-chip active" @click="router.push('/admin')">
          <i class="bi bi-speedometer2 me-1"></i> Overview
        </button>
        <button class="quick-chip" @click="router.push('/admin/clubs')">
          <i class="bi bi-collection-fill me-1 text-primary"></i> Clubs
        </button>
        <button class="quick-chip" @click="router.push('/admin/events')">
          <i class="bi bi-calendar-event-fill me-1 text-success"></i> Events
        </button>
        <button class="quick-chip" @click="router.push('/admin/requests')">
          <i class="bi bi-inbox-fill me-1 text-warning"></i> Requests
        </button>
        <button class="quick-chip" @click="router.push('/admin/users')">
          <i class="bi bi-people-fill me-1 text-info"></i> Users
        </button>
        <button class="quick-chip" @click="router.push('/admin/venues')">
          <i class="bi bi-geo-alt-fill me-1 text-danger"></i> Venues
        </button>
      </div>

      <!-- Summary Statistics Grid -->
      <div class="row g-3 mb-4">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="col-12 col-sm-6 col-lg-4 col-xl-2"
        >
          <StatCard
            :label="stat.label"
            :value="stat.value"
            :icon="stat.icon"
            :trend="stat.trend"
          />
        </div>
      </div>

      <!-- Main Analytics Charts -->
      <div class="row g-4 mb-4">
        <div class="col-12 col-xl-8">
          <PlatformActivityChart :activity="platformAct" />
        </div>

        <div class="col-12 col-xl-4">
          <UserDistributionChart :distribution="userDist" />
        </div>
      </div>

      <!-- Club & Activity Analytics -->
      <div class="row g-4">
        <div class="col-12 col-xl-7">
          <ClubMembershipChart :membership="clubMem" />
        </div>

        <!-- Recent System Activity Feed -->
        <div class="col-12 col-xl-5">
          <div class="analytics-card">
            <div class="card-header d-flex justify-content-between align-items-center mb-3">
              <div>
                <h4>Recent Platform Activity</h4>
                <p>Live events, registrations & role updates</p>
              </div>
              <RouterLink to="/admin/requests" class="badge bg-success-subtle text-success border px-2.5 py-1 text-decoration-none hover-badge">
                View All <i class="bi bi-arrow-right ms-1"></i>
              </RouterLink>
            </div>

            <div class="activity-list d-flex flex-column gap-3 mt-3">
              <div
                v-for="act in recentActs"
                :key="act.id"
                class="activity-item d-flex align-items-start gap-3 p-3 rounded-3 cursor-pointer"
                @click="router.push('/admin/requests')"
                :title="'Click to view in Requests'"
              >
                <div class="activity-icon">{{ act.icon || '📌' }}</div>
                <div class="flex-grow-1">
                  <div class="d-flex justify-content-between align-items-center">
                    <p class="m-0 fw-semibold text-dark text-sm">{{ act.text }}</p>
                    <span class="badge bg-light text-secondary border text-xs">{{ act.badge || act.type || 'Activity' }}</span>
                  </div>
                  <small class="text-secondary">{{ act.time }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </section>
  </AdminLayout>
</template>

<style scoped>
.dashboard-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-header h2 {
  margin: 0;
  color: #1E293B;
  font-size: 1.75rem;
  font-weight: 800;
}

.dashboard-header p {
  margin: 6px 0 0;
  color: #64748B;
  font-size: 0.95rem;
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

.analytics-card {
  height: 100%;
  background: #ffffff;
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.card-header h4 {
  margin: 0;
  color: #1E293B;
  font-size: 1.15rem;
  font-weight: 700;
}

.card-header p {
  margin: 6px 0 0;
  color: #64748B;
  font-size: 0.9rem;
}

.activity-item {
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: #eff6ff;
  border-color: #dbeafe;
  transform: translateX(2px);
}

.activity-icon {
  font-size: 1.25rem;
}

.text-xs {
  font-size: 0.75rem;
}

.cursor-pointer {
  cursor: pointer;
}

.spin {
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .dashboard-header h2 {
    font-size: 1.5rem;
  }
}
</style>