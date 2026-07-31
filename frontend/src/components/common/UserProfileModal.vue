<script setup>
import { ref, watch } from 'vue'
import { getUser } from '@/api/users'

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

watch([() => props.show, () => props.userId], async ([newShow, newId]) => {
  if (newShow && newId) {
    loading.value = true
    userData.value = null
    try {
      const u = await getUser(newId)
      userData.value = u
    } catch (err) {
      console.error('Failed to load profile in UserProfileModal', err)
    } finally {
      loading.value = false
    }
  }
})

function roleBadgeClass(role, designation) {
  if (designation === 'PRINCIPAL') return 'bg-warning text-dark'
  if (role === 'ADMIN') return 'bg-danger text-white'
  if (role === 'FACULTY') return 'bg-primary text-white'
  return 'bg-info text-dark'
}
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
          <button class="btn-close-glass" @click="$emit('close')"><i class="bi bi-x-lg"></i></button>
        </div>

        <!-- Body -->
        <div class="modal-body-glass">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="text-muted mt-2 text-sm">Loading user profile...</p>
          </div>

          <div v-else-if="userData" class="profile-content">
            
            <!-- User Avatar & Core Banner -->
            <div class="avatar-banner d-flex align-items-center gap-3 p-3 bg-light rounded-3 mb-3">
              <div class="user-avatar-lg">
                {{ (userData.fullName || userData.name || 'U').charAt(0).toUpperCase() }}
              </div>
              <div>
                <h5 class="fw-bold text-dark mb-1">{{ userData.fullName || userData.name }}</h5>
                <span class="badge" :class="roleBadgeClass(userData.role, userData.designation)">
                  {{ userData.designation || userData.role }}
                </span>
                <small class="text-muted d-block mt-1">{{ userData.email }}</small>
              </div>
            </div>

            <!-- Profile Details Grid -->
            <div class="row g-3 text-sm">
              <div class="col-6">
                <span class="text-muted d-block text-xs uppercase fw-bold">Register / ID No.</span>
                <strong class="text-dark">{{ userData.registerNumber || userData.rollNo || userData.employeeId || 'N/A' }}</strong>
              </div>

              <div class="col-6">
                <span class="text-muted d-block text-xs uppercase fw-bold">Department</span>
                <strong class="text-dark">{{ userData.department || 'N/A' }}</strong>
              </div>

              <div class="col-6" v-if="userData.year || userData.yearOfStudy">
                <span class="text-muted d-block text-xs uppercase fw-bold">Year of Study</span>
                <strong class="text-dark">{{ userData.year || userData.yearOfStudy }}</strong>
              </div>

              <div class="col-6" v-if="userData.designation">
                <span class="text-muted d-block text-xs uppercase fw-bold">Designation</span>
                <strong class="text-dark">{{ userData.designation }}</strong>
              </div>

              <div class="col-6">
                <span class="text-muted d-block text-xs uppercase fw-bold">Phone</span>
                <strong class="text-dark">{{ userData.phone || 'N/A' }}</strong>
              </div>

              <div class="col-6">
                <span class="text-muted d-block text-xs uppercase fw-bold">Account Status</span>
                <span class="badge" :class="userData.status === 'ACTIVE' ? 'bg-success' : 'bg-secondary'">
                  {{ userData.status || 'ACTIVE' }}
                </span>
              </div>

              <div class="col-12" v-if="userData.bio">
                <span class="text-muted d-block text-xs uppercase fw-bold mb-1">Bio / Notes</span>
                <p class="bio-box text-secondary bg-white p-2 border rounded-2 mb-0">{{ userData.bio }}</p>
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

.user-avatar-lg {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  font-weight: 700;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
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
