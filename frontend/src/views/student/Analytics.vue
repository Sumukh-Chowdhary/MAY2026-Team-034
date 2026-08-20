<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import StatCard from '@/components/admin/analytics/StatCard.vue'
import MembershipGrowthChart from '@/components/student/analytics/MembershipGrowthChart.vue'
import RoleDistributionChart from '@/components/student/analytics/RoleDistributionChart.vue'
import DepartmentBreakdownChart from '@/components/student/analytics/DepartmentBreakdownChart.vue'
import EventPerformanceChart from '@/components/student/analytics/EventPerformanceChart.vue'
import { getMyClubs, getClubAnalytics } from '@/api/clubs'
import { getCurrentUser } from '@/services/authService'

const loading = ref(true)
const error = ref('')
const organizedClubs = ref([])
const selectedClubId = ref(null)
const analytics = ref(null)

const currentUser = getCurrentUser()

const selectedClub = computed(() =>
  organizedClubs.value.find(c => c.id === selectedClubId.value) || null
)

async function loadOrganizedClubs() {
  loading.value = true
  error.value = ''

  try {
    const myClubs = await getMyClubs()

    // Only clubs where the current user appears in the organizers list
    organizedClubs.value = (myClubs || []).filter(club =>
      (club.organizers || []).some(org => org.id === currentUser?.id)
    )

    if (organizedClubs.value.length > 0) {
      selectedClubId.value = organizedClubs.value[0].id
      await loadAnalytics(selectedClubId.value)
    }
  } catch (err) {
    console.error(err)
    error.value = 'Could not load your clubs right now. Please try again.'
  } finally {
    loading.value = false
  }
}

async function loadAnalytics(clubId) {
  if (!clubId) return
  loading.value = true
  error.value = ''

  try {
    analytics.value = await getClubAnalytics(clubId)
  } catch (err) {
    console.error(err)
    error.value = 'Could not load analytics for this club.'
    analytics.value = null
  } finally {
    loading.value = false
  }
}

watch(selectedClubId, (newId) => {
  if (newId) loadAnalytics(newId)
})

onMounted(loadOrganizedClubs)
</script>

<template>
  <StudentLayout>
    <section class="analytics-page">
      <div class="page-header">
        <div>
          <h2>Club Analytics</h2>
          <p>Real membership and event insights for the clubs you organize.</p>
        </div>

        <select
          v-if="organizedClubs.length > 1"
          v-model="selectedClubId"
          class="form-select club-select"
        >
          <option v-for="club in organizedClubs" :key="club.id" :value="club.id">
            {{ club.name }}
          </option>
        </select>
      </div>

      <!-- Not an organizer of any club -->
      <div v-if="!loading && organizedClubs.length === 0" class="empty-panel">
        <i class="bi bi-bar-chart-line"></i>
        <h4>No clubs to show analytics for</h4>
        <p>Analytics are available once you're an organizer of a club. Ask your club to add you as an organizer, or check "My Roles".</p>
      </div>

      <div v-else-if="error" class="empty-panel error">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="loading" class="empty-panel">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <template v-else-if="analytics">
        <!-- Summary Stats -->
        <div class="row g-4">
          <div class="col-12 col-sm-6 col-xl-3">
            <StatCard label="Active Members" :value="analytics.membership.activeMembers" />
          </div>
          <div class="col-12 col-sm-6 col-xl-3">
            <StatCard label="Total Members (all-time)" :value="analytics.membership.totalMembers" />
          </div>
          <div class="col-12 col-sm-6 col-xl-3">
            <StatCard label="Total Events" :value="analytics.events.totalEvents" />
          </div>
          <div class="col-12 col-sm-6 col-xl-3">
            <StatCard label="Avg. Attendance Rate" :value="`${analytics.events.avgAttendanceRate}%`" />
          </div>
        </div>

        <!-- Membership Charts -->
        <div class="row g-4 mt-1">
          <div class="col-12 col-xl-8">
            <MembershipGrowthChart :growth="analytics.membership.growth" />
          </div>
          <div class="col-12 col-xl-4">
            <RoleDistributionChart :roles="analytics.membership.roleDistribution" />
          </div>
        </div>

        <div class="row g-4 mt-1">
          <div class="col-12 col-xl-6">
            <DepartmentBreakdownChart :departments="analytics.membership.departmentBreakdown" />
          </div>
          <div class="col-12 col-xl-6">
            <EventPerformanceChart :events="analytics.events.perEvent" />
          </div>
        </div>

        <!-- Event Breakdown Table -->
        <div class="row g-4 mt-1">
          <div class="col-12">
            <div class="analytics-card">
              <div class="card-header">
                <h4>Event Breakdown</h4>
                <p>Registration and attendance detail for every event this club has held</p>
              </div>

              <div class="table-responsive mt-3" v-if="analytics.events.perEvent.length">
                <table class="event-table">
                  <thead>
                    <tr>
                      <th>Event</th>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Registrations</th>
                      <th>Present</th>
                      <th>Attendance Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ev in analytics.events.perEvent" :key="ev.eventId">
                      <td>{{ ev.name }}</td>
                      <td>{{ ev.date }}</td>
                      <td><span class="status-pill">{{ ev.status }}</span></td>
                      <td>{{ ev.registrations }}</td>
                      <td>{{ ev.present }}</td>
                      <td>{{ ev.attendanceRate }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p v-else class="empty-state">No events recorded for this club yet.</p>
            </div>
          </div>
        </div>
      </template>
    </section>
  </StudentLayout>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 8px;
}

.page-header h2 {
  margin: 0;
  font-weight: 700;
  color: #1E293B;
}

.page-header p {
  margin: 4px 0 0;
  color: #64748B;
}

.club-select {
  max-width: 260px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  font-weight: 600;
  color: #1E293B;
}

.empty-panel {
  background: #ffffff;
  border-radius: 18px;
  padding: 60px 24px;
  text-align: center;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  margin-top: 24px;
}

.empty-panel i {
  font-size: 2.2rem;
  color: #94A3B8;
  margin-bottom: 12px;
  display: block;
}

.empty-panel.error i {
  color: #DC2626;
}

.empty-panel h4 {
  color: #1E293B;
  font-weight: 700;
}

.empty-panel p {
  color: #64748B;
  max-width: 420px;
  margin: 8px auto 0;
}

.analytics-card {
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

.event-table {
  width: 100%;
  border-collapse: collapse;
}

.event-table th {
  text-align: left;
  padding: 12px;
  color: #64748B;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-bottom: 1px solid #E2E8F0;
}

.event-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #F1F5F9;
  color: #1E293B;
}

.status-pill {
  background: #EFF6FF;
  color: #2563EB;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-state {
  color: #94A3B8;
  text-align: center;
  padding: 24px 0 0;
}
</style>
