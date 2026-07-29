<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { getUser, updateUser } from '@/api/users'
import '@/assets/css/UserDetails.css'

const route  = useRoute()
const router = useRouter()

// ── Load User ─────────────────────────────────────
const userId = Number(route.params.id)
const user   = ref(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    user.value = await getUser(userId)
  } catch (error) {
    console.error('Failed to load user', error)
  } finally {
    loading.value = false
  }
})

// ── Club emoji map (matches clubs.js data) ────────
const clubEmojiMap = {
  'AI Club':            '🤖',
  'Music Club':         '🎵',
  'Sports Club':        '⚽',
  'Drama Club':         '🎭',
  'Photography Club':   '📷',
  'Science Club':       '🧪',
}

function getEmoji(clubName) {
  return clubEmojiMap[clubName] || '🏛️'
}

// ── Helpers ────────────────────────────────────────
function roleBadge(role) {
  const map = { ADMIN: 'role-admin', FACULTY: 'role-faculty', STUDENT: 'role-student' }
  return map[role] || 'role-student'
}

function roleLabel(role) {
  if (!role) return ''
  return role.charAt(0) + role.slice(1).toLowerCase()
}

function initial(name) {
  return name ? name.charAt(0).toUpperCase() : '?'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}

// ── Toggle Status ──────────────────────────────────
function toggleStatus() {
  if (!user.value) return
  const newStatus = user.value.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  updateUser(user.value.id, { accountStatus: newStatus })
    .then((updated) => {
      user.value = updated
    })
    .catch(() => {
      alert('Failed to update status. Please try again.')
    })
}

// ── Edit Modal ─────────────────────────────────────
const showEditModal = ref(false)
const editForm = ref({})

function openEditModal() {
  editForm.value = { ...user.value }
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
}

function saveEdit() {
  updateUser(user.value.id, editForm.value)
    .then((updated) => {
      user.value = updated
      closeEditModal()
    })
    .catch(() => {
      alert('Failed to save profile. Please try again.')
    })
}

// ── Activity Timeline (derived) ────────────────────
const timeline = computed(() => {
  if (!user.value) return []
  const items = []

  if (user.value.joinedDate) {
    items.push({
      type: 'join',
      label: 'Joined the platform',
      date: formatDate(user.value.joinedDate),
      icon: 'bi-person-check-fill',
      dot: 'dot-join'
    })
  }

  if (user.value.clubs && user.value.clubs.length) {
    user.value.clubs.forEach(club => {
      items.push({
        type: 'club',
        label: `Joined ${club}`,
        date: 'Member',
        icon: 'bi-collection-fill',
        dot: 'dot-club'
      })
    })
  }

  return items
})
</script>

