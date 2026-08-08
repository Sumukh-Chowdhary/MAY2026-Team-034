<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FacultyLayout from '@/layouts/FacultyLayout.vue'

import { getMySupervisedClubs, getFacultyGeneralEvents, leaveFacultyRole } from '@/api/faculty'
import { getFacultyRequestsDashboard, approveRequest as apiApproveRequest, rejectRequest as apiRejectRequest } from '@/api/requests'
import { useToast } from '@/composables/useToast'

const { showToast } = useToast()
const router = useRouter()

// Dynamic Faculty assigned roles & requests
const facultyRoles = ref([])
const generalEvents = ref([])
const incomingRequests = ref([])
const completedRolesCount = ref(5)
const loading = ref(true)

// Active Responsibilities Search & Navigation
const searchQuery = ref('')

function navigateToRoleHistory() {
  router.push('/faculty/roles/history')
}

function navigateToClub(clubId) {
  router.push(`/faculty/clubs/${clubId}`)
}

// Filtered Active Lists (Active Only)
const filteredFacultyRoles = computed(() => {
  if (!searchQuery.value.trim()) return facultyRoles.value
  const query = searchQuery.value.toLowerCase()
  return facultyRoles.value.filter(r =>
    (r.clubName || '').toLowerCase().includes(query) ||
    (r.roleTitle || '').toLowerCase().includes(query)
  )
})

const filteredGeneralEvents = computed(() => {
  if (!searchQuery.value.trim()) return generalEvents.value
  const query = searchQuery.value.toLowerCase()
  return generalEvents.value.filter(e =>
    (e.name || e.title || '').toLowerCase().includes(query) ||
    (e.role || '').toLowerCase().includes(query)
  )
})

// Active Navigation States
const activeRoleView = ref(null)
const showDetailModal = ref(false)
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
    const [supervisedClubs, myGenEvents, reqsData] = await Promise.all([
      getMySupervisedClubs().catch(() => []),
      getFacultyGeneralEvents().catch(() => []),
      getFacultyRequestsDashboard().catch(() => ({ requests: [] }))
    ])

    facultyRoles.value = (supervisedClubs || []).map(club => ({
      id: club.id,
      clubId: club.id,
      clubName: club.clubName || 'Campus Club',
      roleTitle: club.roleTitle || 'Faculty Coordinator',
      status: club.status || 'Active',
      startDate: 'Aug 2025',
      logo: club.logo || 'groups',
      category: club.category || 'General',
      activeMembersCount: club.memberCount || 0,
      totalEventsCount: club.eventCount || 0,
      pendingRequestsCount: club.pendingRequestsCount || 0,
      assignedStudents: club.assignedStudents || [],
      events: (club.events || []).map(ev => ({
        id: ev.id,
        title: ev.name,
        club: club.clubName,
        status: ev.status || 'Active',
        startDate: 'Upcoming',
        description: `Event organized under ${club.clubName}.`
      }))
    }))

    generalEvents.value = (myGenEvents || []).map(ev => ({
      id: ev.id,
      name: ev.name || ev.event_name || 'General Event',
      role: 'Event Organizer',
      status: ev.status || 'Active',
      startDate: ev.startDate || 'Upcoming',
      logo: 'star'
    }))

    incomingRequests.value = reqsData.requests || reqsData || []
  } catch (err) {
    console.error('Failed to load faculty dashboard roles:', err)
  } finally {
    loading.value = false
  }
}

function openDashboard(role) {
  activeRoleView.value = role
  showDetailModal.value = true
}

const showLeaveRoleModal = ref(false)
const selectedRoleForLeave = ref(null)

function closeDashboard() {
  showDetailModal.value = false
  activeRoleView.value = null
}

function triggerLeaveRole(role) {
  selectedRoleForLeave.value = role
  showLeaveRoleModal.value = true
}

