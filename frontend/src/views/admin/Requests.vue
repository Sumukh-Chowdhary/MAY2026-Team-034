<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import GlassRequestDetailsModal from '@/components/common/GlassRequestDetailsModal.vue'
import AssignmentTicketModal from '@/components/admin/requests/AssignmentTicketModal.vue'

import { getAdminRequestsDashboard } from '@/api/requests'
import { getActionTickets } from '@/api/actionTickets'
import { getAssignmentTickets } from '@/api/assignmentTickets'
import { reseedDatabase } from '@/api/admin'
import { useRealtimeTickets } from '@/composables/useRealtimeTickets'

import { getClubs } from '@/api/clubs'
import { getRequestPreview, formatRequestPreview } from '@/utils/requestFormatter'

// Active Tabs: 'requests' | 'action-tickets' | 'assignments'
const mainTab = ref('requests')
const subTab = ref('all') // 'all' | 'clubs' | 'events' (for requests tab)
const statusFilter = ref('LIVE') // 'LIVE' | 'CLOSED' | 'ALL'
const roleFilter = ref('ALL') // Role filter for assignments
const selectedClubFilter = ref('ALL') // Specific club filter
const search = ref('')

// Data lists
const clubRequests = ref([])
const eventRequests = ref([])
const actionTicketsList = ref([])
const assignmentTicketsList = ref([])
const clubsList = ref([])
const loading = ref(false)
const isInitialLoad = ref(true)
const seedLoading = ref(false)
const seedMessage = ref('')

// Modals
const selectedItem = ref(null)
const showDetailsModal = ref(false)
const selectedAssignment = ref(null)
const showAssignmentModal = ref(false)

const currentUserId = ref(null)

onMounted(async () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      currentUserId.value = user.id
    }
  } catch (e) {
    console.error(e)
  }
  await fetchAllData(false)
})

async function fetchAllData(isSilent = false) {
  if (!isSilent && isInitialLoad.value) {
    loading.value = true
  }
  try {
    const [dashRes, actionRes, assignRes, clubRes] = await Promise.allSettled([
      getAdminRequestsDashboard(),
      getActionTickets(),
      getAssignmentTickets(),
      getClubs()
    ])

    if (dashRes.status === 'fulfilled' && dashRes.value.success) {
      const data = dashRes.value.data
      clubRequests.value = data.clubRequests || []
      eventRequests.value = data.eventRequests || []
    }

    if (actionRes.status === 'fulfilled' && actionRes.value.success) {
      actionTicketsList.value = actionRes.value.data || []
    }

    if (assignRes.status === 'fulfilled' && assignRes.value.success) {
      assignmentTicketsList.value = assignRes.value.data || []
    }

    if (clubRes.status === 'fulfilled') {
      clubsList.value = clubRes.value.clubs || clubRes.value || []
    }
  } catch (err) {
    console.error('Error fetching admin requests board data', err)
  } finally {
    loading.value = false
    isInitialLoad.value = false
  }
}

// Enable silent background polling simulation (every 10s)
useRealtimeTickets(() => fetchAllData(true), 10000)

// Filtered Workflow Requests (Tab 1)
const filteredRequests = computed(() => {
  let combined = []
  if (subTab.value === 'all' || subTab.value === 'clubs') {
    combined.push(...clubRequests.value)
  }
  if (subTab.value === 'all' || subTab.value === 'events') {
    combined.push(...eventRequests.value)
  }

  return combined.filter(req => {
    const title = (req.title || req.subject || '').toLowerCase()
    const requester = (req.requester?.name || req.requestedBy || '').toLowerCase()
    const refName = (req.referenceName || req.club || '').toLowerCase()
    const query = search.value.toLowerCase()

    const matchesSearch = !query || title.includes(query) || requester.includes(query) || refName.includes(query)

    const status = req.workflowStatus || req.approvalStatus || req.status || 'PENDING'
    const isLive = ['PENDING', 'OPEN', 'IN_PROGRESS', 'CHANGES_REQUESTED'].includes(status)
    const matchesStatus = statusFilter.value === 'ALL' || 
                          (statusFilter.value === 'LIVE' && isLive) || 
                          (statusFilter.value === 'CLOSED' && !isLive)

    const matchesClub = selectedClubFilter.value === 'ALL' || 
                        req.referenceId == selectedClubFilter.value ||
                        (req.referenceName && req.referenceName.toLowerCase() === String(selectedClubFilter.value).toLowerCase())

    return matchesSearch && matchesStatus && matchesClub
  })
})