<template>
  <AdminLayout>
    <section class="user-details-page">

      <!-- ── Back ── -->
      <button class="back-btn" @click="router.push('/admin/users')">
        <i class="bi bi-arrow-left"></i> Back to Users
      </button>

      <!-- ── Not Found ── -->
      <div v-if="!user" class="not-found">
        <i class="bi bi-person-x"></i>
        <h3>User Not Found</h3>
        <p>The user you're looking for doesn't exist.</p>
      </div>

      <!-- ── Profile Content ── -->
      <template v-else>

        <!-- ── Profile Header Card ── -->
        <div class="profile-header-card">
          <div class="avatar-large" :style="{ background: user.avatarColor }">
            {{ initial(user.name) }}
          </div>

          <div class="profile-meta">
            <h2 class="profile-name">{{ user.name }}</h2>
            <p class="profile-reg">{{ user.registerNumber }}</p>
            <div class="profile-badges">
              <span class="role-badge" :class="roleBadge(user.role)">
                {{ roleLabel(user.role) }}
              </span>
              <span
                class="status-badge"
                :class="user.status === 'ACTIVE' ? 'status-active' : 'status-inactive'"
              >
                <span class="status-dot"></span>
                {{ user.status === 'ACTIVE' ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>

          <div class="header-actions">
            <button class="btn-edit" @click="openEditModal">
              <i class="bi bi-pencil-fill"></i> Edit Profile
            </button>
            <button class="btn-deactivate" @click="toggleStatus">
              <i class="bi" :class="user.status === 'ACTIVE' ? 'bi-slash-circle' : 'bi-check-circle'"></i>
              {{ user.status === 'ACTIVE' ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>

        <!-- ── Detail Grid ── -->
        <div class="detail-grid">

          <!-- Left Column -->
          <div style="display:flex; flex-direction:column; gap:20px;">

            <!-- Personal Information -->
            <div class="info-card">
              <div class="card-header">
                <i class="bi bi-person-lines-fill"></i>
                <h4>Personal Information</h4>
              </div>
              <div class="card-body">
                <div class="info-grid">
                  <div class="info-field">
                    <label>Full Name</label>
                    <div class="value">{{ user.name }}</div>
                  </div>
                  <div class="info-field">
                    <label>Register Number</label>
                    <div class="value">{{ user.registerNumber }}</div>
                  </div>
                  <div class="info-field">
                    <label>Email Address</label>
                    <a :href="'mailto:' + user.email" class="value email-val">{{ user.email }}</a>
                  </div>
                  <div class="info-field">
                    <label>Phone Number</label>
                    <div class="value phone-val">{{ user.phone || '—' }}</div>
                  </div>
                  <div class="info-field">
                    <label>Department</label>
                    <div class="value">{{ user.department || '—' }}</div>
                  </div>
                  <div class="info-field">
                    <label>Year of Study</label>
                    <div class="value">{{ user.year || '—' }}</div>
                  </div>
                  <div class="info-field">
                    <label>Role</label>
                    <div class="value">{{ roleLabel(user.role) }}</div>
                  </div>
                  <div class="info-field">
                    <label>Joined Date</label>
                    <div class="value">{{ formatDate(user.joinedDate) }}</div>
                  </div>
                </div>

                <!-- Bio -->
                <div class="bio-section" v-if="user.bio">
                  <label>About / Bio</label>
                  <p class="bio-text">{{ user.bio }}</p>
                </div>
              </div>
            </div>

          </div>

          <!-- Right Column -->
          <div style="display:flex; flex-direction:column; gap:20px;">

            <!-- Club Memberships -->
            <div class="info-card">
              <div class="card-header">
                <i class="bi bi-collection-fill"></i>
                <h4>Club Memberships</h4>
              </div>
              <div class="card-body">
                <div class="clubs-list" v-if="user.clubs && user.clubs.length">
                  <div
                    v-for="club in user.clubs"
                    :key="club"
                    class="club-item"
                  >
                    <span class="club-emoji">{{ getEmoji(club) }}</span>
                    <span class="club-name">{{ club }}</span>
                  </div>
                </div>
                <div class="no-clubs-msg" v-else>
                  <i class="bi bi-collection"></i>
                  <p>Not a member of any club yet.</p>
                </div>
              </div>
            </div>

            <!-- Activity Timeline -->
            <div class="info-card">
              <div class="card-header">
                <i class="bi bi-clock-history"></i>
                <h4>Activity Timeline</h4>
              </div>
              <div class="card-body">
                <div class="timeline" v-if="timeline.length">
                  <div
                    v-for="(item, idx) in timeline"
                    :key="idx"
                    class="timeline-item"
                  >
                    <div class="timeline-dot" :class="item.dot">
                      <i class="bi" :class="item.icon"></i>
                    </div>
                    <div class="timeline-content">
                      <p>{{ item.label }}</p>
                      <span>{{ item.date }}</span>
                    </div>
                  </div>
                </div>
                <div class="no-clubs-msg" v-else>
                  <p>No activity recorded.</p>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- ── Edit Modal ── -->
        <Teleport to="body">
          <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
            <div class="edit-modal">
              <div class="edit-modal-header">
                <h4><i class="bi bi-pencil-fill me-2" style="color:#2563eb;"></i>Edit Profile</h4>
                <button class="close-btn" @click="closeEditModal">
                  <i class="bi bi-x-lg"></i>
                </button>
              </div>

              <div class="edit-modal-body">
                <div class="form-row">
                  <div class="form-group">
                    <label>Full Name</label>
                    <input v-model="editForm.name" type="text" placeholder="Full name" />
                  </div>
                  <div class="form-group">
                    <label>Register Number</label>
                    <input v-model="editForm.registerNumber" type="text" placeholder="Register number" />
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Email</label>
                    <input v-model="editForm.email" type="email" placeholder="Email address" />
                  </div>
                  <div class="form-group">
                    <label>Phone</label>
                    <input v-model="editForm.phone" type="text" placeholder="Phone number" />
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Department</label>
                    <input v-model="editForm.department" type="text" placeholder="Department" />
                  </div>
                  <div class="form-group">
                    <label>Year of Study</label>
                    <select v-model="editForm.year">
                      <option value="">N/A</option>
                      <option>1st Year</option>
                      <option>2nd Year</option>
                      <option>3rd Year</option>
                      <option>4th Year</option>
                    </select>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Role</label>
                    <select v-model="editForm.role">
                      <option value="STUDENT">Student</option>
                      <option value="FACULTY">Faculty</option>
                      <option value="ADMIN">Admin</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Status</label>
                    <select v-model="editForm.status">
                      <option value="ACTIVE">Active</option>
                      <option value="INACTIVE">Inactive</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label>Bio / About</label>
                  <textarea v-model="editForm.bio" placeholder="Short bio about the user…"></textarea>
                </div>
              </div>

              <div class="edit-modal-footer">
                <button class="btn-cancel" @click="closeEditModal">Cancel</button>
                <button class="btn-save" @click="saveEdit">Save Changes</button>
              </div>
            </div>
          </div>
        </Teleport>

      </template>

    </section>
  </AdminLayout>
</template>
