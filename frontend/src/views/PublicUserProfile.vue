<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCurrentUser } from '@/services/authService'
import { getUser } from '@/api/users'

import AdminLayout from '@/layouts/AdminLayout.vue'
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'

import UserAvatar from '@/components/profile/UserAvatar.vue'
import UserProfileHeader from '@/components/profile/UserProfileHeader.vue'
import UserInformationCard from '@/components/profile/UserInformationCard.vue'
import RoleBadgeList from '@/components/profile/RoleBadgeList.vue'
import UserProfileView from '@/components/common/UserProfileView.vue'

const route = useRoute()
const router = useRouter()

const currentUser = computed(() => getCurrentUser() || {})
const targetUserId = computed(() => route.params.id || route.params.userId)

const isSelf = computed(() => {
  if (!targetUserId.value) return true
  return String(targetUserId.value) === String(currentUser.value.id)
})

const layoutComponent = computed(() => {
  const r = currentUser.value?.role
  if (r === 'ADMIN') return AdminLayout
  if (r === 'FACULTY') return FacultyLayout
  return StudentLayout
})

const userData = ref(null)
const loading = ref(false)
const errorMsg = ref('')

const userClubs = ref([])
const coordinatorRoles = ref([])
const organizerRoles = ref([])

onMounted(async () => {
  await loadUserData()
})

watch(() => targetUserId.value, async () => {
  await loadUserData()
})

async function loadUserData() {
  if (isSelf.value) return

  loading.value = true
  errorMsg.value = ''
  userData.value = null

  try {
    const u = await getUser(targetUserId.value)
    userData.value = u

    userClubs.value = u.clubs || []
    if (u.role === 'FACULTY') {
      coordinatorRoles.value = (u.clubs || []).map(club => ({ club, role: 'Faculty Coordinator' }))
    } else {
      organizerRoles.value = []
    }
  } catch (err) {
    console.error('Failed to load public user profile', err)
    errorMsg.value = 'User profile not found or unavailable.'
  } finally {
    loading.value = false
  }
}

const formattedUserForm = computed(() => {
  if (!userData.value) return {}
  const u = userData.value
  return {
    fullName: u.fullName || u.name || u.username || 'User',
    email: u.email || '',
    username: u.username || u.email?.split('@')[0] || '',
    phone: u.phone || u.phoneNumber || '',
    department: u.department || 'General',
    role: u.role || 'MEMBER',
    bio: u.bio || '',
    status: u.status || 'ACTIVE',
    avatarStyle: u.avatarStyle || 'adventurer',
    avatarSeed: u.avatarSeed || u.fullName || u.username || 'User'
  }
})
</script>

<template>
  <component :is="layoutComponent">
    <div class="public-profile-container py-4 px-3 px-md-4">
      
      <!-- Back Button -->
      <div class="mb-3">
        <button class="btn btn-sm btn-outline-secondary rounded-pill px-3" @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i> Back
        </button>
      </div>

      <!-- IF VIEWING OWN PROFILE -->
      <UserProfileView v-if="isSelf" :layoutRole="currentUser.role || 'STUDENT'" />

      <!-- IF VIEWING ANOTHER USER'S PROFILE -->
      <template v-else>
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="text-muted mt-2">Loading user profile...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMsg" class="alert alert-warning rounded-4 p-4 text-center">
          <i class="bi bi-exclamation-triangle-fill fs-2 d-block mb-2 text-warning"></i>
          <h5>{{ errorMsg }}</h5>
          <button class="btn btn-primary rounded-pill mt-3 px-4" @click="router.back()">Return Back</button>
        </div>

        <!-- Public Read-Only Profile View -->
        <div v-else class="d-flex flex-column gap-4">
          <!-- 1. HEADER (Read-only, no avatar edit button) -->
          <UserProfileHeader 
            :user="formattedUserForm" 
            :editableAvatar="false" 
          />

          <!-- 2. MAIN CONTENT GRID -->
          <div class="row g-4">
            <!-- Personal Info Card (Read-only) -->
            <div class="col-12 col-lg-7">
              <UserInformationCard 
                :user="formattedUserForm" 
                :isEditing="false" 
              />
            </div>

            <!-- Role Badges & Responsibilities Card -->
            <div class="col-12 col-lg-5 d-flex flex-column gap-4">
              <div class="card border-0 shadow-sm rounded-4 p-4">
                <RoleBadgeList 
                  :role="formattedUserForm.role" 
                  :clubs="userClubs" 
                  :coordinatorRoles="coordinatorRoles"
                  :organizerRoles="organizerRoles"
                />
              </div>
            </div>
          </div>
        </div>
      </template>

    </div>
  </component>
</template>

<style scoped>
.public-profile-container {
  max-width: 1100px;
  margin: 0 auto;
}
</style>
