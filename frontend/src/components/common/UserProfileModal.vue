<script setup>
import { ref, computed, watch } from 'vue'
import { getUser } from '@/api/users'
import { getCurrentUser } from '@/services/authService'
import UserAvatar from '@/components/profile/UserAvatar.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  userId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close'])

const userData = ref(null)
const loading = ref(false)
const errorMsg = ref('')

const loggedInUser = computed(() => getCurrentUser() || {})
const viewerRole = computed(() => (loggedInUser.value?.role || 'STUDENT').toUpperCase())

const isSelf = computed(() => {
  if (!props.userId || !loggedInUser.value?.id) return false
  return String(props.userId) === String(loggedInUser.value.id)
})

const canSeePhone = computed(() => {
  if (isSelf.value) return true
  if (viewerRole.value === 'ADMIN' || viewerRole.value === 'FACULTY') return true
  return false
})

watch([() => props.show, () => props.userId], async ([newShow, newId]) => {
  if (newShow && newId) {
    loading.value = true
    errorMsg.value = ''
    userData.value = null
    try {
      const u = await getUser(newId)
      userData.value = u
    } catch (err) {
      console.error('Failed to load profile in UserProfileModal', err)
      errorMsg.value = 'User profile information unavailable.'
    } finally {
      loading.value = false
    }
  }
})

const targetRole = computed(() => {
  if (!userData.value) return 'MEMBER'
  return (userData.value.role || 'MEMBER').toUpperCase()
})

function roleBadgeClass(role, designation) {
  if (designation === 'PRINCIPAL') return 'bg-warning text-dark'
  if (role === 'ADMIN') return 'bg-danger text-white'
  if (role === 'FACULTY') return 'bg-primary text-white'
  return 'bg-info text-dark'
}

// Compute safe, role-appropriate, non-sensitive profile fields
const profileFields = computed(() => {
  if (!userData.value) return []
  const u = userData.value
  const role = targetRole.value
  const fields = []

  // 1. Register / ID / Employee Number (if present)
  const regNo = u.registerNumber || u.rollNo || u.employeeId
  if (regNo) {
    const label = role === 'FACULTY' ? 'Employee ID' : 'Register / ID No.'
    fields.push({ label, value: regNo })
  }

  // 2. Department (if present)
  if (u.department) {
    fields.push({ label: 'Department', value: u.department })
  }

  // 3. Year of Study (ONLY for Student role!)
  if (role === 'STUDENT' && (u.yearOfStudy || u.year)) {
    fields.push({ label: 'Year of Study', value: u.yearOfStudy || u.year })
  }

  // 4. Designation (ONLY for Faculty role!)
  if (role === 'FACULTY' && u.designation) {
    fields.push({ label: 'Designation', value: u.designation })
  }

  // 5. Phone Number (ONLY if viewer is authorized and phone is returned!)
  const phoneVal = u.phone || u.phoneNumber
  if (canSeePhone.value && phoneVal) {
    fields.push({ label: 'Phone', value: phoneVal })
  }

  // 6. Email (Always included)
  if (u.email) {
    fields.push({ label: 'Email', value: u.email })
  }

  // 7. Account Status
  fields.push({ 
    label: 'Account Status', 
    value: u.status || u.accountStatus || 'ACTIVE',
    isBadge: true 
  })

  return fields
})
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="profile-modal-overlay" @click.self="$emit('close')">
      <div class="profile-modal-card shadow-2xl">
        
        <!-- Header -->
        <div class="modal-header-glass">
          <h5 class="fw-bold mb-0">
            <i class="bi bi-person-badge-fill me-2 text-primary"></i>
            User Profile Details
          </h5>
          <button class="btn-close-glass" @click="$emit('close')" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Body -->
        <div class="modal-body-glass">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="text-muted mt-2 text-sm">Loading user profile...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="errorMsg" class="text-center py-4 text-muted">
            <i class="bi bi-exclamation-circle fs-2 d-block mb-2 text-warning"></i>
            <p class="mb-0">{{ errorMsg }}</p>
          </div>

          <!-- Profile Details -->
          <div v-else-if="userData" class="profile-content">
            
            <!-- User Avatar & Core Banner -->
            <div class="avatar-banner d-flex align-items-center gap-3 p-3 bg-light rounded-3 mb-3">
              <UserAvatar size="card" :user="userData" />
              <div>
                <h5 class="fw-bold text-dark mb-1">{{ userData.fullName || userData.name || 'User' }}</h5>
                <span class="badge" :class="roleBadgeClass(targetRole, userData.designation)">
                  {{ userData.designation || targetRole }}
                </span>
                <small class="text-muted d-block mt-1">{{ userData.email }}</small>
              </div>
            </div>

            <!-- Profile Details Grid (Dynamic & Self-Reflowing) -->
            <div class="row g-3 text-sm">
              <div 
                v-for="field in profileFields" 
                :key="field.label" 
                class="col-6"
              >
                <span class="text-muted d-block text-xs uppercase fw-bold mb-1">{{ field.label }}</span>
                
                <span v-if="field.isBadge" class="badge" :class="field.value === 'ACTIVE' ? 'bg-success' : 'bg-secondary'">
                  {{ field.value }}
                </span>
                <strong v-else class="text-dark d-block text-truncate">{{ field.value }}</strong>
              </div>

              <!-- Bio Box (Full-width if present) -->
              <div class="col-12" v-if="userData.bio">
                <span class="text-muted d-block text-xs uppercase fw-bold mb-1">Bio / Notes</span>
                <p class="bio-box text-secondary bg-white p-2.5 border rounded-2 mb-0">{{ userData.bio }}</p>
              </div>
            </div>

          </div>

          <div v-else class="text-center text-muted py-4">
            Could not load profile information.
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer-glass">
          <button class="btn btn-secondary rounded-pill px-4 btn-sm" @click="$emit('close')">
            Close Profile
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.profile-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1070;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.profile-modal-card {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.modal-header-glass {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close-glass {
  background: #f1f5f9;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
}

.modal-body-glass {
  padding: 1.25rem;
  max-height: 70vh;
  overflow-y: auto;
}

.bio-box {
  font-size: 0.825rem;
  line-height: 1.4;
}

.modal-footer-glass {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}
</style>
