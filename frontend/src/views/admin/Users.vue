<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { getUsers, updateUserStatus } from '@/api/users'
import { getCurrentUser } from '@/services/authService'
import UserAvatar from '@/components/profile/UserAvatar.vue'
import '@/assets/css/Users.css'

const router = useRouter()
const currentAdminId = computed(() => getCurrentUser()?.id)

// ── State ──────────────────────────────────────────
const search     = ref('')
const activeTab  = ref('ALL')   // 'ALL' | 'STUDENT' | 'FACULTY'
const userList   = ref([])
const loading    = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const users = await getUsers()
    userList.value = users
  } catch (error) {
    console.error('Failed to load users', error)
  } finally {
    loading.value = false
  }
})

const userToBlock  = ref(null)
const showBlockModal = ref(false)

// ── Helpers ────────────────────────────────────────
function roleBadge(role) {
  const map = { ADMIN: 'role-admin', FACULTY: 'role-faculty', STUDENT: 'role-student' }
  return map[role] || 'role-student'
}

function roleLabel(role) {
  return role ? (role.charAt(0) + role.slice(1).toLowerCase()) : 'User'
}

function getAvatarUrl(user) {
  const style = user.avatarStyle || 'adventurer'
  const seed = user.avatarSeed || user.name || user.email || 'User'
  return `https://api.dicebear.com/7.x/${style}/svg?seed=${encodeURIComponent(seed)}`
}

// ── Other Users (Logged-in admin completely excluded) ────
const otherUsers = computed(() => {
  const myId = String(currentAdminId.value || '')
  return userList.value.filter(u => String(u.id) !== myId)
})

// ── Stats ──────────────────────────────────────────
const totalUsers    = computed(() => otherUsers.value.length)
const totalStudents = computed(() => otherUsers.value.filter(u => u.role === 'STUDENT').length)
const totalFaculty  = computed(() => otherUsers.value.filter(u => u.role === 'FACULTY').length)
const activeUsers   = computed(() => otherUsers.value.filter(u => u.status === 'ACTIVE').length)

// ── Filtered List ──────────────────────────────────
const filteredUsers = computed(() => {
  const q = search.value.trim().toLowerCase()

  return otherUsers.value.filter(u => {
    const matchTab =
      activeTab.value === 'ALL' ||
      u.role === activeTab.value

    const matchSearch =
      !q ||
      (u.name && u.name.toLowerCase().includes(q)) ||
      (u.email && u.email.toLowerCase().includes(q)) ||
      (u.registerNumber && u.registerNumber.toLowerCase().includes(q)) ||
      (u.department && u.department.toLowerCase().includes(q))

    return matchTab && matchSearch
  })
})

// ── Navigation ─────────────────────────────────────
function viewUser(user) {
  router.push({ name: 'AdminUserDetails', params: { id: user.id } })
}

// ── Block / Unblock ────────────────────────────────
function openBlockModal(event, user) {
  event.stopPropagation()
  userToBlock.value = user
  showBlockModal.value = true
}

function closeBlockModal() {
  showBlockModal.value = false
  userToBlock.value = null
}

function confirmBlock() {
  if (!userToBlock.value) return
  const target = userList.value.find(u => u.id === userToBlock.value.id)
  if (!target) return

  const newStatus = target.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  updateUserStatus(target.id, newStatus)
    .then(() => {
      target.status = newStatus
      closeBlockModal()
    })
    .catch(() => {
      alert('Failed to update user status. Please try again.')
    })
}

const blockModalTitle = computed(() =>
  userToBlock.value?.status === 'ACTIVE' ? 'Block User?' : 'Unblock User?'
)

const blockModalMsg = computed(() =>
  userToBlock.value?.status === 'ACTIVE'
    ? 'will be blocked and cannot access the platform.'
    : 'will be unblocked and regain access to the platform.'
)

const blockBtnLabel = computed(() =>
  userToBlock.value?.status === 'ACTIVE' ? 'Yes, Block' : 'Yes, Unblock'
)
</script>

