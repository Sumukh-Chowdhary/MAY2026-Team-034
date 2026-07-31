<script setup>
import { ref, computed, onMounted } from 'vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import GlassRequestDetailsModal from '@/components/common/GlassRequestDetailsModal.vue'
import NewTicketModal from '@/components/student/NewTicketModal.vue'
import PermissionTokensCard from '@/components/student/PermissionTokensCard.vue'

import { getStudentRequestsDashboard } from '@/api/requests'
import { useRealtimeTickets } from '@/composables/useRealtimeTickets'

const search = ref('')
const filter = ref('open') // 'open' | 'closed' | 'all'

const myTickets = ref([])
const loading = ref(false)
const isInitialLoad = ref(true)

const selectedTicket = ref(null)
const showTicketModal = ref(false)
const showNewTicketModal = ref(false)
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
  await fetchStudentData(false)
})

async function fetchStudentData(isSilent = false) {
  if (!isSilent && isInitialLoad.value) {
    loading.value = true
  }
  try {
    const res = await getStudentRequestsDashboard()
    if (res.success && res.data) {
      myTickets.value = res.data.myTickets || []
    }
  } catch (err) {
    console.error('Failed to fetch student requests dashboard', err)
  } finally {
    loading.value = false
    isInitialLoad.value = false
  }
}

// Enable silent background polling (every 10s) without jarring UI flicker
useRealtimeTickets(() => fetchStudentData(true), 10000)

function openTicket(ticket) {
  selectedTicket.value = ticket
  showTicketModal.value = true
}

const filteredTickets = computed(() => {
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
  <StudentLayout>
    <section class="requests-page">
      
      <!-- Page Header -->
      <div class="page-header d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
          <h1 class="fw-bold mb-1">Student Requests & Permissions Hub</h1>
          <p class="text-secondary mb-0">Track all submitted requests, action tickets, and live active permission tokens.</p>
        </div>

        <button class="btn btn-warning fw-semibold px-4 rounded-pill shadow-sm" @click="showNewTicketModal = true">
          <i class="bi bi-plus-lg me-1"></i> Raise Request / Ticket
        </button>
      </div>

      <!-- Permission Tokens & Role Assignments Section -->
      <PermissionTokensCard v-if="currentUserId" :userId="currentUserId" />

      <!-- Toolbar -->
      <div class="toolbar d-flex justify-content-between align-items-center gap-3 flex-wrap">
        <div class="search-box">
          <div class="input-group">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
            <input 
              v-model="search" 
              type="text" 
              class="form-control border-start-0 ps-0" 
              placeholder="Search your requests..."
            />
          </div>
        </div>

        <div class="actions d-flex align-items-center gap-2">
          <label class="form-label text-sm fw-medium mb-0 me-1 text-muted">Filter Status:</label>
          <select v-model="filter" class="form-select form-select-sm w-auto">
            <option value="open">Live / Open</option>
            <option value="closed">Closed / Past</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      <!-- Loading State (Initial mount only) -->
      <div v-if="loading && isInitialLoad" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading requests...</p>
      </div>

      <!-- Cards Grid -->
      <div v-else-if="filteredTickets.length > 0" class="cards-grid">
        <div 
          v-for="ticket in filteredTickets" 
          :key="ticket.id" 
          class="card shadow-sm border-0 ticket-card h-100"
        >
          <div class="card-body d-flex flex-column">
            
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="badge bg-light text-dark border">
                {{ ticket.requestType || ticket.ticketType || 'REQUEST' }}
                <span class="ms-1 text-muted">v{{ ticket.version || 1 }}</span>
              </span>
              <span class="badge" :class="badgeClass(ticket.workflowStatus || ticket.approvalStatus || ticket.status)">
                {{ ticket.workflowStatus || ticket.approvalStatus || ticket.status }}
              </span>
            </div>

            <h5 class="fw-bold text-dark mb-2">{{ ticket.title || ticket.subject }}</h5>
            <p class="text-secondary text-sm mb-3" v-if="ticket.description">
              {{ ticket.description.length > 90 ? ticket.description.substring(0, 90) + '...' : ticket.description }}
            </p>

            <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
              <small class="text-muted">
                <i class="bi bi-calendar3 me-1"></i>
                {{ new Date(ticket.createdAt || ticket.date || Date.now()).toLocaleDateString() }}
              </small>

              <button class="btn btn-sm btn-primary rounded-pill px-3" @click="openTicket(ticket)">
                Track Progress
              </button>
            </div>

          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <i class="bi bi-ticket-perforated display-3 text-muted"></i>
        <h4 class="mt-3">No Requests Found</h4>
        <p class="text-secondary">You haven't submitted any requests matching the selected filter.</p>
      </div>

    </section>

    <!-- Glass Request Details Pop-up Modal -->
    <GlassRequestDetailsModal 
      :show="showTicketModal"
      :item="selectedTicket"
      currentUserRole="STUDENT"
      :currentUserId="currentUserId"
      @close="showTicketModal = false"
      @updated="() => fetchStudentData(true)"
    />

    <!-- New Ticket Modal -->
    <NewTicketModal 
      :show="showNewTicketModal"
      @close="showNewTicketModal = false"
      @submit="() => fetchStudentData(true)"
    />

  </StudentLayout>
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

.empty-state {
  padding: 80px 0;
  text-align: center;
  color: #94a3b8;
  background: white;
  border-radius: 20px;
  border: 1px dashed #cbd5e1;
}
</style>
