<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCurrentUser } from '@/services/authService'
import { getUser, updateUser } from '@/api/users'
import { getRequests } from '@/api/requests'
import { getMyClubs } from '@/api/student'
import { getMySupervisedClubs } from '@/api/faculty'
import { useNotifications } from '@/stores/useNotifications'
import { useToast } from '@/composables/useToast'
import api from '@/api/axios'

import UserProfileHeader from '@/components/profile/UserProfileHeader.vue'
import UserInformationCard from '@/components/profile/UserInformationCard.vue'
import RoleBadgeList from '@/components/profile/RoleBadgeList.vue'
import ProfileStatistics from '@/components/profile/ProfileStatistics.vue'
import UserAvatar from '@/components/profile/UserAvatar.vue'

const props = defineProps({
  layoutRole: {
    type: String,
    default: 'STUDENT'
  }
})

const { showToast } = useToast()
const notificationStore = useNotifications()

const userProfile = ref(null)
const loading = ref(true)
const saving = ref(false)
const isEditing = ref(false)

// Form State
const form = ref({
  fullName: '',
  email: '',
  username: '',
  phone: '',
  department: '',
  role: '',
  registerNumber: '',
  year: '',
  designation: '',
  bio: '',
  status: 'ACTIVE',
  createdAt: '',
  avatarStyle: 'adventurer',
  avatarSeed: ''
})

const statsData = ref({
  totalRequests: 0,
  pendingRequests: 0,
  approvedRequests: 0,
  notificationsCount: 0
})

const userClubs = ref([])
const coordinatorRoles = ref([])
const organizerRoles = ref([])

// Avatar Picker Modal State
const showAvatarModal = ref(false)
const selectedStyle = ref('adventurer')
const customSeed = ref('')

const avatarStyles = [
  { id: 'adventurer', name: 'Adventurer' },
  { id: 'pixel-art', name: 'Pixel Art' },
  { id: 'bottts', name: 'Bottts' },
  { id: 'personas', name: 'Personas' },
  { id: 'lorelei', name: 'Lorelei' }
]

const presetSeeds = ['Felix', 'Callie', 'Anerette', 'Oliver', 'Zoe', 'Jack', 'Leo', 'Luna', 'Milo', 'Maya']

// Change Password Modal State
const showPasswordModal = ref(false)
const passwordForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const passwordLoading = ref(false)

onMounted(async () => {
  await loadProfile()
})

async function loadProfile() {
  loading.value = true
  try {
    const stored = getCurrentUser() || {}
    let u = stored
    if (stored.id) {
      u = await getUser(stored.id).catch(() => stored)
    }
    userProfile.value = u

    form.value = {
      fullName: u.fullName || u.name || u.username || 'User',
      email: u.email || '',
      username: u.username || u.email?.split('@')[0] || 'username',
      phone: u.phone || u.phoneNumber || '',
      department: u.department || 'General',
      role: u.role || props.layoutRole,
      registerNumber: u.registerNumber || u.rollNo || u.employeeId || '',
      year: u.year || u.yearOfStudy || (props.layoutRole === 'STUDENT' ? '3rd Year' : ''),
      designation: u.designation || (props.layoutRole === 'FACULTY' ? 'Faculty Advisor' : ''),
      bio: u.bio || '',
      status: u.status || 'ACTIVE',
      createdAt: u.createdAt ? new Date(u.createdAt).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Aug 2025',
      avatarStyle: u.avatarStyle || 'adventurer',
      avatarSeed: u.avatarSeed || u.fullName || u.username || 'User'
    }

    // Load actual club entities with IDs
    try {
      if (u.role === 'FACULTY') {
        const clubsRes = await getMySupervisedClubs().catch(() => [])
        const list = Array.isArray(clubsRes) ? clubsRes : []
        userClubs.value = list.map(c => ({ id: c.id, name: c.clubName || c.name }))
        coordinatorRoles.value = list.map(c => ({ 
          club: c.clubName || c.name, 
          clubId: c.id, 
          role: c.roleTitle || 'Faculty Coordinator' 
        }))
      } else if (u.role === 'STUDENT') {
        const clubsRes = await getMyClubs().catch(() => [])
        const list = Array.isArray(clubsRes) ? clubsRes : []
        if (list.length) {
          userClubs.value = list.map(c => ({ id: c.id, name: c.name || c.clubName, role: c.membershipRole }))
          organizerRoles.value = list
            .filter(c => c.membershipRole && c.membershipRole.toUpperCase() !== 'MEMBER')
            .map(c => ({
              title: c.membershipRole,
              club: c.name || c.clubName,
              clubId: c.id,
              role: c.membershipRole
            }))
        } else {
          userClubs.value = (u.clubs || []).map((c, i) => typeof c === 'object' ? c : { id: i + 1, name: c })
        }
      } else {
        userClubs.value = (u.clubs || []).map((c, i) => typeof c === 'object' ? c : { id: i + 1, name: c })
      }
    } catch (e) {
      userClubs.value = (u.clubs || []).map((c, i) => typeof c === 'object' ? c : { id: i + 1, name: c })
    }

    // Fetch REAL request & notification stats
    try {
      const [reqsRes] = await Promise.all([
        getRequests().catch(() => []),
        notificationStore.fetchInitial().catch(() => {})
      ])
      const list = Array.isArray(reqsRes) ? reqsRes : (reqsRes.data || [])
      const userReqs = list.filter(r => String(r.requesterId || r.userId || r.raisedById) === String(u.id))

      statsData.value = {
        totalRequests: userReqs.length,
        pendingRequests: userReqs.filter(r => r.workflowStatus === 'PENDING' || r.status === 'PENDING').length,
        approvedRequests: userReqs.filter(r => r.workflowStatus === 'APPROVED' || r.status === 'APPROVED').length,
        notificationsCount: notificationStore.notifications.length || 0
      }
    } catch (e) {
      statsData.value = { totalRequests: 0, pendingRequests: 0, approvedRequests: 0, notificationsCount: 0 }
    }

    selectedStyle.value = form.value.avatarStyle
    customSeed.value = form.value.avatarSeed
  } catch (err) {
    console.error('Failed to load profile', err)
  } finally {
    loading.value = false
  }
}