// Filtered Action Tickets (Tab 2)
const filteredActionTickets = computed(() => {
  return actionTicketsList.value.filter(ticket => {
    const title = (ticket.title || '').toLowerCase()
    const refName = (ticket.referenceName || '').toLowerCase()
    const query = search.value.toLowerCase()

    const matchesSearch = !query || title.includes(query) || refName.includes(query)

    const status = ticket.taskStatus || ticket.approvalStatus || 'PENDING'
    const isLive = ['PENDING', 'OPEN', 'IN_PROGRESS', 'CHANGES_REQUESTED'].includes(status)
    const matchesStatus = statusFilter.value === 'ALL' || 
                          (statusFilter.value === 'LIVE' && isLive) || 
                          (statusFilter.value === 'CLOSED' && !isLive)

    const matchesClub = selectedClubFilter.value === 'ALL' || 
                        ticket.referenceId == selectedClubFilter.value ||
                        (ticket.referenceName && ticket.referenceName.toLowerCase() === String(selectedClubFilter.value).toLowerCase())

    return matchesSearch && matchesStatus && matchesClub
  })
})

// Filtered Assignment Tickets (Tab 3)
const filteredAssignments = computed(() => {
  return assignmentTicketsList.value.filter(assign => {
    const holder = (assign.holder?.name || '').toLowerCase()
    const role = (assign.assignmentRole || '').toLowerCase()
    const refName = (assign.referenceName || '').toLowerCase()
    const query = search.value.toLowerCase()

    const matchesSearch = !query || holder.includes(query) || role.includes(query) || refName.includes(query)

    const matchesRole = roleFilter.value === 'ALL' || assign.assignmentRole === roleFilter.value

    const isLive = assign.status === 'ACTIVE'
    const matchesStatus = statusFilter.value === 'ALL' || 
                          (statusFilter.value === 'LIVE' && isLive) || 
                          (statusFilter.value === 'CLOSED' && !isLive)

    const matchesClub = selectedClubFilter.value === 'ALL' || 
                        assign.referenceId == selectedClubFilter.value ||
                        (assign.referenceName && assign.referenceName.toLowerCase() === String(selectedClubFilter.value).toLowerCase())

    return matchesSearch && matchesRole && matchesStatus && matchesClub
  })
})

// Stats for Live Assignments
const activeCount = computed(() => assignmentTicketsList.value.filter(a => a.status === 'ACTIVE').length)
const suspendedCount = computed(() => assignmentTicketsList.value.filter(a => a.status === 'SUSPENDED').length)
const terminatedCount = computed(() => assignmentTicketsList.value.filter(a => a.status === 'TERMINATED').length)
const expiredCount = computed(() => assignmentTicketsList.value.filter(a => a.status === 'EXPIRED').length)

// Modal Openers
function openDetails(item) {
  selectedItem.value = item
  showDetailsModal.value = true
}

function openAssignmentManage(assign) {
  selectedAssignment.value = assign
  showAssignmentModal.value = true
}

function badgeClass(status) {
  switch (status) {
    case 'APPROVED': case 'COMPLETED': case 'ACTIVE': return 'bg-success'
    case 'REJECTED': case 'TERMINATED': return 'bg-danger'
    case 'SUSPENDED': case 'IN_PROGRESS': case 'CHANGES_REQUESTED': return 'bg-warning text-dark'
    case 'PENDING': case 'OPEN': case 'EXPIRED': return 'bg-primary'
    default: return 'bg-secondary'
  }
}
</script>

