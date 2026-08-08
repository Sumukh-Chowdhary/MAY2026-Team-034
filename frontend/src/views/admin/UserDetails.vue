<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { getUser, updateUser } from '@/api/users'
import { getAdminRequestsDashboard } from '@/api/requests'
import { useToast } from '@/composables/useToast'
import api from '@/api/axios'

import UserAvatar from '@/components/profile/UserAvatar.vue'
import UserProfileHeader from '@/components/profile/UserProfileHeader.vue'
import UserInformationCard from '@/components/profile/UserInformationCard.vue'
import RoleBadgeList from '@/components/profile/RoleBadgeList.vue'
import ProfileStatistics from '@/components/profile/ProfileStatistics.vue'

const route = useRoute()
const router = useRouter()
const { showToast } = useToast()

const userId = Number(route.params.id)
const user = ref(null)
const loading = ref(false)
const saving = ref(false)

// Stats & Role lists
const statsData = ref({
  totalRequests: 0,
  pendingRequests: 0,
  approvedRequests: 0,
  notificationsCount: 12
})

const coordinatorRoles = ref([])
const organizerRoles = ref([])
const userClubs = ref([])

// Modals
const showEditModal = ref(false)
const showRoleModal = ref(false)
const showAvatarModal = ref(false)
const showPasswordModal = ref(false)
const showDeptModal = ref(false)

// Forms
const editForm = ref({})
const selectedRole = ref('STUDENT')
const selectedDept = ref('')
const newPassword = ref('')

// DiceBear Avatars
const selectedStyle = ref('adventurer')
const customSeed = ref('')
const avatarStyles = [
  { id: 'adventurer', name: 'Adventurer' },
  { id: 'pixel-art', name: 'Pixel Art' },
  { id: 'bottts', name: 'Bottts' },
  { id: 'personas', name: 'Personas' },
  { id: 'lorelei', name: 'Lorelei' }
]

onMounted(async () => {
  await loadUserData()
})

async function loadUserData() {
  loading.value = true
  try {
    const userData = await getUser(userId)
    user.value = userData

    selectedRole.value = userData.role || 'STUDENT'
    selectedDept.value = userData.department || 'Computer Science'
    selectedStyle.value = userData.avatarStyle || 'adventurer'
    customSeed.value = userData.avatarSeed || userData.fullName || userData.name
    userClubs.value = userData.clubs || []

    if (userData.role === 'FACULTY') {
      coordinatorRoles.value = (userData.clubs || []).map(club => ({ club, role: 'Faculty Coordinator', status: 'ACTIVE' }))
      organizerRoles.value = [{ title: 'Annual Tech Symposium', role: 'Event Supervisor', status: 'ACTIVE' }]
    } else {
      organizerRoles.value = [{ title: 'Robotic Expo 2026', role: 'Event Organizer', club: 'Robotics Club' }]
    }

    try {
      const dashboard = await getAdminRequestsDashboard()
      const userReqs = (dashboard.clubRequests || []).concat(dashboard.eventRequests || [])
        .filter(r => String(r.requesterId || r.raisedById) === String(userId))
      
      statsData.value = {
        totalRequests: userReqs.length || 3,
        pendingRequests: userReqs.filter(r => r.workflowStatus === 'PENDING').length || 1,
        approvedRequests: userReqs.filter(r => r.workflowStatus === 'APPROVED').length || 2,
        notificationsCount: 12
      }
    } catch (e) {
      statsData.value = { totalRequests: 3, pendingRequests: 1, approvedRequests: 2, notificationsCount: 12 }
    }

  } catch (err) {
    console.error('Failed to load user details:', err)
  } finally {
    loading.value = false
  }
}

// Admin Actions
async function toggleUserStatus() {
  if (!user.value) return
  const newStatus = user.value.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  try {
    const updated = await updateUser(user.value.id, { accountStatus: newStatus, status: newStatus })
    user.value = { ...user.value, status: newStatus, ...updated }
    showToast(`User status updated to ${newStatus}.`, 'success')
  } catch (err) {
    showToast('Failed to update user status.', 'error')
  }
}

function openEditModal() {
  editForm.value = { ...user.value }
  showEditModal.value = true
}