function openAvatarPicker() {
  selectedStyle.value = form.value.avatarStyle || 'adventurer'
  customSeed.value = form.value.avatarSeed || form.value.fullName || 'User'
  showAvatarModal.value = true
}

async function applyAvatar() {
  form.value.avatarStyle = selectedStyle.value
  form.value.avatarSeed = customSeed.value || form.value.fullName || 'User'
  showAvatarModal.value = false

  // Persist directly to backend & localStorage
  if (userProfile.value?.id) {
    try {
      const payload = {
        fullName: form.value.fullName,
        phone: form.value.phone,
        year: form.value.year,
        designation: form.value.designation,
        bio: form.value.bio,
        avatarStyle: form.value.avatarStyle,
        avatarSeed: form.value.avatarSeed
      }

      const updated = await updateUser(userProfile.value.id, payload)
      userProfile.value = { 
        ...userProfile.value, 
        ...updated, 
        avatarStyle: form.value.avatarStyle, 
        avatarSeed: form.value.avatarSeed 
      }

      // Sync localStorage
      const currentStored = getCurrentUser() || {}
      localStorage.setItem('user', JSON.stringify({ 
        ...currentStored, 
        ...updated, 
        avatarStyle: form.value.avatarStyle, 
        avatarSeed: form.value.avatarSeed 
      }))

      window.dispatchEvent(new Event('storage'))
      showToast('Avatar updated and saved!', 'success')
    } catch (err) {
      console.error('Failed to auto-save avatar', err)
      showToast('Avatar updated in preview! Click Save Profile Changes to persist.', 'info')
    }
  } else {
    showToast('Avatar updated!', 'success')
  }
}

async function handleSaveProfile() {
  if (!userProfile.value?.id) return
  saving.value = true
  try {
    const payload = {
      fullName: form.value.fullName,
      phone: form.value.phone,
      year: form.value.year,
      designation: form.value.designation,
      bio: form.value.bio,
      avatarStyle: form.value.avatarStyle,
      avatarSeed: form.value.avatarSeed
    }

    const updated = await updateUser(userProfile.value.id, payload)
    userProfile.value = { 
      ...userProfile.value, 
      ...updated, 
      avatarStyle: form.value.avatarStyle, 
      avatarSeed: form.value.avatarSeed 
    }

    // Sync localStorage
    const currentStored = getCurrentUser() || {}
    localStorage.setItem('user', JSON.stringify({ 
      ...currentStored, 
      ...updated, 
      avatarStyle: form.value.avatarStyle, 
      avatarSeed: form.value.avatarSeed 
    }))

    window.dispatchEvent(new Event('storage'))
    showToast('Profile updated successfully!', 'success')
    isEditing.value = false
  } catch (err) {
    showToast('Failed to update profile.', 'error')
    console.error(err)
  } finally {
    saving.value = false
  }
}