<template>
  <AdminLayout>
    <section class="requests-board-page">
      
      <!-- Top Title Header -->
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4">
        <div>
          <h2 class="fw-bold mb-1 title-heading">Requests & Tickets Management</h2>
          <p class="text-secondary mb-0">Oversee workflow requests, administrative action tickets, and live role assignments across all clubs.</p>
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-outline-primary rounded-pill px-3" @click="() => fetchAllData(false)">
            <i class="bi bi-arrow-clockwise me-1"></i> Refresh Board
          </button>
        </div>
      </div>

      <!-- Main Navigation Tabs -->
      <div class="board-main-tabs mb-4">
        <button 
          class="tab-btn" 
          :class="{ active: mainTab === 'requests' }"
          @click="mainTab = 'requests'"
        >
          <i class="bi bi-file-earmark-text-fill me-2"></i> Approval Requests
          <span class="count-pill">{{ clubRequests.length + eventRequests.length }}</span>
        </button>

        <button 
          class="tab-btn" 
          :class="{ active: mainTab === 'action-tickets' }"
          @click="mainTab = 'action-tickets'"
        >
          <i class="bi bi-kanban-fill me-2"></i> Action Tickets
          <span class="count-pill">{{ actionTicketsList.length }}</span>
        </button>

        <button 
          class="tab-btn" 
          :class="{ active: mainTab === 'assignments' }"
          @click="mainTab = 'assignments'"
        >
          <i class="bi bi-person-workspace me-2"></i> Live Assignments
          <span class="count-pill highlight-pill">{{ activeCount }}</span>
        </button>
      </div>

      <!-- Toolbar: Filters & Search -->
      <div class="toolbar-card mb-4 shadow-sm">
        <div class="row g-3 align-items-center">
          
          <!-- Search input -->
          <div class="col-md-4 col-lg-3">
            <div class="input-group input-group-sm">
              <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
              <input 
                v-model="search" 
                type="text" 
                class="form-control border-start-0 ps-0" 
                placeholder="Search requests & tickets..."
              />
            </div>
          </div>

          <!-- Specific Club Filter Dropdown -->
          <div class="col-md-4 col-lg-3">
            <select v-model="selectedClubFilter" class="form-select form-select-sm border-slate-300 rounded-pill">
              <option value="ALL">🏛️ All Clubs & References</option>
              <option v-for="c in clubsList" :key="c.id" :value="c.id">
                {{ c.clubName }}
              </option>
            </select>
          </div>

          <!-- Status Live / Closed Filter Pills -->
          <div class="col-md-4 col-lg-3">
            <div class="status-pills-bar">
              <button 
                class="pill-btn" 
                :class="{ active: statusFilter === 'LIVE' }"
                @click="statusFilter = 'LIVE'"
              >
                <i class="bi bi-broadcast me-1 text-emerald-500"></i> Live
              </button>

              <button 
                class="pill-btn" 
                :class="{ active: statusFilter === 'CLOSED' }"
                @click="statusFilter = 'CLOSED'"
              >
                <i class="bi bi-archive-fill me-1"></i> Closed
              </button>

              <button 
                class="pill-btn" 
                :class="{ active: statusFilter === 'ALL' }"
                @click="statusFilter = 'ALL'"
              >
                All
              </button>
            </div>
          </div>

          <!-- Sub-filters: Clubs/Events for Requests, Role for Assignments -->
          <div class="col-md-12 col-lg-3 text-end" v-if="mainTab === 'requests'">
            <div class="btn-group btn-group-sm w-100">
              <button class="btn btn-outline-primary" :class="{ active: subTab === 'all' }" @click="subTab = 'all'">All Types</button>
              <button class="btn btn-outline-primary" :class="{ active: subTab === 'clubs' }" @click="subTab = 'clubs'">Clubs</button>
              <button class="btn btn-outline-primary" :class="{ active: subTab === 'events' }" @click="subTab = 'events'">Events</button>
            </div>
          </div>

          <div class="col-md-12 col-lg-3" v-else-if="mainTab === 'assignments'">
            <select v-model="roleFilter" class="form-select form-select-sm rounded-pill">
              <option value="ALL">All Roles</option>
              <option value="ORGANIZER">Organizer</option>
              <option value="VOLUNTEER">Volunteer</option>
              <option value="FACULTY_COORDINATOR">Faculty Coordinator</option>
              <option value="EVENT_ORGANIZER">Event Organizer</option>
            </select>
          </div>

        </div>
      </div>

      <!-- Loading State (Initial mount only) -->
      <div v-if="loading && isInitialLoad" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading board...</p>
      </div>

      <!-- TAB 1: APPROVAL REQUESTS -->
      <div v-else-if="mainTab === 'requests'">
        <div class="row g-4" v-if="filteredRequests.length > 0">
          <div 
            v-for="req in filteredRequests" 
            :key="req.id" 
            class="col-xl-4 col-md-6"
          >
            <div class="card h-100 shadow-sm border-0 request-item-card">
              <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <span class="badge bg-light text-dark border">
                    {{ req.requestType }}
                    <span class="ms-1 text-muted">v{{ req.version || 1 }}</span>
                  </span>
                  <span class="badge" :class="badgeClass(req.workflowStatus || req.status)">
                    {{ formatRequestPreview(req).status }}
                  </span>
                </div>

                <h5 class="card-title fw-bold text-dark mb-1">{{ formatRequestPreview(req).title }}</h5>
                <p class="text-sm text-primary font-semibold m-0 mb-1" v-if="formatRequestPreview(req).club">
                  {{ formatRequestPreview(req).club }}
                </p>
                <p class="text-xs text-secondary m-0 mb-1" v-if="formatRequestPreview(req).venue">
                  📍 {{ formatRequestPreview(req).venue }}
                </p>
                <p class="text-xs text-muted m-0 mb-1" v-if="formatRequestPreview(req).date">
                  📅 {{ formatRequestPreview(req).date }}
                </p>
                <p class="text-xs text-muted m-0 mb-2" v-if="formatRequestPreview(req).capacity">
                  👥 Expected Capacity: {{ formatRequestPreview(req).capacity }}
                </p>

                <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    <i class="bi bi-person me-1"></i> {{ req.requester?.name || req.requestedBy || 'Requester' }}
                  </small>

                  <button class="btn btn-sm btn-primary rounded-pill px-3" @click="openDetails(req)">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state-box">
          <i class="bi bi-inbox display-4 text-muted mb-3"></i>
          <h4>No Requests Found</h4>
          <p class="text-secondary">No approval requests matching your search/filters.</p>
        </div>
      </div>

      <!-- TAB 2: ACTION TICKETS -->
      <div v-else-if="mainTab === 'action-tickets'">
        <div class="row g-4" v-if="filteredActionTickets.length > 0">
          <div 
            v-for="ticket in filteredActionTickets" 
            :key="ticket.id" 
            class="col-xl-4 col-md-6"
          >
            <div class="card h-100 shadow-sm border-0 request-item-card action-ticket-accent">
              <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <span class="badge bg-indigo text-white">
                    {{ ticket.ticketType }}
                    <span class="ms-1 text-light">v{{ ticket.version || 1 }}</span>
                  </span>
                  <span class="badge" :class="badgeClass(ticket.taskStatus || ticket.approvalStatus)">
                    {{ ticket.taskStatus || ticket.approvalStatus }}
                  </span>
                </div>

                <div>
                  <h5 class="card-title fw-bold text-dark mb-1">{{ getRequestPreview(ticket).title }}</h5>
                  <p class="text-sm text-primary font-semibold m-0" v-if="getRequestPreview(ticket).subtitle">
                    {{ getRequestPreview(ticket).subtitle }}
                  </p>
                  <p class="text-xs text-secondary m-0" v-if="getRequestPreview(ticket).secondaryLine">
                    📍 {{ getRequestPreview(ticket).secondaryLine }}
                  </p>
                  <p class="text-xs text-muted m-0" v-if="getRequestPreview(ticket).date">
                    📅 {{ getRequestPreview(ticket).date }}
                  </p>
                  <p class="text-xs text-muted m-0" v-if="getRequestPreview(ticket).capacity">
                    👥 Expected Capacity: {{ getRequestPreview(ticket).capacity }}
                  </p>
                  <p class="text-secondary text-sm mt-1 mb-0" v-if="!getRequestPreview(ticket).isStructured && getRequestPreview(ticket).rawDescription">
                    {{ getRequestPreview(ticket).rawDescription.length > 80 ? getRequestPreview(ticket).rawDescription.substring(0, 80) + '...' : getRequestPreview(ticket).rawDescription }}
                  </p>
                </div>

                <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                  <div>
                    <span class="badge bg-outline-secondary me-1">{{ ticket.priority }}</span>
                    <small class="text-muted">#{{ ticket.id }}</small>
                  </div>

                  <button class="btn btn-sm btn-primary rounded-pill px-3" @click="openDetails(ticket)">
                    View / Execute
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state-box">
          <i class="bi bi-kanban display-4 text-muted mb-3"></i>
          <h4>No Action Tickets Found</h4>
          <p class="text-secondary">No administrative action tickets matching current criteria.</p>
        </div>
      </div>

      <!-- TAB 3: LIVE ASSIGNMENTS BOARD -->
      <div v-else-if="mainTab === 'assignments'">
        
        <!-- Stats Summary Bar -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3">
            <div class="stat-card active-card">
              <div class="stat-icon"><i class="bi bi-check-circle-fill text-success"></i></div>
              <div>
                <h4 class="mb-0 font-bold">{{ activeCount }}</h4>
                <small class="text-muted">Active Assignments</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-card suspended-card">
              <div class="stat-icon"><i class="bi bi-pause-circle-fill text-warning"></i></div>
              <div>
                <h4 class="mb-0 font-bold">{{ suspendedCount }}</h4>
                <small class="text-muted">Suspended</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-card terminated-card">
              <div class="stat-icon"><i class="bi bi-x-circle-fill text-danger"></i></div>
              <div>
                <h4 class="mb-0 font-bold">{{ terminatedCount }}</h4>
                <small class="text-muted">Terminated</small>
              </div>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-card expired-card">
              <div class="stat-icon"><i class="bi bi-clock-history text-secondary"></i></div>
              <div>
                <h4 class="mb-0 font-bold">{{ expiredCount }}</h4>
                <small class="text-muted">Expired</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Assignments Grid -->
        <div class="row g-4" v-if="filteredAssignments.length > 0">
          <div 
            v-for="assign in filteredAssignments" 
            :key="assign.id" 
            class="col-xl-4 col-md-6"
          >
            <div class="card h-100 shadow-sm border-0 assignment-card">
              <div class="card-body d-flex flex-column">
                
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <span class="badge role-pill">{{ assign.assignmentRole.replace('_', ' ') }}</span>
                  <span class="badge" :class="badgeClass(assign.status)">{{ assign.status }}</span>
                </div>

                <div class="holder-info mb-3">
                  <h6 class="holder-name mb-0">
                    <i class="bi bi-person-circle text-primary me-2"></i>
                    {{ assign.holder?.name || 'Holder #' + assign.holderId }}
                  </h6>
                  <small class="text-muted ps-4" v-if="assign.holder?.email">{{ assign.holder.email }}</small>
                </div>

                <div class="assignment-details-box mb-3">
                  <div class="d-flex justify-content-between text-xs mb-1">
                    <span class="text-muted">Reference:</span>
                    <strong>{{ assign.referenceType || 'CLUB' }}: {{ assign.referenceName || '#' + assign.referenceId }}</strong>
                  </div>
                  <div class="d-flex justify-content-between text-xs">
                    <span class="text-muted">Duration:</span>
                    <span class="badge bg-light text-dark">{{ assign.durationType }}</span>
                  </div>
                </div>

                <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                  <small class="text-muted text-xs">
                    Starts: {{ new Date(assign.startsAt).toLocaleDateString() }}
                  </small>

                  <button class="btn btn-sm btn-outline-primary rounded-pill px-3" @click="openAssignmentManage(assign)">
                    <i class="bi bi-gear-fill me-1"></i> Manage
                  </button>
                </div>

              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state-box">
          <i class="bi bi-person-workspace display-4 text-muted mb-3"></i>
          <h4>No Assignments Found</h4>
          <p class="text-secondary">No role assignments matching your query.</p>
        </div>

      </div>

    </section>

    <!-- Glass Request Details Modal -->
    <GlassRequestDetailsModal 
      :show="showDetailsModal"
      :item="selectedItem"
      currentUserRole="ADMIN"
      :currentUserId="currentUserId"
      @close="showDetailsModal = false"
      @updated="() => fetchAllData(true)"
    />

    <!-- Admin Assignment Ticket Management Modal -->
    <AssignmentTicketModal 
      :show="showAssignmentModal"
      :ticket="selectedAssignment"
      @close="showAssignmentModal = false"
      @updated="() => fetchAllData(true)"
    />

  </AdminLayout>
