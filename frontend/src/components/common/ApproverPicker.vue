<script setup>
import { ref, computed, onMounted } from 'vue'
import { getUsers } from '@/api/users'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import UserProfileModal from '@/components/common/UserProfileModal.vue'

const showProfileModal = ref(false)
const selectedProfileUserId = ref(null)

function openProfile(item) {
  const targetId = item.id || item.approverId || item.userId
  if (targetId) {
    selectedProfileUserId.value = targetId
    showProfileModal.value = true
  }
}

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [] // Array of { approverId: number, role: string, name?: string, email?: string, designation?: string }
  }
})

const emit = defineEmits(['update:modelValue'])

const allUsers = ref([])
const search = ref('')
const roleFilter = ref('ALL') // 'ALL' | 'FACULTY' | 'ADMIN' | 'STUDENT'
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const users = await getUsers()
    allUsers.value = users || []
  } catch (err) {
    console.error('Failed to load users for approver picker', err)
  } finally {
    loading.value = false
  }
})

// Map of currently selected user IDs
const selectedUserIds = computed(() => props.modelValue.map(item => item.approverId || item.id))

// Available users filtering
const availableUsers = computed(() => {
  return allUsers.value.filter(u => {
    const isSelected = selectedUserIds.value.includes(u.id)
    if (isSelected) return false

    const query = search.value.trim().toLowerCase()
    const nameStr = (u.fullName || u.name || '').toLowerCase()
    const emailStr = (u.email || '').toLowerCase()
    const desigStr = (u.designation || u.role || '').toLowerCase()

    const matchesSearch = !query || nameStr.includes(query) || emailStr.includes(query) || desigStr.includes(query)

    let matchesRole = true
    if (roleFilter.value === 'FACULTY') {
      matchesRole = u.role === 'FACULTY'
    } else if (roleFilter.value === 'ADMIN') {
      matchesRole = u.role === 'ADMIN'
    } else if (roleFilter.value === 'STUDENT') {
      matchesRole = u.role === 'STUDENT'
    }

    return matchesSearch && matchesRole
  })
})

function userRoleBadge(user) {
  if (user.designation === 'PRINCIPAL') return 'role-badge-principal'
  if (user.role === 'ADMIN') return 'role-badge-admin'
  if (user.role === 'FACULTY') return 'role-badge-faculty'
  return 'role-badge-student'
}

function userRoleLabel(user) {
  if (user.designation === 'PRINCIPAL') return 'PRINCIPAL'
  if (user.role === 'ADMIN') return 'ADMIN'
  if (user.role === 'FACULTY') return 'CLUB_FACULTY'
  return 'STUDENT_ORGANIZER'
}

function addApprover(user) {
  const roleTag = userRoleLabel(user)
  const newItem = {
    approverId: user.id,
    role: roleTag,
    name: user.fullName || user.name,
    email: user.email,
    designation: user.designation || user.role
  }
  emit('update:modelValue', [...props.modelValue, newItem])
}

function removeApprover(index) {
  const updated = [...props.modelValue]
  updated.splice(index, 1)
  emit('update:modelValue', updated)
}

function moveUp(index) {
  if (index <= 0) return
  const updated = [...props.modelValue]
  const temp = updated[index]
  updated[index] = updated[index - 1]
  updated[index - 1] = temp
  emit('update:modelValue', updated)
}

function moveDown(index) {
  if (index >= props.modelValue.length - 1) return
  const updated = [...props.modelValue]
  const temp = updated[index]
  updated[index] = updated[index + 1]
  updated[index + 1] = temp
  emit('update:modelValue', updated)
}
</script>