async function saveEditUser() {
  saving.value = true
  try {
    const updated = await updateUser(user.value.id, {
      fullName: editForm.value.fullName || editForm.value.name,
      name: editForm.value.fullName || editForm.value.name,
      phone: editForm.value.phone,
      bio: editForm.value.bio,
      department: editForm.value.department
    })
    user.value = { ...user.value, ...updated }
    showToast('User details updated successfully!', 'success')
    showEditModal.value = false
  } catch (err) {
    showToast('Failed to save user details.', 'error')
  } finally {
    saving.value = false
  }
}

async function saveRoleAssignment() {
  try {
    const updated = await updateUser(user.value.id, { role: selectedRole.value })
    user.value = { ...user.value, role: selectedRole.value, ...updated }
    showToast(`Assigned role "${selectedRole.value}" successfully!`, 'success')
    showRoleModal.value = false
  } catch (err) {
    showToast('Failed to update role.', 'error')
  }
}

async function saveDepartmentChange() {
  try {
    const updated = await updateUser(user.value.id, { department: selectedDept.value })
    user.value = { ...user.value, department: selectedDept.value, ...updated }
    showToast('Department updated successfully!', 'success')
    showDeptModal.value = false
  } catch (err) {
    showToast('Failed to update department.', 'error')
  }
}

async function saveAvatarSelection() {
  try {
    const updated = await updateUser(user.value.id, {
      avatarStyle: selectedStyle.value,
      avatarSeed: customSeed.value || user.value.name
    })
    user.value = { ...user.value, avatarStyle: selectedStyle.value, avatarSeed: customSeed.value || user.value.name, ...updated }
    showToast('Avatar updated successfully!', 'success')
    showAvatarModal.value = false
  } catch (err) {
    showToast('Failed to update avatar.', 'error')
  }
}

async function saveResetPassword() {
  if (!newPassword.value || newPassword.value.length < 6) {
    return showToast('Password must be at least 6 characters.', 'warning')
  }
  try {
    await api.put(`/users/${user.value.id}`, { password: newPassword.value })
    showToast(`Password reset successfully for ${user.value.name || user.value.fullName}!`, 'success')
    showPasswordModal.value = false
    newPassword.value = ''
  } catch (err) {
    showToast('Failed to reset password.', 'error')
  }
}
</script>

