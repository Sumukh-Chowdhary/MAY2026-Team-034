<script setup>
import { ref, onMounted } from 'vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { getUser, updateUser } from '@/api/users'

const userProfile = ref(null)
const loading = ref(true)
const saving = ref(false)

const form = ref({
  fullName: '',
  phone: '',
  year: '',
  bio: '',
  department: '',
  email: '',
  registerNumber: '',
  status: 'ACTIVE'
})

onMounted(async () => {
  await loadProfile()
})

async function loadProfile() {
  loading.value = true
  try {
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
    let u = storedUser
    if (storedUser.id) {
      u = await getUser(storedUser.id).catch(() => storedUser)
    }
    userProfile.value = u
    form.value = {
      fullName: u.fullName || u.name || '',
      phone: u.phone || u.phoneNumber || '',
      year: u.year || u.yearOfStudy || '3rd Year',
      bio: u.bio || '',
      department: u.department || 'Computer Science',
      email: u.email || '',
      registerNumber: u.registerNumber || u.rollNo || 'STU001',
      status: u.status || 'ACTIVE'
    }
  } catch (err) {
    console.error('Failed to load student profile', err)
  } finally {
    loading.value = false
  }
}

async function handleSaveProfile() {
  if (!userProfile.value?.id) return
  saving.value = true
  try {
    const updated = await updateUser(userProfile.value.id, {
      fullName: form.value.fullName,
      phone: form.value.phone,
      year: form.value.year,
      bio: form.value.bio
    })
    userProfile.value = { ...userProfile.value, ...updated }

    const currentStored = JSON.parse(localStorage.getItem('user') || '{}')
    localStorage.setItem('user', JSON.stringify({ ...currentStored, ...updated }))

    alert('Profile updated successfully!')
  } catch (err) {
    alert('Failed to update profile.')
    console.error(err)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <StudentLayout>
    <section class="profile-page">
      <!-- Page Header -->
      <div class="page-header mb-4">
        <div>
          <h2 class="fw-bold text-dark m-0">My Profile</h2>
          <p class="text-secondary m-0 mt-1">View and update your student account information.</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading profile details...</p>
      </div>

      <!-- Profile Container -->
      <div v-else class="row g-4">
        
        <!-- Left Column: User Card & Avatar -->
        <div class="col-12 col-lg-4">
          <div class="card p-4 border-0 rounded-4 shadow-sm text-center">
            <div class="profile-avatar mx-auto mb-3">
              {{ (form.fullName || 'S').charAt(0).toUpperCase() }}
            </div>

            <h4 class="fw-bold text-dark mb-1">{{ form.fullName || 'Student' }}</h4>
            <span class="badge bg-primary px-3 py-1 rounded-pill mb-2">
              {{ form.year }} · {{ form.department }}
            </span>
            <p class="text-secondary text-sm mb-3">{{ form.email }}</p>

            <div class="border-top pt-3 text-start">
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted text-sm">Account Status</span>
                <span class="badge bg-success">{{ form.status }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted text-sm">Department</span>
                <strong class="text-dark text-sm">{{ form.department }}</strong>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted text-sm">Roll / Register No</span>
                <strong class="text-dark text-sm">{{ form.registerNumber }}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Edit Profile Form -->
        <div class="col-12 col-lg-8">
          <div class="card p-4 border-0 rounded-4 shadow-sm">
            <h5 class="fw-bold mb-4 text-dark">
              <i class="bi bi-person-gear text-primary me-2"></i>Edit Profile Details
            </h5>

            <form @submit.prevent="handleSaveProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label font-semibold">Full Name</label>
                  <input v-model="form.fullName" type="text" class="form-control rounded-3" required />
                </div>

                <div class="col-md-6">
                  <label class="form-label font-semibold">Email Address (Read-only)</label>
                  <input v-model="form.email" type="email" class="form-control rounded-3 bg-light" disabled />
                </div>

                <div class="col-md-6">
                  <label class="form-label font-semibold">Phone Number</label>
                  <input v-model="form.phone" type="text" class="form-control rounded-3" placeholder="+91 XXXXX XXXXX" />
                </div>

                <div class="col-md-6">
                  <label class="form-label font-semibold">Year of Study</label>
                  <select v-model="form.year" class="form-select rounded-3">
                    <option value="1st Year">1st Year</option>
                    <option value="2nd Year">2nd Year</option>
                    <option value="3rd Year">3rd Year</option>
                    <option value="4th Year">4th Year</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label font-semibold">Department (Read-only)</label>
                  <input v-model="form.department" type="text" class="form-control rounded-3 bg-light" disabled />
                </div>

                <div class="col-md-6">
                  <label class="form-label font-semibold">Roll Number (Read-only)</label>
                  <input v-model="form.registerNumber" type="text" class="form-control rounded-3 bg-light" disabled />
                </div>

                <div class="col-12">
                  <label class="form-label font-semibold">Bio / Student Notes</label>
                  <textarea v-model="form.bio" class="form-control rounded-3" rows="4" placeholder="Tell us about yourself..."></textarea>
                </div>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
                <button type="submit" class="btn btn-success rounded-pill px-4" :disabled="saving">
                  <i class="bi bi-check-circle me-1"></i>
                  {{ saving ? 'Saving Changes...' : 'Save Profile Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>

      </div>
    </section>
  </StudentLayout>
</template>

<style scoped>
.profile-page {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  font-size: 2.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
