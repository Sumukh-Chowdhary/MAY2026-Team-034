<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FacultyLayout from '@/layouts/FacultyLayout.vue'

import { getMySupervisedClubs, leaveFacultyRole } from '@/api/faculty'
import { getFacultyRequestsDashboard, approveRequest as apiApproveRequest, rejectRequest as apiRejectRequest } from '@/api/requests'

const router = useRouter()

// Dynamic Faculty assigned roles & requests
const facultyRoles = ref([])
const incomingRequests = ref([])
const loading = ref(true)

// Active Navigation States
const activeRoleView = ref(null)
const activeClubTab = ref('details') // 'details', 'members', 'events', 'alumni'

// User Profile Modal State
const showUserProfileModal = ref(false)
const selectedUserProfile = ref(null)

// Faculty Create Event Modal State
const showCreateEventModal = ref(false)
const newEventForm = ref({
  name: '',
  startDate: '',
  endDate: '',
  description: ''
})

// Assign Role Modal State
const showAssignRoleModal = ref(false)
const selectedStudentForAssign = ref(null)
const assignRoleInput = ref('')
const assignRoleDescInput = ref('')

const showRejectModal = ref(false)
const selectedRequestForReject = ref(null)
const rejectionReason = ref('')

onMounted(async () => {
  await loadFacultyRolesData()
})

async function loadFacultyRolesData() {
  loading.value = true
  try {
    const rolesData = await getMySupervisedClubs().catch(() => [])
    facultyRoles.value = Array.isArray(rolesData) ? rolesData : []

    const reqData = await getFacultyRequestsDashboard().catch(() => ({ data: {} }))
    incomingRequests.value = reqData?.data?.incomingRequests || []
  } catch (err) {
    console.error('Failed to load faculty roles data', err)
  } finally {
    loading.value = false
  }
}

function openFacultyDashboard(role) {
  activeRoleView.value = JSON.parse(JSON.stringify(role))
  activeClubTab.value = 'details'
}

function closeDashboard() {
  activeRoleView.value = null
}

async function handleLeaveFacultyRole(clubId) {
  if (confirm('Are you sure you want to step down from coordinating this club?')) {
    try {
      await leaveFacultyRole(clubId)
      alert('Successfully stepped down from club coordinator role.')
      await loadFacultyRolesData()
      closeDashboard()
    } catch (err) {
      alert('Failed to leave role.')
      console.error(err)
    }
  }
}

// User Profile View Trigger
function openUserProfile(student) {
  selectedUserProfile.value = student
  showUserProfileModal.value = true
}

// Separate Page Navigation for Event Details (strictly /faculty/events/:id)
function navigateToEventDetails(eventId) {
  router.push(`/faculty/events/${eventId}`)
}

// Faculty Event Creation
function submitFacultyCreateEvent() {
  if (!newEventForm.value.name.trim()) return alert('Please enter Event Name.')

  const newId = activeRoleView.value.events.length ? Math.max(...activeRoleView.value.events.map(e => e.id)) + 1 : 101
  const created = {
    id: newId,
    emoji: '🎉',
    name: newEventForm.value.name,
    title: newEventForm.value.name,
    club: activeRoleView.value.clubName,
    status: 'Active',
    startDate: newEventForm.value.startDate || '25 Jul 2026',
    endDate: newEventForm.value.endDate || '25 Jul 2026',
    description: newEventForm.value.description || 'New club event created by Faculty.'
  }

  activeRoleView.value.events.unshift({
    id: newId,
    title: created.name,
    club: created.club,
    status: 'Active',
    startDate: created.startDate,
    description: created.description
  })

  alert(`Event "${created.name}" created successfully!`)
  showCreateEventModal.value = false
  newEventForm.value = { name: '', startDate: '', endDate: '', description: '' }
}

// Assign Role (Faculty Only)
function triggerAssignRole(student) {
  selectedStudentForAssign.value = student
  assignRoleInput.value = ''
  assignRoleDescInput.value = ''
  showAssignRoleModal.value = true
}

