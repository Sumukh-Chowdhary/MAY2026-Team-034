<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { useToast } from '@/composables/useToast'
import { isLegacyUser, LEGACY_READ_ONLY_MESSAGE } from '@/utils/permissions'

import { getUserAssignments, leaveAssignmentTicket } from '@/api/assignmentTickets'
import { createRequest } from '@/api/requests'
import { getClubs } from '@/api/student'

const router = useRouter()
const { showToast } = useToast()

const userStr = localStorage.getItem('user')
const currentUser = userStr ? JSON.parse(userStr) : null
const isLegacy = computed(() => isLegacyUser(currentUser))

function navigateToEventDetails(eventId) {
  router.push(`/student/events/${eventId}`)
}

// Student assignment tickets
const activeRoles = ref([])
const historyRoles = ref([])
const availableClubs = ref([])
const loading = ref(true)

// Navigation Tabs
const currentTab = ref('active') // 'active' | 'history'

// Modal & Form Controls
const activeRoleView = ref(null)
const showApplyModal = ref(false)
const applyForm = ref({
  requestType: 'BECOME_ORGANIZER',
  clubId: '',
  title: '',
  description: '',
  priority: 'MEDIUM'
})
const submittingApply = ref(false)

onMounted(async () => {
  await loadStudentRolesData()
})

async function loadStudentRolesData() {
  loading.value = true
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      const res = await getUserAssignments(user.id).catch(() => ({ data: {} }))
      activeRoles.value = res?.data?.active || []
      historyRoles.value = res?.data?.history || []
    }

    const clubsRes = await getClubs().catch(() => [])
    availableClubs.value = Array.isArray(clubsRes) ? clubsRes : []
  } catch (err) {
    console.error('Failed to load student roles', err)
  } finally {
    loading.value = false
  }
}

function openRoleDashboard(role) {
  activeRoleView.value = JSON.parse(JSON.stringify(role))
}

function closeDashboard() {
  activeRoleView.value = null
}

async function handleLeaveStudentRole(ticketId) {
  if (confirm('Are you sure you want to step down from this role?')) {
    try {
      await leaveAssignmentTicket(ticketId)
      alert('Successfully stepped down from role.')
      await loadStudentRolesData()
      closeDashboard()
    } catch (err) {
      alert('Failed to leave role.')
      console.error(err)
    }
  }
}

function openApplyModal() {
  if (isLegacy.value) {
    showToast('Your student account is now read-only because your student lifecycle is marked Legacy.', 'warning')
    return
  }
  applyForm.value = {
    requestType: 'BECOME_ORGANIZER',
    clubId: availableClubs.value.length ? availableClubs.value[0].id : '',
    title: '',
    description: '',
    priority: 'MEDIUM'
  }
  showApplyModal.value = true
}

async function handleApplySubmit() {
  if (!applyForm.value.title.trim()) return alert('Please enter a request title.')
  if (!applyForm.value.clubId) return alert('Please select a target club.')

  submittingApply.value = true
  try {
    const selectedClub = availableClubs.value.find(c => c.id === parseInt(applyForm.value.clubId))
    const payload = {
      requestType: applyForm.value.requestType,
      title: applyForm.value.title.trim(),
      description: applyForm.value.description.trim(),
      priority: applyForm.value.priority,
      referenceType: 'CLUB',
      referenceId: parseInt(applyForm.value.clubId),
      referenceName: selectedClub ? (selectedClub.name || selectedClub.clubName) : 'Club'
    }

    await createRequest(payload)
    alert('Role request submitted successfully! Sent to club faculty coordinator for approval.')
    showApplyModal.value = false
    await loadStudentRolesData()
  } catch (err) {
    alert('Failed to submit role request.')
    console.error(err)
  } finally {
    submittingApply.value = false
  }
}
</script>

