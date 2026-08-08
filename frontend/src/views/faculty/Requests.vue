<script setup>
import { ref, computed, onMounted } from 'vue'
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import GlassRequestDetailsModal from '@/components/common/GlassRequestDetailsModal.vue'
import NewTicketModal from '@/components/faculty/NewTicketModal.vue'

import { getFacultyRequestsDashboard } from '@/api/requests'
import { useRealtimeTickets } from '@/composables/useRealtimeTickets'
import { getRequestPreview, formatRequestPreview } from '@/utils/requestFormatter'

const activeTab = ref('my-tickets') // 'my-tickets' | 'incoming'
const filter = ref('open') // 'open' | 'closed' | 'all'
const search = ref('')

const myTickets = ref([])
const incomingRequests = ref([])
const loading = ref(false)
const isInitialLoad = ref(true)

const selectedTicket = ref(null)
const showTicketModal = ref(false)
const showNewTicketModal = ref(false)
const currentUserId = ref(null)
const userDesignation = ref('')

onMounted(async () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      currentUserId.value = user.id
      userDesignation.value = user.designation || ''
    }
  } catch (e) {
    console.error(e)
  }
  await fetchFacultyData(false)
})

async function fetchFacultyData(isSilent = false) {
  if (!isSilent && isInitialLoad.value) {
    loading.value = true
  }
  try {
    const res = await getFacultyRequestsDashboard()
    if (res.success && res.data) {
      myTickets.value = res.data.myTickets || []
      incomingRequests.value = res.data.incomingRequests || []
    }
  } catch (err) {
    console.error('Failed to fetch faculty requests dashboard', err)
  } finally {
    loading.value = false
    isInitialLoad.value = false
  }
}

// Enable silent background polling simulation (every 10s)
useRealtimeTickets(() => fetchFacultyData(true), 10000)

function openTicket(ticket) {
  selectedTicket.value = ticket
  showTicketModal.value = true
}

// Filtered Lists
const filteredMyTickets = computed(() => {
  return myTickets.value.filter(ticket => {
    const title = (ticket.title || ticket.subject || '').toLowerCase()
    const query = search.value.toLowerCase()
    const matchesSearch = !query || title.includes(query)

    const status = ticket.workflowStatus || ticket.approvalStatus || ticket.status || 'PENDING'
    const isLive = ['PENDING', 'OPEN', 'IN_PROGRESS', 'CHANGES_REQUESTED'].includes(status)

    const matchesFilter = filter.value === 'all' ||
                          (filter.value === 'open' && isLive) ||
                          (filter.value === 'closed' && !isLive)

    return matchesSearch && matchesFilter
  })
})

const filteredIncoming = computed(() => {
  return incomingRequests.value.filter(req => {
    const title = (req.title || req.subject || '').toLowerCase()
    const query = search.value.toLowerCase()
    const matchesSearch = !query || title.includes(query)

    const status = req.workflowStatus || req.approvalStatus || req.status || 'PENDING'
    const isLive = ['PENDING', 'OPEN', 'IN_PROGRESS', 'CHANGES_REQUESTED'].includes(status)

    const matchesFilter = filter.value === 'all' ||
                          (filter.value === 'open' && isLive) ||
                          (filter.value === 'closed' && !isLive)

    return matchesSearch && matchesFilter
  })
})

function badgeClass(status) {
  switch (status) {
    case 'APPROVED': case 'COMPLETED': return 'bg-success'
    case 'REJECTED': return 'bg-danger'
    case 'IN_PROGRESS': case 'CHANGES_REQUESTED': return 'bg-warning text-dark'
    case 'PENDING': case 'OPEN': return 'bg-primary'
    default: return 'bg-secondary'
  }
}
</script>