</template>

<style scoped>
.requests-board-page {
  width: 100%;
}

.title-heading {
  color: #0f172a;
}

.board-main-tabs {
  display: flex;
  gap: 10px;
  background: white;
  padding: 6px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.tab-btn {
  border: none;
  background: transparent;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.25s ease;
  cursor: pointer;
}

.tab-btn.active {
  background: #2563eb;
  color: white;
}

.count-pill {
  background: rgba(241, 245, 249, 0.9);
  color: #334155;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}

.tab-btn.active .count-pill {
  background: rgba(255, 255, 255, 0.25);
  color: white;
}

.highlight-pill {
  background: #10b981;
  color: white;
}

.toolbar-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1rem 1.25rem;
}

.status-pills-bar {
  display: inline-flex;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
  width: 100%;
}

.pill-btn {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.825rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn.active {
  background: white;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.request-item-card {
  border-radius: 18px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.request-item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08) !important;
}

.action-ticket-accent {
  border-left: 4px solid #6366f1 !important;
}

.assignment-card {
  border-radius: 18px;
  border-left: 4px solid #10b981 !important;
}

.role-pill {
  background: #e0e7ff;
  color: #3730a3;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 12px;
}

.assignment-details-box {
  background: #f8fafc;
  border-radius: 12px;
  padding: 10px;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  font-size: 1.75rem;
}

.empty-state-box {
  text-align: center;
  padding: 4rem 1rem;
  background: white;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
}

.bg-indigo { background: #6366f1; }
</style>