function confirmAssignRole() {
  if (!assignRoleInput.value.trim()) return alert('Please enter role title.')
  selectedStudentForAssign.value.role = assignRoleInput.value.trim()
  alert(`Successfully assigned role "${assignRoleInput.value}" to ${selectedStudentForAssign.value.name}!`)
  showAssignRoleModal.value = false
}

// Remove Role (Faculty Only)
function handleRemoveRole(student) {
  if (confirm(`Are you sure you want to revoke the role from ${student.name}?`)) {
    student.role = 'Member'
  }
}

// Request Approvals
async function handleApproveRequest(reqId) {
  try {
    await apiApproveRequest(reqId)
    incomingRequests.value = incomingRequests.value.filter(r => r.id !== reqId)
    alert('Request approved successfully!')
  } catch (err) {
    alert('Failed to approve request.')
    console.error(err)
  }
}

function triggerRejectRequest(req) {
  selectedRequestForReject.value = req
  rejectionReason.value = ''
  showRejectModal.value = true
}

async function confirmRejectRequest() {
  if (!rejectionReason.value.trim()) return alert('Please enter rejection reason.')
  try {
    await apiRejectRequest(selectedRequestForReject.value.id, rejectionReason.value)
    incomingRequests.value = incomingRequests.value.filter(r => r.id !== selectedRequestForReject.value.id)
    alert('Request rejected successfully.')
    showRejectModal.value = false
  } catch (err) {
    alert('Failed to reject request.')
    console.error(err)
  }
}
</script>