<template>
  <AdminLayout>
    <section class="admin-users-page">

      <!-- ── Page Header ── -->
      <div class="page-top">
        <div>
          <p class="eyebrow">Admin Dashboard</p>
          <h2 class="fw-bold mb-2">Users Management</h2>
          <p class="subtitle">
            View and manage all registered students, faculty and administrators on the platform.
          </p>
        </div>
      </div>

      <!-- ── Stats Row ── -->
      <div class="stats-row">
        <div class="stat-chip">
          <i class="bi bi-people-fill" style="color:#2563eb;"></i>
          <span class="chip-count">{{ totalUsers }}</span>
          <span>Total Users</span>
        </div>
        <div class="stat-chip">
          <i class="bi bi-mortarboard-fill" style="color:#16a34a;"></i>
          <span class="chip-count">{{ totalStudents }}</span>
          <span>Students</span>
        </div>
        <div class="stat-chip">
          <i class="bi bi-person-badge-fill" style="color:#7c3aed;"></i>
          <span class="chip-count">{{ totalFaculty }}</span>
          <span>Faculty</span>
        </div>
        <div class="stat-chip">
          <i class="bi bi-check-circle-fill" style="color:#0891b2;"></i>
          <span class="chip-count">{{ activeUsers }}</span>
          <span>Active</span>
        </div>
      </div>

      <!-- ── Toolbar: Search + Tabs ── -->
      <div class="toolbar">
        <div class="search-box">
          <i class="bi bi-search"></i>
          <input
            v-model="search"
            type="text"
            placeholder="Search by name, email, register no, department…"
          />
        </div>
        <!-- Role Tab Toggles (as per wireframe) -->
        <div class="tab-group">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'ALL' }"
            @click="activeTab = 'ALL'"
          >All</button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'STUDENT' }"
            @click="activeTab = 'STUDENT'"
          >Students</button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'FACULTY' }"
            @click="activeTab = 'FACULTY'"
          >Faculty</button>
        </div>
      </div>

      <!-- ── Table ── -->
      <div class="table-panel">
        <table class="users-table" v-if="filteredUsers.length > 0">
          <thead>
            <tr>
              <th>User</th>
              <th>Role</th>
              <th>Department</th>
              <th>Clubs</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              :class="{ 'bg-light border-start border-primary border-4': user.id === currentAdminId }"
              @click="viewUser(user)"
            >
              <!-- Avatar + Name + Reg -->
              <td>
                <div class="user-cell align-items-center gap-2">
                  <UserAvatar size="table" :user="user" />
                  <div>
                    <div class="user-name fw-bold d-flex align-items-center gap-1">
                      {{ user.name }}
                      <span class="badge bg-primary-subtle text-primary border text-xs ms-1" v-if="user.id === currentAdminId">My Account</span>
                    </div>
                    <div class="user-reg text-xs text-muted">{{ user.registerNumber }}</div>
                  </div>
                </div>
              </td>

              <!-- Role -->
              <td>
                <span class="role-badge" :class="roleBadge(user.role)">
                  {{ roleLabel(user.role) }}
                </span>
              </td>

              <!-- Department -->
              <td>{{ user.department || '—' }}</td>

              <!-- Club Tags -->
              <td>
                <div class="club-tags" v-if="user.clubs && user.clubs.length">
                  <span
                    v-for="club in user.clubs"
                    :key="club"
                    class="club-tag"
                  >{{ club }}</span>
                </div>
                <span v-else class="no-clubs">None</span>
              </td>

              <!-- Status -->
              <td>
                <span
                  class="status-badge"
                  :class="user.status === 'ACTIVE' ? 'status-active' : 'status-inactive'"
                >
                  <span class="status-dot"></span>
                  {{ user.status === 'ACTIVE' ? 'Active' : 'Blocked' }}
                </span>
              </td>

              <!-- Actions: View + Block -->
              <td>
                <div class="action-cell">
                  <button
                    class="btn-action btn-view"
                    title="View Profile"
                    @click.stop="viewUser(user)"
                  >
                    <i class="bi bi-eye-fill"></i> View
                  </button>
                  <button
                    class="btn-action"
                    :class="user.status === 'ACTIVE' ? 'btn-block' : 'btn-unblock'"
                    :title="user.status === 'ACTIVE' ? 'Block User' : 'Unblock User'"
                    @click="openBlockModal($event, user)"
                  >
                    <i class="bi" :class="user.status === 'ACTIVE' ? 'bi-slash-circle-fill' : 'bi-check-circle-fill'"></i>
                    {{ user.status === 'ACTIVE' ? 'Block' : 'Unblock' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div class="empty-state" v-else>
          <i class="bi bi-people"></i>
          <h4 style="color:#1e293b; margin-bottom:6px;">No users found</h4>
          <p>Try adjusting your search or filter.</p>
        </div>
      </div>

      <!-- ── Block / Unblock Confirmation Modal ── -->
      <Teleport to="body">
        <div v-if="showBlockModal" class="modal-overlay" @click.self="closeBlockModal">
          <div class="delete-modal">
            <div class="delete-icon" :class="userToBlock?.status === 'ACTIVE' ? 'icon-block' : 'icon-unblock'">
              <i class="bi" :class="userToBlock?.status === 'ACTIVE' ? 'bi-slash-circle-fill' : 'bi-check-circle-fill'"></i>
            </div>
            <h4>{{ blockModalTitle }}</h4>
            <p>
              <strong>{{ userToBlock?.name }}</strong> {{ blockModalMsg }}
            </p>
            <div class="modal-actions">
              <button class="btn-cancel" @click="closeBlockModal">Cancel</button>
              <button
                class="btn-confirm-block"
                :class="userToBlock?.status === 'ACTIVE' ? 'confirm-block' : 'confirm-unblock'"
                @click="confirmBlock"
              >{{ blockBtnLabel }}</button>
            </div>
          </div>
        </div>
      </Teleport>

    </section>
  </AdminLayout>
</template>