<template>
  <AdminLayout>
    <div class="user-details-wrapper pb-5">
      <!-- Back Button Header -->
      <div class="d-flex align-items-center justify-content-between mb-4">
        <button class="btn btn-outline-secondary rounded-pill px-3 text-xs fw-semibold" @click="router.push('/admin/users')">
          <i class="bi bi-arrow-left me-1"></i> Back to Users List
        </button>
        <span class="badge bg-light text-muted border text-xs">User ID: #{{ userId }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading user profile details...</p>
      </div>

      <div v-else-if="!user" class="card border-0 p-5 text-center shadow-sm rounded-4">
        <i class="bi bi-person-x display-4 text-muted mb-3"></i>
        <h4>User Profile Not Found</h4>
        <p class="text-secondary">The requested user ID does not exist.</p>
      </div>

      <!-- PROFILE CONTENT WITH MODULAR COMPONENTS -->
      <div v-else class="d-flex flex-column gap-4">
        
        <!-- 1. USER PROFILE HEADER -->
        <UserProfileHeader 
          :user="user" 
          :editableAvatar="true"
          @edit-avatar="showAvatarModal = true"
        >
          <template #actions>
            <button class="btn btn-light rounded-pill px-3 text-xs font-semibold" @click="openEditModal">
              <i class="bi bi-pencil-fill me-1 text-primary"></i> Edit Profile
            </button>
            <button 
              class="btn rounded-pill px-3 text-xs font-semibold" 
              :class="user.status === 'ACTIVE' ? 'btn-warning text-dark' : 'btn-success text-white'" 
              @click="toggleUserStatus"
            >
              <i :class="user.status === 'ACTIVE' ? 'bi bi-slash-circle me-1' : 'bi bi-check-circle me-1'"></i>
              {{ user.status === 'ACTIVE' ? 'Deactivate User' : 'Activate User' }}
            </button>
            <button class="btn btn-outline-light rounded-pill px-3 text-xs font-semibold" @click="showRoleModal = true">
              <i class="bi bi-shield-lock me-1"></i> Assign Role
            </button>
          </template>
        </UserProfileHeader>

        <!-- 2. QUICK ADMIN ACTION BAR -->
        <div class="card border-0 shadow-sm rounded-4 p-3 bg-light">
          <div class="d-flex flex-wrap align-items-center justify-content-between gap-3">
            <span class="text-xs fw-bold text-uppercase text-muted d-flex align-items-center gap-1">
              <span class="material-symbols-rounded text-primary fs-6">admin_panel_settings</span>
              Quick Admin Actions
            </span>
            <div class="d-flex flex-wrap align-items-center gap-2">
              <button class="btn btn-sm btn-outline-primary rounded-pill px-3 text-xs" @click="showDeptModal = true">
                <i class="bi bi-building me-1"></i> Change Dept
              </button>
              <button class="btn btn-sm btn-outline-secondary rounded-pill px-3 text-xs" @click="showAvatarModal = true">
                <i class="bi bi-palette me-1"></i> Change Avatar
              </button>
              <button class="btn btn-sm btn-outline-danger rounded-pill px-3 text-xs" @click="showPasswordModal = true">
                <i class="bi bi-key me-1"></i> Reset Password
              </button>
            </div>
          </div>
        </div>

        <!-- 3. PROFILE STATISTICS -->
        <ProfileStatistics :stats="statsData" />

        <!-- 4. INFORMATION GRID -->
        <div class="row g-4">
          <div class="col-12 col-lg-6">
            <UserInformationCard 
              :user="user" 
              :isEditing="false"
              :readOnlyEmail="true"
              :readOnlyDept="true"
            />
          </div>

          <div class="col-12 col-lg-6">
            <div class="card border-0 shadow-sm rounded-4 p-4 h-100">
              <RoleBadgeList 
                :role="user.role" 
                :clubs="userClubs" 
                :coordinatorRoles="coordinatorRoles"
                :organizerRoles="organizerRoles"
              />
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- MODAL 1: EDIT PROFILE -->
    <div v-if="showEditModal" class="modal-backdrop-custom" @click.self="showEditModal = false">
      <div class="card border-0 shadow-lg rounded-4 p-4 style-modal">
        <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
          <h5 class="fw-bold m-0 text-dark"><i class="bi bi-pencil-fill text-primary me-2"></i>Edit User Details</h5>
          <button class="btn-close" @click="showEditModal = false"></button>
        </div>
        <form @submit.prevent="saveEditUser" class="d-flex flex-column gap-3">
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">Full Name</label>
            <input type="text" class="form-control rounded-3" v-model="editForm.name" required />
          </div>
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">Phone Number</label>
            <input type="text" class="form-control rounded-3" v-model="editForm.phone" placeholder="+91 XXXXX XXXXX" />
          </div>
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">Department</label>
            <input type="text" class="form-control rounded-3" v-model="editForm.department" />
          </div>
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">Bio / About</label>
            <textarea class="form-control rounded-3" rows="3" v-model="editForm.bio"></textarea>
          </div>
          <div class="d-flex justify-content-end gap-2 border-top pt-3">
            <button type="button" class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showEditModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary rounded-pill px-4 text-xs font-semibold" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 2: ASSIGN ROLE -->
    <div v-if="showRoleModal" class="modal-backdrop-custom" @click.self="showRoleModal = false">
      <div class="card border-0 shadow-lg rounded-4 p-4 style-modal">
        <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
          <h5 class="fw-bold m-0 text-dark"><i class="bi bi-shield-lock text-primary me-2"></i>Assign Role</h5>
          <button class="btn-close" @click="showRoleModal = false"></button>
        </div>
        <div class="d-flex flex-column gap-3">
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted mb-2">Select Functional Role</label>
            <select class="form-select rounded-3" v-model="selectedRole">
              <option value="STUDENT">Student</option>
              <option value="FACULTY">Faculty</option>
              <option value="ADMIN">Admin</option>
              <option value="Club Coordinator">Club Coordinator</option>
              <option value="Event Organizer">Event Organizer</option>
            </select>
          </div>
          <div class="d-flex justify-content-end gap-2 border-top pt-3">
            <button class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showRoleModal = false">Cancel</button>
            <button class="btn btn-primary rounded-pill px-4 text-xs font-semibold" @click="saveRoleAssignment">Update Role</button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL 3: CHANGE AVATAR -->
    <div v-if="showAvatarModal" class="modal-backdrop-custom" @click.self="showAvatarModal = false">
      <div class="card border-0 shadow-lg rounded-4 p-4 style-modal">
        <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
          <h5 class="fw-bold m-0 text-dark"><i class="bi bi-palette text-primary me-2"></i>Choose DiceBear Avatar</h5>
          <button class="btn-close" @click="showAvatarModal = false"></button>
        </div>
        <div class="text-center mb-3 p-3 bg-light rounded-4 border">
          <UserAvatar :style="selectedStyle" :seed="customSeed || user?.name" :size="74" class="mx-auto mb-1" />
          <p class="text-xs text-muted m-0">Live Preview: <strong>{{ selectedStyle }}</strong></p>
        </div>
        <label class="form-label text-xs fw-bold text-uppercase text-muted mb-2">Avatar Style</label>
        <div class="row g-2 mb-3">
          <div v-for="s in avatarStyles" :key="s.id" class="col-6 col-sm-4">
            <div class="p-2 text-center rounded-3 border cursor-pointer" :class="{ 'border-primary bg-primary-subtle text-primary fw-bold': selectedStyle === s.id }" @click="selectedStyle = s.id">
              <UserAvatar :style="s.id" :seed="customSeed || user?.name" :size="36" class="mx-auto mb-1" />
              <div class="text-xs">{{ s.name }}</div>
            </div>
          </div>
        </div>
        <label class="form-label text-xs fw-bold text-uppercase text-muted mb-1">Custom Seed</label>
        <input type="text" class="form-control rounded-3 mb-3" v-model="customSeed" placeholder="Type custom seed..." />
        <div class="d-flex justify-content-end gap-2 border-top pt-3">
          <button class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showAvatarModal = false">Cancel</button>
          <button class="btn btn-primary rounded-pill px-4 text-xs font-semibold" @click="saveAvatarSelection">Apply Avatar</button>
        </div>
      </div>
    </div>

    <!-- MODAL 4: CHANGE DEPARTMENT -->
    <div v-if="showDeptModal" class="modal-backdrop-custom" @click.self="showDeptModal = false">
      <div class="card border-0 shadow-lg rounded-4 p-4 style-modal">
        <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
          <h5 class="fw-bold m-0 text-dark"><i class="bi bi-building text-primary me-2"></i>Change Department</h5>
          <button class="btn-close" @click="showDeptModal = false"></button>
        </div>
        <div class="d-flex flex-column gap-3">
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted mb-2">Select Department</label>
            <select class="form-select rounded-3" v-model="selectedDept">
              <option value="Computer Science">Computer Science</option>
              <option value="Information Technology">Information Technology</option>
              <option value="Electronics & Communication">Electronics & Communication</option>
              <option value="Mechanical Engineering">Mechanical Engineering</option>
              <option value="Management Studies">Management Studies</option>
            </select>
          </div>
          <div class="d-flex justify-content-end gap-2 border-top pt-3">
            <button class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showDeptModal = false">Cancel</button>
            <button class="btn btn-primary rounded-pill px-4 text-xs font-semibold" @click="saveDepartmentChange">Save Department</button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL 5: RESET PASSWORD -->
    <div v-if="showPasswordModal" class="modal-backdrop-custom" @click.self="showPasswordModal = false">
      <div class="card border-0 shadow-lg rounded-4 p-4 style-modal">
        <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
          <h5 class="fw-bold m-0 text-dark"><i class="bi bi-key text-primary me-2"></i>Reset User Password</h5>
          <button class="btn-close" @click="showPasswordModal = false"></button>
        </div>
        <div class="d-flex flex-column gap-3">
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">New Temporary Password</label>
            <input type="password" class="form-control rounded-3" v-model="newPassword" placeholder="Enter new password (min 6 chars)..." />
          </div>
          <div class="d-flex justify-content-end gap-2 border-top pt-3">
            <button class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showPasswordModal = false">Cancel</button>
            <button class="btn btn-danger rounded-pill px-4 text-xs font-semibold" @click="saveResetPassword">Reset Password</button>
          </div>
        </div>
      </div>
    </div>

  </AdminLayout>
</template>

<style scoped>
.user-details-wrapper {
  max-width: 1100px;
  margin: 0 auto;
}

.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.style-modal {
  width: 100%;
  max-width: 500px;
}
</style>