<template>
  <div class="approver-picker-card">
    <div class="picker-header mb-3 d-flex justify-content-between align-items-center flex-wrap gap-2">
      <div>
        <label class="form-label font-bold text-slate-800 mb-0">
          <i class="bi bi-person-check-fill me-1 text-primary"></i>
          Interactive Tagged Approvers Chain
        </label>
        <small class="text-muted d-block">Add and order people who must approve this ticket (Step 1 → Step 2...)</small>
      </div>

      <span class="badge bg-primary rounded-pill px-3">
        {{ modelValue.length }} Approver(s) Tagged
      </span>
    </div>

    <!-- Selected Tagged Chain List -->
    <div class="selected-chain-box mb-3">
      <h6 class="text-xs font-bold uppercase text-slate-600 mb-2">Ordered Approval Sequence</h6>
      
      <div v-if="modelValue.length === 0" class="empty-chain-hint text-center py-3">
        <i class="bi bi-info-circle text-primary me-1"></i>
        No approvers tagged yet. Search and click <strong>"+ Add to Chain"</strong> below to select approvers.
      </div>

      <div v-else class="chain-items-list d-flex flex-column gap-2">
        <div 
          v-for="(item, index) in modelValue" 
          :key="item.approverId || index"
          class="chain-item-row shadow-sm"
        >
          <div class="d-flex align-items-center gap-2" @click="openProfile(item)" style="cursor: pointer;">
            <span class="step-num">Step {{ index + 1 }}</span>
            <UserAvatar size="list" :user="item" />
            <div>
              <strong class="user-name-text text-primary-hover">{{ item.name || 'User #' + item.approverId }}</strong>
              <span class="badge ms-2" :class="item.role === 'PRINCIPAL' ? 'role-badge-principal' : 'role-badge-default'">
                {{ item.role }}
              </span>
              <small class="text-muted d-block text-xs" v-if="item.email">{{ item.email }}</small>
            </div>
          </div>

          <div class="action-buttons d-flex align-items-center gap-1">
            <button 
              type="button" 
              class="btn-icon" 
              :disabled="index === 0" 
              title="Move Up" 
              @click="moveUp(index)"
            >
              <i class="bi bi-arrow-up"></i>
            </button>
            <button 
              type="button" 
              class="btn-icon" 
              :disabled="index === modelValue.length - 1" 
              title="Move Down" 
              @click="moveDown(index)"
            >
              <i class="bi bi-arrow-down"></i>
            </button>
            <button 
              type="button" 
              class="btn-icon-danger ms-1" 
              title="Remove Tag" 
              @click="removeApprover(index)"
            >
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Available Users Selector -->
    <div class="available-users-box p-3 bg-light rounded-3">
      <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
        <h6 class="text-xs font-bold uppercase text-slate-700 mb-0">Search & Tag System Users</h6>
        <div class="btn-group btn-group-sm">
          <button class="btn btn-outline-secondary btn-xs" :class="{ active: roleFilter === 'ALL' }" @click="roleFilter = 'ALL'">All</button>
          <button class="btn btn-outline-secondary btn-xs" :class="{ active: roleFilter === 'FACULTY' }" @click="roleFilter = 'FACULTY'">Faculty</button>
          <button class="btn btn-outline-secondary btn-xs" :class="{ active: roleFilter === 'ADMIN' }" @click="roleFilter = 'ADMIN'">Admin</button>
          <button class="btn btn-outline-secondary btn-xs" :class="{ active: roleFilter === 'STUDENT' }" @click="roleFilter = 'STUDENT'">Students</button>
        </div>
      </div>

      <input 
        v-model="search" 
        type="text" 
        class="form-control form-control-sm mb-2" 
        placeholder="Search by name, email, or designation (e.g. Principal, Meena)..."
      />

      <div v-if="loading" class="text-center py-2">
        <div class="spinner-border spinner-border-sm text-primary"></div>
      </div>

      <div v-else-if="availableUsers.length > 0" class="users-scroll-list">
        <div 
          v-for="u in availableUsers" 
          :key="u.id" 
          class="user-option-card d-flex justify-content-between align-items-center p-2 mb-1 bg-white rounded border"
        >
          <div>
            <strong class="text-sm font-semibold text-slate-800">{{ u.fullName || u.name }}</strong>
            <span class="badge ms-2" :class="userRoleBadge(u)">{{ userRoleLabel(u) }}</span>
            <small class="text-muted d-block text-xs">{{ u.email }} | {{ u.designation || u.department || u.role }}</small>
          </div>
          <button type="button" class="btn btn-sm btn-primary rounded-pill px-3 text-xs" @click="addApprover(u)">
            <i class="bi bi-plus-lg me-1"></i> Add
          </button>
        </div>
      </div>

      <div v-else class="text-center text-muted text-xs py-2">
        No matching users available to tag.
      </div>
    </div>

    <UserProfileModal 
      :show="showProfileModal"
      :userId="selectedProfileUserId"
      @close="showProfileModal = false"
    />
  </div>
</template>

<style scoped>
.approver-picker-card {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  padding: 1rem;
}

.selected-chain-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px;
}

.empty-chain-hint {
  font-size: 0.8rem;
  color: #64748b;
  background: white;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
}

.chain-item-row {
  background: white;
  border: 1px solid #3b82f6;
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-num {
  font-size: 0.7rem;
  font-weight: 800;
  background: #2563eb;
  color: white;
  padding: 2px 8px;
  border-radius: 8px;
}

.user-avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  font-weight: 700;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-name-text {
  font-size: 0.85rem;
  color: #0f172a;
}

.btn-icon {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #334155;
  cursor: pointer;
}

.btn-icon:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-icon-danger {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dc2626;
  cursor: pointer;
}

.users-scroll-list {
  max-height: 180px;
  overflow-y: auto;
}

.role-badge-principal { background: #fef3c7; color: #92400e; }
.role-badge-admin { background: #fce7f3; color: #9d174d; }
.role-badge-faculty { background: #dbeafe; color: #1e40af; }
.role-badge-student { background: #e2e8f0; color: #475569; }
.role-badge-default { background: #e0e7ff; color: #3730a3; }
</style>