<template>
  <FacultyLayout>
    <section class="requests-page">
      
      <!-- Page Header -->
      <div class="page-header d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
          <h1 class="fw-bold mb-1">
            Faculty Requests & Tagged Approvals
            <span v-if="userDesignation === 'PRINCIPAL'" class="badge bg-amber text-dark ms-2 font-normal text-xs rounded-pill">
              <i class="bi bi-shield-check me-1"></i> Principal Approvals View
            </span>
          </h1>
          <p class="text-secondary mb-0">Review incoming tagged requests and track your submitted tickets.</p>
        </div>

        <button class="btn btn-warning fw-semibold px-4 rounded-pill shadow-sm" @click="showNewTicketModal = true">
          <i class="bi bi-plus-lg me-1"></i> New Request / Ticket
        </button>
      </div>

      <!-- Main Tabs Toggle -->
      <div class="tab-toggle-bar">
        <button 
          class="toggle-btn" 
          :class="{ active: activeTab === 'my-tickets' }"
          @click="activeTab = 'my-tickets'"
        >
          <i class="bi bi-person-fill me-2"></i> My Raised Tickets
          <span class="count-badge">{{ myTickets.length }}</span>
        </button>

        <button 
          class="toggle-btn" 
          :class="{ active: activeTab === 'incoming' }"
          @click="activeTab = 'incoming'"
        >
          <i class="bi bi-inbox-fill me-2"></i> Tagged Incoming Approvals
          <span class="count-badge highlight-badge">{{ incomingRequests.length }}</span>
        </button>
      </div>

      <!-- Search & Filters Toolbar -->
      <div class="toolbar d-flex justify-content-between align-items-center gap-3 flex-wrap">
        <div class="search-box">
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
            <input 
              v-model="search" 
              type="text" 
              class="form-control border-start-0 ps-0" 
              placeholder="Search by title or subject..."
            />
          </div>
        </div>

        <div class="actions d-flex align-items-center gap-2">
          <label class="form-label text-sm fw-medium mb-0 me-1 text-muted">Status:</label>
          <select v-model="filter" class="form-select form-select-sm w-auto">
            <option value="open">Live / Open</option>
            <option value="closed">Closed</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      <!-- Loading State (Initial mount only) -->
      <div v-if="loading && isInitialLoad" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading requests...</p>
      </div>

      <!-- TAB 1: MY RAISED TICKETS -->
      <div v-else-if="activeTab === 'my-tickets'">
        <div class="cards-grid" v-if="filteredMyTickets.length > 0">
          <div 
            v-for="ticket in filteredMyTickets" 
            :key="ticket.id" 
            class="card shadow-sm border-0 ticket-card h-100"
          >
            <div class="card-body d-flex flex-column gap-2">
              <div class="d-flex justify-content-between align-items-start">
                <span class="badge bg-light text-dark border">
                  {{ ticket.requestType || ticket.ticketType || 'TICKET' }}
                  <span class="ms-1 text-muted">v{{ ticket.version || 1 }}</span>
                </span>
                <span class="badge" :class="badgeClass(ticket.workflowStatus || ticket.approvalStatus || ticket.status)">
                  {{ getRequestPreview(ticket).status }}
                </span>
              </div>

              <div>
                <h5 class="fw-bold text-dark mb-1">{{ getRequestPreview(ticket).title }}</h5>
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
                  {{ getRequestPreview(ticket).rawDescription.length > 90 ? getRequestPreview(ticket).rawDescription.substring(0, 90) + '...' : getRequestPreview(ticket).rawDescription }}
                </p>
              </div>

              <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                <small class="text-muted">
                  <i class="bi bi-clock me-1"></i> {{ getRequestPreview(ticket).date || 'Submitted' }}
                </small>

                <button class="btn btn-sm btn-primary rounded-pill px-3" @click="openTicket(ticket)">
                  View Request
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <i class="bi bi-folder2-open display-3 text-muted"></i>
          <h4 class="mt-3">No Raised Tickets Found</h4>
          <p class="text-secondary">You haven't raised any tickets matching the current filter.</p>
        </div>
      </div>

      <!-- TAB 2: TAGGED INCOMING REQUESTS -->
      <div v-else-if="activeTab === 'incoming'">
        <div class="cards-grid" v-if="filteredIncoming.length > 0">
          <div 
            v-for="req in filteredIncoming" 
            :key="req.id" 
            class="card shadow-sm border-0 ticket-card incoming-card-accent h-100"
          >
            <div class="card-body d-flex flex-column gap-2">
              <div class="d-flex justify-content-between align-items-start">
                <span class="badge bg-amber text-dark">
                  <i class="bi bi-tag-fill me-1"></i> Tagged Approver
                </span>
                <span class="badge" :class="badgeClass(req.workflowStatus || req.approvalStatus || req.status)">
                  {{ getRequestPreview(req).status }}
                </span>
              </div>

              <div>
                <h5 class="fw-bold text-dark mb-1">{{ getRequestPreview(req).title }}</h5>
                <p class="text-sm text-primary font-semibold m-0" v-if="getRequestPreview(req).subtitle">
                  {{ getRequestPreview(req).subtitle }}
                </p>
                <p class="text-xs text-secondary m-0" v-if="getRequestPreview(req).secondaryLine">
                  📍 {{ getRequestPreview(req).secondaryLine }}
                </p>
                <p class="text-xs text-muted m-0" v-if="getRequestPreview(req).date">
                  📅 {{ getRequestPreview(req).date }}
                </p>
                <p class="text-xs text-muted m-0" v-if="getRequestPreview(req).capacity">
                  👥 Expected Capacity: {{ getRequestPreview(req).capacity }}
                </p>
                <p class="text-secondary text-sm mt-1 mb-0" v-if="!getRequestPreview(req).isStructured && getRequestPreview(req).rawDescription">
                  {{ getRequestPreview(req).rawDescription.length > 90 ? getRequestPreview(req).rawDescription.substring(0, 90) + '...' : getRequestPreview(req).rawDescription }}
                </p>
              </div>

              <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                <small class="text-muted">
                  By: <strong>{{ req.requester?.name || req.raisedBy?.name || 'Faculty Coordinator' }}</strong>
                </small>

                <button class="btn btn-sm btn-warning font-semibold rounded-pill px-3" @click="openTicket(req)">
                  Review & Action
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <i class="bi bi-check-all display-3 text-muted"></i>
          <h4 class="mt-3">No Pending Incoming Approvals</h4>
          <p class="text-secondary">You have no tagged incoming requests awaiting your decision.</p>
        </div>
      </div>

    </section>

    <!-- Glass Request Details Pop-up Modal -->
    <GlassRequestDetailsModal 
      :show="showTicketModal"
      :item="selectedTicket"
      currentUserRole="FACULTY"
      :currentUserId="currentUserId"
      @close="showTicketModal = false"
      @updated="() => fetchFacultyData(true)"
    />

    <!-- New Ticket Modal -->
    <NewTicketModal 
      :show="showNewTicketModal"
      @close="showNewTicketModal = false"
      @submit="() => fetchFacultyData(true)"
    />

  </FacultyLayout>
</template>

<style scoped>
.requests-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header h1 {
  font-size: 2rem;
  color: #0f172a;
}

.tab-toggle-bar {
  display: inline-flex;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 6px;
  gap: 6px;
  align-self: flex-start;
}

.toggle-btn {
  border: none;
  background: transparent;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 600;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.25s ease;
  cursor: pointer;
}

.toggle-btn.active {
  background: #f59e0b;
  color: white;
}

.count-badge {
  background: #f1f5f9;
  color: #334155;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}

.toggle-btn.active .count-badge {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.highlight-badge {
  background: #3b82f6;
  color: white;
}

.toolbar {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 12px 16px;
}

.search-box {
  flex: 1;
  max-width: 500px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.ticket-card {
  border-radius: 18px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ticket-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08) !important;
}

.incoming-card-accent {
  border-left: 4px solid #f59e0b !important;
}

.empty-state {
  padding: 80px 0;
  text-align: center;
  color: #94a3b8;
  background: white;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
}

.bg-amber { background: #fef3c7; }
</style>