<template>
  <FacultyLayout>
    <section class="roles-page">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h2>My Roles & Supervised Clubs</h2>
          <p>Supervise club coordinators, manage student roles, and review incoming requests.</p>
        </div>
      </div>

      <!-- Main Roles View -->
      <div v-if="!activeRoleView">
        
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading roles data...</p>
        </div>

        <div v-else>
          <!-- Managed Roles Grid -->
          <h4 class="fw-bold mb-3 text-dark">Assigned Club Roles</h4>
          
          <div v-if="facultyRoles.length === 0" class="card p-4 text-center text-muted mb-4 border-0 rounded-4 shadow-sm">
            You are not currently designated as a Faculty Coordinator for any active clubs.
          </div>

          <div v-else class="row g-4 mb-5">
            <div v-for="role in facultyRoles" :key="role.id" class="col-12 col-md-6">
              <div class="role-card">
                <div class="role-card-header">
                  <div class="role-icon">{{ role.emoji || '📌' }}</div>
                  <div>
                    <span class="role-badge">{{ role.roleTitle }}</span>
                    <h5 class="role-title">{{ role.clubName }}</h5>
                    <span class="text-secondary text-sm">{{ role.totalMembers }} Enrolled Members</span>
                  </div>
                </div>

                <p class="role-description">{{ role.description }}</p>

                <div class="role-card-footer">
                  <button class="btn btn-sm btn-outline-danger me-2 rounded-pill px-3" @click="handleLeaveFacultyRole(role.id)">
                    Leave Role
                  </button>
                  <button class="manage-btn" @click="openFacultyDashboard(role)">
                    View Management Dashboard
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Incoming Student Requests Review Queue -->
          <div class="card p-4 shadow-sm border-0 rounded-4">
            <h4 class="fw-bold mb-3">Incoming Student Requests</h4>
            <p class="text-secondary text-sm mb-4">Review club join applications, event proposals, and volunteer requests.</p>

            <div v-if="incomingRequests.length === 0" class="text-center py-4 text-secondary">
              No pending incoming requests.
            </div>

            <div v-else class="row g-3">
              <div v-for="req in incomingRequests" :key="req.id" class="col-12 col-md-4">
                <div class="p-3 border rounded-3 bg-white shadow-sm d-flex flex-column h-100">
                  <span class="badge bg-primary-subtle text-primary border mb-2 align-self-start">{{ req.requestType || req.ticketType || 'REQUEST' }}</span>
                  <h6 class="fw-bold m-0">{{ req.title || req.subject }}</h6>
                  <small class="text-secondary">Requester: {{ req.requesterName || req.requester?.name || 'Student' }}</small>
                  <p class="text-sm mt-2 text-dark flex-grow-1">{{ req.description || 'No additional details provided.' }}</p>
                  <div class="d-flex gap-2 mt-3">
                    <button class="btn btn-sm btn-success flex-fill rounded-pill" @click="handleApproveRequest(req.id)">Approve</button>
                    <button class="btn btn-sm btn-outline-danger flex-fill rounded-pill" @click="triggerRejectRequest(req)">Reject</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- ==================================================================== -->
      <!-- UNLOCKED FACULTY DASHBOARD VIEW                                      -->
      <!-- ==================================================================== -->
      <div v-if="activeRoleView" class="unlocked-dashboard">
        <!-- Banner -->
        <div class="dashboard-banner mb-4">
          <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
              <button class="back-btn" @click="closeDashboard">← Back to Roles</button>
              <div class="banner-emoji">{{ activeRoleView.emoji || '📌' }}</div>
              <div>
                <h3 class="m-0 text-dark font-bold">{{ activeRoleView.clubName }}</h3>
                <span class="badge bg-success px-3 py-1 mt-1">{{ activeRoleView.roleTitle }}</span>
              </div>
            </div>
            <button class="btn btn-outline-danger rounded-pill px-3" @click="handleLeaveFacultyRole(activeRoleView.id)">
              Leave Role
            </button>
          </div>
        </div>

        <!-- Clean Navigation Tabs -->
        <div class="detail-tabs mb-4">
          <button class="tab-option" :class="{ active: activeClubTab === 'details' }" @click="activeClubTab = 'details'">📌 Details</button>
          <button class="tab-option" :class="{ active: activeClubTab === 'members' }" @click="activeClubTab = 'members'">👥 Members</button>
          <button class="tab-option" :class="{ active: activeClubTab === 'events' }" @click="activeClubTab = 'events'">📅 Events</button>
        </div>

        <!-- Tab 1: Details -->
        <div v-if="activeClubTab === 'details'" class="card p-4 shadow-sm border-0 rounded-4">
          <h5 class="fw-bold mb-3">Club Details</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="info-box">
                <label>Co-Faculty Coordinators / Advisors</label>
                <p>{{ (activeRoleView.coCoordinators && activeRoleView.coCoordinators.length) ? activeRoleView.coCoordinators.join(', ') : 'None' }}</p>
              </div>
            </div>
            <div class="col-md-6">
              <div class="info-box">
                <label>Total Registered Members</label>
                <p>{{ activeRoleView.totalMembers }} Members</p>
              </div>
            </div>
            <div class="col-12">
              <div class="info-box">
                <label>Description</label>
                <p>{{ activeRoleView.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 2: Members & User Profiles -->
        <div v-if="activeClubTab === 'members'" class="card p-4 shadow-sm border-0 rounded-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold m-0">Student Members</h5>
              <span class="text-secondary text-sm">Click on any member's name to view profile.</span>
            </div>
          </div>

          <div v-if="!activeRoleView.assignedStudents || activeRoleView.assignedStudents.length === 0" class="py-4 text-center text-muted">
            No active student organizers or members listed.
          </div>

          <table v-else class="table table-hover align-middle">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Roll Number</th>
                <th>Branch</th>
                <th>Assigned Role</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="st in activeRoleView.assignedStudents" :key="st.id">
                <td>
                  <button class="btn btn-link text-decoration-none fw-semibold text-primary p-0" @click="openUserProfile(st)">
                    👤 {{ st.name }}
                  </button>
                </td>
                <td>{{ st.roll }}</td>
                <td>{{ st.branch }}</td>
                <td>
                  <span class="badge bg-primary-subtle text-primary border px-2 py-1">{{ st.role }}</span>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-light border me-2" @click="openUserProfile(st)">
                    View Profile
                  </button>
                  <button class="btn btn-sm btn-outline-success me-2" @click="triggerAssignRole(st)">
                    Assign Role
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Tab 3: Events -->
        <div v-if="activeClubTab === 'events'" class="card p-4 shadow-sm border-0 rounded-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h5 class="fw-bold m-0">Club Events</h5>
              <span class="text-secondary text-sm">Click on any event card to view details.</span>
            </div>
            <button class="btn btn-success font-semibold rounded-pill px-3" @click="showCreateEventModal = true">+ Create Event</button>
          </div>

          <div v-if="!activeRoleView.events || activeRoleView.events.length === 0" class="py-4 text-center text-muted">
            No events scheduled for this club.
          </div>

          <div v-else class="row g-3">
            <div v-for="ev in activeRoleView.events" :key="ev.id" class="col-md-6">
              <div class="event-card-item p-3 border rounded-3 bg-white shadow-sm" @click="navigateToEventDetails(ev.id)">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="m-0 fw-bold text-primary">{{ ev.name || ev.title }}</h6>
                  <span class="badge bg-success">{{ ev.status || 'Active' }}</span>
                </div>
                <p class="text-sm text-secondary mb-2 line-clamp-2">{{ ev.description || 'Club event' }}</p>
                <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                  <small class="text-muted">🗓️ {{ ev.startDate || 'Upcoming' }}</small>
                  <button class="btn btn-sm btn-outline-primary py-0 px-2" @click.stop="navigateToEventDetails(ev.id)">
                    View Event Details →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Modals -->
      <div v-if="showUserProfileModal && selectedUserProfile" class="modal-backdrop" @click.self="showUserProfileModal = false">
        <div class="modal-dialog-custom">
          <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
            <div class="d-flex align-items-center gap-3">
              <div class="profile-avatar-large">👤</div>
              <div>
                <h4 class="m-0 fw-bold text-dark">{{ selectedUserProfile.name }}</h4>
                <span class="badge bg-primary px-2 py-1 mt-1">{{ selectedUserProfile.role }}</span>
              </div>
            </div>
            <button class="close-btn" @click="showUserProfileModal = false">&times;</button>
          </div>

          <div class="row g-3">
            <div class="col-6">
              <div class="info-box">
                <label>Roll / Reg Number</label>
                <p>{{ selectedUserProfile.roll }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Department / Branch</label>
                <p>{{ selectedUserProfile.branch }}</p>
              </div>
            </div>
            <div class="col-6">
              <div class="info-box">
                <label>Campus Email</label>
                <p>{{ selectedUserProfile.email }}</p>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end mt-4">
            <button class="btn btn-secondary rounded-pill px-4" @click="showUserProfileModal = false">Close</button>
          </div>
        </div>
      </div>

      <!-- Reject Request Modal -->
      <div v-if="showRejectModal && selectedRequestForReject" class="modal-backdrop" @click.self="showRejectModal = false">
        <div class="modal-dialog-custom">
          <h4 class="fw-bold text-danger mb-2">Reject Request</h4>
          <p class="text-secondary text-sm mb-3">Rejecting: <strong>{{ selectedRequestForReject.title || selectedRequestForReject.subject }}</strong></p>

          <div class="mb-3">
            <label class="form-label font-semibold">Reason for Rejection</label>
            <textarea v-model="rejectionReason" class="form-control" rows="3" placeholder="State reason..."></textarea>
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-secondary rounded-pill" @click="showRejectModal = false">Cancel</button>
            <button class="btn btn-danger rounded-pill" @click="confirmRejectRequest">Confirm Rejection</button>
          </div>
        </div>
      </div>
    </section>
  </FacultyLayout>
</template>

<style scoped>
.roles-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  gap: 20px;
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

.role-badge {
  display: inline-block;
  background: #f0fdf4;
  color: #16a34a;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 999px;
  margin-bottom: 4px;
}

.role-title {
  margin: 0;
  color: #1e293b;
  font-weight: 700;
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

.manage-btn {
  padding: 8px 20px;
  background: #16a34a;
  border: none;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
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

.detail-tabs {
  display: flex;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 6px;
}

.tab-option {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  transition: 0.2s;
}

.tab-option.active {
  background: #16a34a;
  color: white;
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

.event-card-item {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
}

.profile-avatar-large {
  width: 54px;
  height: 54px;
  background: #eff6ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #94a3b8;
  cursor: pointer;
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
  max-width: 600px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}
</style>