async function confirmLeaveRole() {
  if (!selectedRoleForLeave.value) return
  try {
    await leaveFacultyRole(selectedRoleForLeave.value.id || selectedRoleForLeave.value.clubId)
    showToast(`Successfully stepped down from role for ${selectedRoleForLeave.value.clubName}.`, 'success')
    await loadFacultyRolesData()
    showLeaveRoleModal.value = false
    closeDashboard()
  } catch (err) {
    showToast('Failed to leave role.', 'error')
    console.error(err)
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
  if (!newEventForm.value.name.trim()) return showToast('Please enter Event Name.', 'warning')

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

  showToast(`Event "${created.name}" created successfully!`, 'success')
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
  if (!assignRoleInput.value.trim()) return showToast('Please enter role title.', 'warning')
  selectedStudentForAssign.value.role = assignRoleInput.value.trim()
  showToast(`Successfully assigned role "${assignRoleInput.value}" to ${selectedStudentForAssign.value.name}!`, 'success')
  showAssignRoleModal.value = false
}

// Remove Role (Faculty Only)
function handleRemoveRole(student) {
  student.role = 'Member'
  showToast(`Revoked role from ${student.name}.`, 'info')
}

// Request Approvals
async function handleApproveRequest(reqId) {
  try {
    await apiApproveRequest(reqId)
    incomingRequests.value = incomingRequests.value.filter(r => r.id !== reqId)
    showToast('Request approved successfully!', 'success')
  } catch (err) {
    showToast('Failed to approve request.', 'error')
    console.error(err)
  }
}

function triggerRejectRequest(req) {
  selectedRequestForReject.value = req
  rejectionReason.value = ''
  showRejectModal.value = true
}

async function confirmRejectRequest() {
  if (!rejectionReason.value.trim()) return showToast('Please enter rejection reason.', 'warning')
  try {
    await apiRejectRequest(selectedRequestForReject.value.id, rejectionReason.value)
    incomingRequests.value = incomingRequests.value.filter(r => r.id !== selectedRequestForReject.value.id)
    showToast('Request rejected successfully.', 'success')
    showRejectModal.value = false
  } catch (err) {
    showToast('Failed to reject request.', 'error')
    console.error(err)
  }
}
</script>

<template>
  <FacultyLayout>
    <section class="roles-page">
      <!-- Page Header (STEP 1) -->
      <div class="page-header mb-4">
        <div>
          <h2>Faculty Responsibilities</h2>
          <p>Supervise club activities, lead institutional events, and track past responsibilities.</p>
        </div>
      </div>

      <!-- Dashboard Statistics Grid (STEP 6) -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="stat-mini-card">
            <div class="stat-icon bg-primary-subtle text-primary">
              <span class="material-symbols-rounded">groups</span>
            </div>
            <div>
              <div class="stat-num">{{ facultyRoles.length }}</div>
              <div class="stat-lbl">Current Clubs</div>
            </div>
          </div>
        </div>

        <div class="col-6 col-md-3">
          <div class="stat-mini-card">
            <div class="stat-icon bg-purple-subtle text-purple">
              <span class="material-symbols-rounded">campaign</span>
            </div>
            <div>
              <div class="stat-num">{{ generalEvents.length }}</div>
              <div class="stat-lbl">General Events</div>
            </div>
          </div>
        </div>

        <div class="col-6 col-md-3">
          <div class="stat-mini-card">
            <div class="stat-icon bg-warning-subtle text-warning">
              <span class="material-symbols-rounded">pending_actions</span>
            </div>
            <div>
              <div class="stat-num">{{ incomingRequests.length }}</div>
              <div class="stat-lbl">Pending Requests</div>
            </div>
          </div>
        </div>

        <div class="col-6 col-md-3">
          <div class="stat-mini-card cursor-pointer" @click="navigateToRoleHistory">
            <div class="stat-icon bg-success-subtle text-success">
              <span class="material-symbols-rounded">history</span>
            </div>
            <div>
              <div class="stat-num">{{ completedRolesCount }}</div>
              <div class="stat-lbl">Completed Roles</div>
            </div>
          </div>
        </div>
      </div>      <!-- Filter Toolbar (Active Only) -->
      <div class="filter-toolbar-card mb-4">
        <div class="row g-3 align-items-center justify-content-between">
          <!-- Search -->
          <div class="col-12 col-md-8">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0 text-muted">
                <span class="material-symbols-rounded icon-sm">search</span>
              </span>
              <input
                v-model="searchQuery"
                type="text"
                class="form-control border-start-0 ps-0"
                placeholder="Search active clubs or general events..."
              />
            </div>
          </div>

          <!-- View History Button -->
          <div class="col-12 col-md-4 text-md-end">
            <button class="btn btn-outline-primary rounded-pill px-4 font-semibold text-sm d-inline-flex align-items-center gap-1.5" @click="navigateToRoleHistory">
              <span class="material-symbols-rounded icon-sm">history</span>
              View Role History
            </button>
          </div>
        </div>
      </div>

      <!-- Main Roles View (Active Only) -->
      <div v-if="!activeRoleView">
        
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading active responsibilities...</p>
        </div>

        <div v-else>
          <!-- SECTION 1: Club Coordination -->
          <div class="assignment-section mb-5">
            <div class="section-header-bar mb-3">
              <div class="d-flex align-items-center gap-2">
                <span class="material-symbols-rounded text-primary icon-md">groups</span>
                <h4 class="fw-bold m-0 text-dark">Club Coordination</h4>
              </div>
              <p class="text-muted text-sm m-0 ms-1">Clubs you currently supervise and manage.</p>
            </div>
            
            <div v-if="filteredFacultyRoles.length === 0" class="card p-4 text-center text-muted border-0 rounded-4 shadow-sm">
              No active club coordination roles match your current search.
            </div>

            <div v-else class="row g-3">
              <div v-for="role in filteredFacultyRoles" :key="role.id" class="col-12 col-md-6 col-xl-4">
                <div class="compact-assignment-card">
                  <!-- Header: Title + Active Badge + Overflow Menu -->
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <div class="d-flex align-items-center gap-2">
                      <h5 class="assignment-title m-0">{{ role.clubName }}</h5>
                      <span class="status-pill-subtle">Active</span>
                    </div>

                    <!-- Overflow Menu Dropdown -->
                    <div class="dropdown">
                      <button class="btn btn-sm btn-icon-ghost text-muted p-1 rounded-circle" type="button" data-bs-toggle="dropdown" aria-expanded="false" title="More options">
                        <span class="material-symbols-rounded icon-sm">more_vert</span>
                      </button>
                      <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 text-xs">
                        <li>
                          <a class="dropdown-item d-flex align-items-center gap-2 py-1.5" href="#" @click.prevent="navigateToClub(role.id)">
                            <span class="material-symbols-rounded icon-xs text-primary">visibility</span>
                            View Club Details
                          </a>
                        </li>
                        <li><hr class="dropdown-divider my-1"></li>
                        <li>
                          <a class="dropdown-item d-flex align-items-center gap-2 py-1.5 text-danger" href="#" @click.prevent="triggerLeaveRoleModal(role)">
                            <span class="material-symbols-rounded icon-xs text-danger">no_accounts</span>
                            Leave Role
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <!-- Simplified Info Rows -->
                  <div class="simplified-info-stack my-2">
                    <div class="info-line-clean">
                      <span class="material-symbols-rounded icon-xs text-secondary">groups</span>
                      <span>{{ role.memberCount || role.totalMembers || 1 }} Members</span>
                    </div>
                    <div class="info-line-clean">
                      <span class="material-symbols-rounded icon-xs text-secondary">event</span>
                      <span class="text-truncate">{{ role.events?.[0]?.name || role.nextEvent?.name || 'AI Hack Sprint' }}</span>
                    </div>
                    <div class="info-line-clean">
                      <span class="material-symbols-rounded icon-xs text-secondary">location_on</span>
                      <span class="text-truncate">{{ role.events?.[0]?.venueName || role.primaryVenue || 'Innovation Lab' }}</span>
                    </div>

                    <!-- Highlighted Warning Chip when Pending > 0 -->
                    <div v-if="(role.pendingRequestsCount || 0) > 0" class="pending-warning-chip mt-2">
                      <span class="material-symbols-rounded icon-xs text-warning">warning</span>
                      <span>{{ role.pendingRequestsCount }} Pending Request(s)</span>
                    </div>
                  </div>

                  <!-- Primary Action -->
                  <div class="card-footer-clean pt-2 mt-auto">
                    <button class="btn-manage-club-compact w-100 justify-content-center" @click="navigateToClub(role.id)">
                      Manage Club
                      <span class="material-symbols-rounded icon-sm">arrow_forward</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- SECTION 2: General Event Organization -->
          <div class="assignment-section mb-5">
            <div class="section-header-bar mb-3">
              <div class="d-flex align-items-center gap-2">
                <span class="material-symbols-rounded text-primary icon-md">account_balance</span>
                <h4 class="fw-bold m-0 text-dark">General Event Organization</h4>
              </div>
              <p class="text-muted text-sm m-0 ms-1">College-wide institutional events (Orientation, Convocation, Placement Drive, Blood Donation Camp).</p>
            </div>

            <div v-if="filteredGeneralEvents.length === 0" class="card p-4 text-center text-muted border-0 rounded-4 shadow-sm">
              No general college events match your current search.
            </div>

            <div v-else class="row g-3">
              <div v-for="event in filteredGeneralEvents" :key="event.id" class="col-12 col-md-6 col-xl-3">
                <div class="compact-assignment-card" style="min-width: 0;">
                  <!-- Header: Three-dot menu + Title stacked + Purple Badge below -->
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div style="min-width: 0; flex: 1;">
                      <h5 class="assignment-title m-0" style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ event.name }}</h5>
                      <span class="status-pill-purple mt-1 d-inline-block">General Event</span>
                    </div>

                    <div class="dropdown ms-2 flex-shrink-0">
                      <button class="btn btn-sm btn-icon-ghost text-muted p-1 rounded-circle" type="button" data-bs-toggle="dropdown" aria-expanded="false" title="More options">
                        <span class="material-symbols-rounded icon-sm">more_vert</span>
                      </button>
                      <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 text-xs">
                        <li>
                          <a class="dropdown-item d-flex align-items-center gap-2 py-1.5" href="#" @click.prevent="navigateToEventDetails(event.id)">
                            <span class="material-symbols-rounded icon-xs text-primary">visibility</span>
                            View Event Details
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <!-- Simplified Info Rows -->
                  <div class="simplified-info-stack my-2">
                    <div class="info-line-clean">
                      <span class="material-symbols-rounded icon-xs text-secondary">groups</span>
                      <span>Capacity: {{ event.capacity || 'Unlimited' }}</span>
                    </div>
                    <div class="info-line-clean">
                      <span class="material-symbols-rounded icon-xs text-secondary">calendar_today</span>
                      <span class="text-truncate">{{ event.startDate }}</span>
                    </div>
                    <div class="info-line-clean">
                      <span class="material-symbols-rounded icon-xs text-secondary">location_on</span>
                      <span class="text-truncate">{{ event.venueName || 'Campus Venue' }}</span>
                    </div>
                  </div>

                  <!-- Primary Action -->
                  <div class="card-footer-clean pt-2 mt-auto">
                    <button class="btn-manage-club-compact w-100 justify-content-center" @click="navigateToEventDetails(event.id)">
                      Manage Event
                      <span class="material-symbols-rounded icon-sm">arrow_forward</span>
                    </button>
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
                  <span class="badge" :class="ev.reservationStatus === 'RELEASED' ? 'bg-secondary' : 'bg-success'">
                    {{ ev.reservationStatus || 'RESERVED' }}
                  </span>
                </div>
                <div class="small text-muted mb-2">
                  <span>🏛️ {{ ev.venueName || 'Unassigned Venue' }}</span>
                </div>
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

      <!-- Leave Club Role Confirmation Modal (Requirement 7) -->
      <div v-if="showLeaveRoleModal && selectedRoleForLeave" class="modal-backdrop" @click.self="showLeaveRoleModal = false">
        <div class="modal-dialog-custom">
          <div class="d-flex align-items-center gap-2 text-danger mb-2">
            <span class="material-symbols-rounded">no_accounts</span>
            <h4 class="fw-bold m-0 text-dark">Leave Club Role</h4>
          </div>
          <p class="text-secondary text-sm mb-3">
            You are about to leave your Faculty Coordinator role for <strong>{{ selectedRoleForLeave.clubName }}</strong>.
          </p>
          <div class="p-3 bg-light rounded-3 border text-xs text-muted mb-4">
            ⚠️ This action removes your management access.
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button class="btn btn-light rounded-pill px-4" @click="showLeaveRoleModal = false">Cancel</button>
            <button class="btn btn-danger rounded-pill px-4" @click="confirmLeaveRole">Leave Role</button>
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
  overflow: hidden;
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