<template>
  <StudentLayout>
    <section class="roles-page">
      <!-- Header -->
      <div class="page-header d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
          <h2>My Assigned Roles</h2>
          <p>View your active roles, track role history, step down, or apply for new roles.</p>
        </div>

        <button class="btn btn-primary fw-semibold px-4 rounded-pill shadow-sm" @click="openApplyModal">
          <i class="bi bi-plus-lg me-1"></i> Apply for Role Request
        </button>
      </div>

      <!-- Tab Toggle Bar -->
      <div class="tab-toggle-bar mb-4">
        <button 
          class="toggle-btn" 
          :class="{ active: currentTab === 'active' }"
          @click="currentTab = 'active'"
        >
          <i class="bi bi-shield-check me-2"></i> Active Roles
          <span class="count-badge">{{ activeRoles.length }}</span>
        </button>

        <button 
          class="toggle-btn" 
          :class="{ active: currentTab === 'history' }"
          @click="currentTab = 'history'"
        >
          <i class="bi bi-clock-history me-2"></i> Role History
          <span class="count-badge text-muted">{{ historyRoles.length }}</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading assigned roles...</p>
      </div>

      <div v-else-if="!activeRoleView">
        
        <!-- Tab A: Active Roles Grid -->
        <div v-if="currentTab === 'active'">
          <div v-if="activeRoles.length === 0" class="empty-state-card">
            <div class="empty-icon">🛡️</div>
            <h3>No Active Role Assignments</h3>
            <p>You currently hold no active organizer or volunteer roles. Click "Apply for Role Request" to submit an application to a club faculty coordinator!</p>
          </div>

          <div v-else class="row g-4">
            <div
              v-for="role in activeRoles"
              :key="role.id"
              class="col-12 col-md-6"
            >
              <div class="role-card">
                <div class="role-card-header">
                  <div class="role-icon">🛡️</div>
                  <div>
                    <span class="role-type-badge active">{{ role.assignmentRole }}</span>
                    <h5 
                      class="role-title clickable-club" 
                      @click="role.referenceId ? router.push(`/student/clubs/${role.referenceId}`) : router.push('/student/clubs')"
                      :title="`Go to ${role.referenceName || 'Club'} page`"
                    >
                      {{ role.referenceName || 'Club Role' }}
                      <i class="bi bi-box-arrow-up-right text-xs ms-1"></i>
                    </h5>
                    <span class="assigned-date">Granted: {{ new Date(role.grantedAt || role.startsAt || Date.now()).toLocaleDateString() }}</span>
                  </div>
                </div>

                <p class="role-description">
                  Holding {{ role.assignmentRole }} position for 
                  <RouterLink 
                    :to="role.referenceId ? `/student/clubs/${role.referenceId}` : '/student/clubs'" 
                    class="text-primary fw-semibold text-decoration-none"
                  >
                    {{ role.referenceName || 'Club' }}
                  </RouterLink>.
                </p>

                <div class="role-card-footer">
                  <button class="btn btn-sm btn-outline-danger rounded-pill px-3" @click="handleLeaveStudentRole(role.id)">
                    Leave Role
                  </button>
                  <button class="view-btn" @click="openRoleDashboard(role)">
                    View Role Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab B: Role History Grid -->
        <div v-else-if="currentTab === 'history'">
          <div v-if="historyRoles.length === 0" class="empty-state-card">
            <div class="empty-icon">📜</div>
            <h3>No Role History Found</h3>
            <p>Your historical past or stepped-down role records will appear here.</p>
          </div>

          <div v-else class="row g-4">
            <div
              v-for="role in historyRoles"
              :key="role.id"
              class="col-12 col-md-6"
            >
              <div class="role-card opacity-75">
                <div class="role-card-header">
                  <div class="role-icon bg-light text-muted">📜</div>
                  <div>
                    <span class="role-type-badge history">{{ role.status || 'INACTIVE' }}</span>
                    <h5 
                      class="role-title text-secondary clickable-club" 
                      @click="role.referenceId ? router.push(`/student/clubs/${role.referenceId}`) : router.push('/student/clubs')"
                      :title="`Go to ${role.referenceName || 'Club'} page`"
                    >
                      {{ role.referenceName || 'Past Role' }}
                      <i class="bi bi-box-arrow-up-right text-xs ms-1"></i>
                    </h5>
                    <span class="assigned-date">Role: {{ role.assignmentRole }}</span>
                  </div>
                </div>

                <p class="role-description text-muted">
                  Former {{ role.assignmentRole }} position for {{ role.referenceName }}. Status: {{ role.status }}.
                </p>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Unlocked Role Detail View -->
      <div v-if="activeRoleView" class="unlocked-dashboard">
        <div class="dashboard-banner mb-4">
          <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div class="d-flex align-items-center gap-3">
              <button class="back-btn" @click="closeDashboard">← Back to Roles</button>
              <div class="banner-emoji">🛡️</div>
              <div>
                <h3 
                  class="m-0 text-dark font-bold clickable-club" 
                  @click="activeRoleView.referenceId ? router.push(`/student/clubs/${activeRoleView.referenceId}`) : router.push('/student/clubs')"
                  :title="`Open ${activeRoleView.referenceName} club page`"
                >
                  {{ activeRoleView.referenceName }}
                  <i class="bi bi-box-arrow-up-right text-xs ms-1"></i>
                </h3>
                <span class="badge bg-primary px-3 py-1 mt-1">{{ activeRoleView.assignmentRole }}</span>
              </div>
            </div>

            <button class="btn btn-outline-danger rounded-pill px-4" @click="handleLeaveStudentRole(activeRoleView.id)">
              Leave Role
            </button>
          </div>
        </div>

        <div class="card p-4 border-0 rounded-4 shadow-sm">
          <h5 class="fw-bold mb-3">Role Details</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="info-box">
                <label>Assigned Role</label>
                <p>{{ activeRoleView.assignmentRole }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="info-box">
                <label>Target Entity / Club</label>
                <p>
                  <RouterLink 
                    :to="activeRoleView.referenceId ? `/student/clubs/${activeRoleView.referenceId}` : '/student/clubs'" 
                    class="text-primary text-decoration-none fw-bold"
                  >
                    {{ activeRoleView.referenceName }}
                    <i class="bi bi-box-arrow-up-right ms-1"></i>
                  </RouterLink>
                </p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="info-box">
                <label>Duration Type</label>
                <p>{{ activeRoleView.durationType || 'INDEFINITE' }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="info-box">
                <label>Assignment Status</label>
                <p><span class="badge bg-success">{{ activeRoleView.status }}</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Apply for Role Modal -->
      <div v-if="showApplyModal" class="modal-backdrop" @click.self="showApplyModal = false">
        <div class="modal-dialog-custom">
          <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
            <h4 class="fw-bold m-0 text-dark">
              <i class="bi bi-shield-plus text-primary me-2"></i>Apply for Role Request
            </h4>
            <button class="btn-close" @click="showApplyModal = false"></button>
          </div>

          <form @submit.prevent="handleApplySubmit">
            <div class="mb-3">
              <label class="form-label font-semibold">Desired Role Type</label>
              <select v-model="applyForm.requestType" class="form-select" required>
                <option value="BECOME_ORGANIZER">Club Organizer</option>
                <option value="BECOME_VOLUNTEER">Event Volunteer</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label font-semibold">Target Club</label>
              <select v-model="applyForm.clubId" class="form-select" required>
                <option v-for="c in availableClubs" :key="c.id" :value="c.id">
                  {{ c.name || c.clubName }} ({{ c.category || 'Club' }})
                </option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label font-semibold">Request Title</label>
              <input v-model="applyForm.title" type="text" class="form-control" placeholder="e.g. Application for AI Club Organizer" required />
            </div>

            <div class="mb-3">
              <label class="form-label font-semibold">Reason / Statement</label>
              <textarea v-model="applyForm.description" class="form-control" rows="3" placeholder="Describe why you want to apply for this role..."></textarea>
            </div>

            <div class="d-flex justify-content-end gap-2 pt-2 border-top">
              <button type="button" class="btn btn-secondary rounded-pill px-4" @click="showApplyModal = false">Cancel</button>
              <button type="submit" class="btn btn-primary rounded-pill px-4" :disabled="submittingApply">
                {{ submittingApply ? 'Submitting...' : 'Submit Request' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  </StudentLayout>
</template>

<style scoped>
.roles-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.75rem;
  font-weight: 700;
}

.page-header p {
  margin: 7px 0 0;
  color: #64748b;
  font-size: 0.95rem;
}

.tab-toggle-bar {
  display: flex;
  gap: 12px;
  background: #f8fafc;
  padding: 6px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  width: fit-content;
}

.toggle-btn {
  border: none;
  background: transparent;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 600;
  color: #64748b;
  transition: 0.2s;
}

.toggle-btn.active {
  background: #fff;
  color: #2563eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.count-badge {
  background: #eff6ff;
  color: #2563eb;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.8rem;
  margin-left: 6px;
}

.empty-state-card {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.role-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-icon {
  width: 52px;
  height: 52px;
  background: #f1f5f9;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
}

.role-type-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
  margin-bottom: 4px;
}

.role-type-badge.active {
  background: #eff6ff;
  color: #2563eb;
}

.role-type-badge.history {
  background: #f1f5f9;
  color: #64748b;
}

.role-title {
  margin: 0;
  color: #1e293b;
  font-weight: 700;
}

.assigned-date {
  color: #64748b;
  font-size: 0.85rem;
}

.role-description {
  color: #475569;
  font-size: 0.92rem;
  margin: 16px 0;
  flex: 1;
}

.role-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

.view-btn {
  padding: 7px 18px;
  background: #eff6ff;
  color: #2563eb;
  border: none;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.85rem;
}

.view-btn:hover {
  background: #2563eb;
  color: #fff;
}

.dashboard-banner {
  background: #fff;
  border-radius: 20px;
  padding: 20px 24px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
}

.back-btn {
  background: #f1f5f9;
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  color: #475569;
  font-weight: 600;
}

.banner-emoji {
  font-size: 2rem;
}

.info-box {
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 14px;
  padding: 16px 20px;
}

.info-box label {
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 600;
}

.info-box p {
  margin: 4px 0 0;
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
  max-width: 540px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.clickable-club {
  cursor: pointer;
  transition: color 0.2s ease;
}

.clickable-club:hover {
  color: #2563eb !important;
  text-decoration: underline;
}
</style>
