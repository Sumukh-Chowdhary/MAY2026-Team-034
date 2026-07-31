<script setup>
import { ref, onMounted, computed } from 'vue'
import { getUserAssignments } from '@/api/assignmentTickets'

const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  }
})

const activeAssignments = ref([])
const historyAssignments = ref([])
const loading = ref(false)
const activeTab = ref('active') // 'active' | 'history'

onMounted(async () => {
  if (!props.userId) return
  loading.value = true
  try {
    const res = await getUserAssignments(props.userId)
    if (res.success && res.data) {
      activeAssignments.value = res.data.active || []
      historyAssignments.value = res.data.history || []
    }
  } catch (err) {
    console.error('Failed to load user permission tokens', err)
  } finally {
    loading.value = false
  }
})

function roleLabel(role) {
  if (!role) return 'MEMBER'
  return role.replace('_', ' ')
}

function statusBadgeClass(status) {
  switch (status) {
    case 'ACTIVE': return 'badge-status-active'
    case 'SUSPENDED': return 'badge-status-suspended'
    case 'TERMINATED': return 'badge-status-terminated'
    case 'EXPIRED': return 'badge-status-expired'
    default: return 'bg-secondary'
  }
}
</script>

<template>
  <div class="permission-tokens-wrapper shadow-sm border-0 mb-4">
    <div class="tokens-header d-flex justify-content-between align-items-center flex-wrap gap-2">
      <div>
        <h5 class="fw-bold mb-1 text-slate-800">
          <i class="bi bi-shield-check me-2 text-primary"></i>
          My Permission Tokens & Role Assignments
        </h5>
        <p class="text-secondary text-xs mb-0">Live authorization tokens granted for club activities and events.</p>
      </div>

      <div class="btn-group btn-group-sm">
        <button 
          class="btn btn-outline-primary" 
          :class="{ active: activeTab === 'active' }"
          @click="activeTab = 'active'"
        >
          Active Tokens ({{ activeAssignments.length }})
        </button>
        <button 
          class="btn btn-outline-primary" 
          :class="{ active: activeTab === 'history' }"
          @click="activeTab = 'history'"
        >
          Token History ({{ historyAssignments.length }})
        </button>
      </div>
    </div>

    <div class="tokens-body">
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border spinner-border-sm text-primary"></div>
        <span class="ms-2 text-muted text-xs">Loading permission tokens...</span>
      </div>

      <!-- ACTIVE TOKENS -->
      <div v-else-if="activeTab === 'active'">
        <div class="row g-3" v-if="activeAssignments.length > 0">
          <div 
            v-for="item in activeAssignments" 
            :key="item.id" 
            class="col-md-6 col-lg-4"
          >
            <div class="token-card shadow-sm border h-100">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="token-id-pill">TOKEN-{{ item.id }}-ACTIVE</span>
                <span class="status-badge" :class="statusBadgeClass(item.status)">{{ item.status }}</span>
              </div>

              <h6 class="role-title mb-1">{{ roleLabel(item.assignmentRole) }}</h6>
              <p class="text-xs text-secondary mb-2">
                <i class="bi bi-building me-1"></i>
                {{ item.referenceType || 'CLUB' }}: <strong>{{ item.referenceName || '#' + item.referenceId }}</strong>
              </p>

              <div class="mt-auto pt-2 border-top d-flex justify-content-between text-xs text-muted">
                <span>Duration: <strong>{{ item.durationType }}</strong></span>
                <span v-if="item.endsAt">Ends: {{ new Date(item.endsAt).toLocaleDateString() }}</span>
                <span v-else>Indefinite</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-tokens text-center py-4">
          <i class="bi bi-shield-x text-muted display-6 d-block mb-2"></i>
          <span class="text-muted text-sm">No active permission tokens assigned.</span>
          <p class="text-xs text-secondary mt-1 mb-0">Submit a request to become a Volunteer or Club Organizer.</p>
        </div>
      </div>

      <!-- HISTORY TOKENS -->
      <div v-else-if="activeTab === 'history'">
        <div class="row g-3" v-if="historyAssignments.length > 0">
          <div 
            v-for="item in historyAssignments" 
            :key="item.id" 
            class="col-md-6 col-lg-4"
          >
            <div class="token-card history-token-card shadow-sm border h-100">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="token-id-pill bg-slate">TOKEN-{{ item.id }}-PAST</span>
                <span class="status-badge" :class="statusBadgeClass(item.status)">{{ item.status }}</span>
              </div>

              <h6 class="role-title mb-1">{{ roleLabel(item.assignmentRole) }}</h6>
              <p class="text-xs text-secondary mb-2">
                {{ item.referenceType }}: <strong>{{ item.referenceName || '#' + item.referenceId }}</strong>
              </p>

              <div class="mt-auto pt-2 border-top text-xs text-muted">
                Granted: {{ new Date(item.grantedAt || item.startsAt).toLocaleDateString() }}
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-tokens text-center py-4">
          <i class="bi bi-clock-history text-muted display-6 d-block mb-2"></i>
          <span class="text-muted text-sm">No permission history records found.</span>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.permission-tokens-wrapper {
  background: white;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
}

.tokens-header {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.85rem;
  margin-bottom: 1rem;
}

.token-card {
  background: linear-gradient(135deg, #f8fafc, #ffffff);
  border-radius: 16px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  border-left: 4px solid #10b981 !important;
}

.history-token-card {
  border-left: 4px solid #64748b !important;
  opacity: 0.85;
}

.token-id-pill {
  font-size: 0.65rem;
  font-weight: 700;
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 10px;
  letter-spacing: 0.05em;
}

.bg-slate {
  background: #f1f5f9;
  color: #475569;
}

.role-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}

.status-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
}

.badge-status-active { background: #d1fae5; color: #065f46; }
.badge-status-suspended { background: #fef3c7; color: #92400e; }
.badge-status-terminated { background: #fee2e2; color: #991b1b; }
.badge-status-expired { background: #e2e8f0; color: #475569; }

.empty-tokens {
  background: #f8fafc;
  border-radius: 14px;
}
</style>