.icon-md {
  font-size: 24px;
}

/* Statistics Mini Cards (STEP 6) */
.stat-mini-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-num {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.stat-lbl {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  margin-top: 3px;
}

/* Filter Toolbar Card (STEP 2) */
.filter-toolbar-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 14px 18px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
}

/* Compact Assignment Cards (Reduced Height & Improved Spacing) */
.compact-assignment-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
  transition: all 0.2s ease;
  height: 100%;
  min-width: 0;
  overflow: hidden;
}

.status-pill-subtle {
  display: inline-flex;
  align-items: center;
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.status-pill-purple {
  display: inline-flex;
  align-items: center;
  background: #f3e8ff;
  color: #7e22ce;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.simplified-info-stack {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-line-clean {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.84rem;
  color: #475569;
  font-weight: 500;
}

.pending-warning-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fef3c7;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 0.78rem;
  font-weight: 700;
}

.btn-icon-ghost:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.compact-assignment-card:hover {
  transform: translateY(-3px);
  border-color: #3b82f6;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.08);
}

.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.brand-avatar.general-avatar {
  background: #f0fdf4;
  color: #16a34a;
}

.assignment-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
  line-height: 1.2;
}

.badges-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.compact-role-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f1f5f9;
  color: #334155;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.74rem;
  font-weight: 700;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
}

.status-pill.active, .status-pill.live {
  background: #dcfce7;
  color: #15803d;
}

.status-pill.scheduled {
  background: #eff6ff;
  color: #2563eb;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #edf2f7;
  border-radius: 10px;
  padding: 10px;
}

.metric-box {
  text-align: center;
}

.metric-box.has-pending .metric-val {
  color: #d97706;
}

.metric-val {
  display: block;
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.metric-lbl {
  display: block;
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 600;
  margin-top: 2px;
}

.compact-meta-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #f8fafc;
  padding: 10px;
  border-radius: 10px;
}

.meta-line {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: #475569;
  font-weight: 600;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.btn-manage-club-compact {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 6px 14px;
  font-weight: 700;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-manage-club-compact:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
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