async function handlePasswordChange() {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    return showToast('Please fill in both current and new password.', 'warning')
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    return showToast('New passwords do not match.', 'warning')
  }

  passwordLoading.value = true
  try {
    await api.post('/auth/change-password', {
      oldPassword: passwordForm.value.oldPassword,
      newPassword: passwordForm.value.newPassword
    })
    showToast('Password changed successfully!', 'success')
    showPasswordModal.value = false
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to change password.'
    showToast(msg, 'error')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<template>
  <div class="user-profile-wrapper">
    <!-- Loading Spinner -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2">Loading profile details...</p>
    </div>

    <div v-else class="profile-container d-flex flex-column gap-4">
      
      <!-- 1. REUSABLE USER PROFILE HEADER -->
      <UserProfileHeader 
        :user="form" 
        :editableAvatar="true" 
        @edit-avatar="openAvatarPicker"
      >
        <template #actions>
          <button 
            class="btn btn-outline-secondary rounded-pill px-3 text-xs fw-semibold"
            @click="showPasswordModal = true"
          >
            <i class="bi bi-key-fill me-1"></i> Change Password
          </button>
          <button 
            class="btn rounded-pill px-4 text-xs font-semibold"
            :class="isEditing ? 'btn-outline-danger' : 'btn-primary'"
            @click="isEditing = !isEditing"
          >
            <i :class="isEditing ? 'bi bi-x-circle me-1' : 'bi bi-pencil-fill me-1'"></i>
            {{ isEditing ? 'Cancel Editing' : 'Edit Profile' }}
          </button>
        </template>
      </UserProfileHeader>

      <!-- 2. REUSABLE PROFILE STATISTICS -->
      <ProfileStatistics :stats="statsData" />

      <!-- 3. MAIN CONTENT GRID -->
      <div class="row g-4">
        
        <!-- PERSONAL INFORMATION CARD -->
        <div class="col-12 col-lg-7">
          <UserInformationCard 
            :user="form" 
            :isEditing="isEditing" 
            :saving="saving"
            @save="handleSaveProfile"
          />
        </div>

        <!-- ACCOUNT DETAILS & ROLE BADGES -->
        <div class="col-12 col-lg-5 d-flex flex-column gap-4">
          <div class="card border-0 shadow-sm rounded-4 p-4">
            <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
              <h5 class="fw-bold text-dark m-0 d-flex align-items-center gap-2">
                <span class="material-symbols-rounded text-primary">badge</span>
                Account Metadata
              </h5>
            </div>

            <div class="account-details-list d-flex flex-column gap-3">
              <div class="info-tile p-3 bg-light rounded-3 border">
                <span class="text-xs text-uppercase fw-bold text-muted d-block mb-1">Username</span>
                <span class="fw-semibold text-dark fs-6">{{ form.username }}</span>
              </div>

              <div class="info-tile p-3 bg-light rounded-3 border">
                <span class="text-xs text-uppercase fw-bold text-muted d-block mb-1">Assigned System Role</span>
                <div class="d-flex align-items-center justify-content-between">
                  <span class="badge bg-primary px-3 py-1.5 rounded-pill">{{ form.role }}</span>
                  <small class="text-xs text-muted"><i class="bi bi-lock me-1"></i>Managed by Admin</small>
                </div>
              </div>

              <div class="info-tile p-3 bg-light rounded-3 border">
                <span class="text-xs text-uppercase fw-bold text-muted d-block mb-1">Account Creation Date</span>
                <span class="fw-semibold text-dark">{{ form.createdAt }}</span>
              </div>
            </div>
          </div>

          <!-- REUSABLE ROLE BADGE LIST -->
          <div class="card border-0 shadow-sm rounded-4 p-4">
            <RoleBadgeList 
              :role="form.role" 
              :clubs="userClubs" 
              :coordinatorRoles="coordinatorRoles"
              :organizerRoles="organizerRoles"
            />
          </div>
        </div>

      </div>
    </div>

    <!-- DICEBEAR AVATAR SELECTION MODAL -->
    <div v-if="showAvatarModal" class="modal-backdrop-custom" @click.self="showAvatarModal = false">
      <div class="avatar-picker-card card border-0 shadow-lg rounded-4 p-4">
        <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
          <h5 class="fw-bold m-0 text-dark d-flex align-items-center gap-2">
            <span class="material-symbols-rounded text-primary">palette</span>
            DiceBear Avatar Generator
          </h5>
          <button class="btn-close" @click="showAvatarModal = false"></button>
        </div>

        <div class="avatar-picker-body">
          <div class="text-center mb-4 p-3 bg-light rounded-4 border">
            <UserAvatar 
              :style="selectedStyle" 
              :seed="customSeed || form.fullName"
              :size="80"
              class="mx-auto mb-2"
            />
            <p class="text-xs text-muted m-0">Live Preview: <strong>{{ selectedStyle }}</strong> / <em>{{ customSeed || 'Default' }}</em></p>
          </div>

          <label class="form-label text-xs fw-bold text-uppercase text-muted mb-2">1. Choose Avatar Style</label>
          <div class="row g-2 mb-3">
            <div v-for="s in avatarStyles" :key="s.id" class="col-6 col-sm-4">
              <div 
                class="style-card p-2 text-center rounded-3 border cursor-pointer"
                :class="{ 'border-primary bg-primary-subtle text-primary fw-bold': selectedStyle === s.id }"
                @click="selectedStyle = s.id"
              >
                <UserAvatar :style="s.id" :seed="customSeed || form.fullName" :size="38" class="mx-auto mb-1" />
                <div class="text-xs">{{ s.name }}</div>
              </div>
            </div>
          </div>

          <label class="form-label text-xs fw-bold text-uppercase text-muted mb-1">2. Customize Avatar Seed</label>
          <input 
            type="text" 
            class="form-control rounded-3 mb-2" 
            v-model="customSeed" 
            placeholder="Type any word/name to generate unique variation..." 
          />

          <div class="d-flex flex-wrap gap-1 mb-4">
            <span class="text-xs text-muted me-1">Presets:</span>
            <span 
              v-for="seed in presetSeeds" 
              :key="seed"
              class="badge bg-light text-dark border cursor-pointer hover-badge text-xs"
              @click="customSeed = seed"
            >
              {{ seed }}
            </span>
          </div>

          <div class="d-flex justify-content-end gap-2 border-top pt-3">
            <button class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showAvatarModal = false">Cancel</button>
            <button class="btn btn-primary rounded-pill px-4 text-xs font-semibold" @click="applyAvatar">Use Selected Avatar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- CHANGE PASSWORD MODAL -->
    <div v-if="showPasswordModal" class="modal-backdrop-custom" @click.self="showPasswordModal = false">
      <div class="password-card card border-0 shadow-lg rounded-4 p-4">
        <div class="d-flex justify-content-between align-items-center mb-3 border-bottom pb-2">
          <h5 class="fw-bold m-0 text-dark d-flex align-items-center gap-2">
            <span class="material-symbols-rounded text-primary">key</span>
            Change Account Password
          </h5>
          <button class="btn-close" @click="showPasswordModal = false"></button>
        </div>

        <form @submit.prevent="handlePasswordChange" class="d-flex flex-column gap-3">
          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">Current Password</label>
            <input type="password" class="form-control rounded-3" v-model="passwordForm.oldPassword" required />
          </div>

          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">New Password</label>
            <input type="password" class="form-control rounded-3" v-model="passwordForm.newPassword" required />
          </div>

          <div>
            <label class="form-label text-xs fw-bold text-uppercase text-muted">Confirm New Password</label>
            <input type="password" class="form-control rounded-3" v-model="passwordForm.confirmPassword" required />
          </div>

          <div class="d-flex justify-content-end gap-2 border-top pt-3 mt-2">
            <button type="button" class="btn btn-outline-secondary rounded-pill px-3 text-xs" @click="showPasswordModal = false">Cancel</button>
            <button type="submit" class="btn btn-primary rounded-pill px-4 text-xs font-semibold" :disabled="passwordLoading">
              {{ passwordLoading ? 'Updating Password...' : 'Update Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
.user-profile-wrapper {
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

.avatar-picker-card,
.password-card {
  width: 100%;
  max-width: 520px;
}

.style-card {
  transition: all 0.2s ease;
}

.style-card:hover {
  border-color: #2563eb !important;
  transform: translateY(-2px);
}

.hover-badge:hover {
  background-color: #2563eb !important;
  color: #ffffff !important;
}

.cursor-pointer {
  cursor: pointer;
}
</style>
