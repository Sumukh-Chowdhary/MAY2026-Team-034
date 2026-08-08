<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudentLayout from '@/layouts/StudentLayout.vue'
import { getUser, updateUser } from '@/api/users'
import { getMyClubs } from '@/api/student'

const router = useRouter()

const userProfile = ref(null)
const myClubs = ref([])
const loading = ref(true)
const saving = ref(false)
const showEditModal = ref(false)
const saveSuccess = ref(false)

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

const editForm = ref({
  fullName: '',
  phone: '',
  year: '',
  bio: ''
})

const avatarInitials = computed(() => {
  const name = form.value.fullName || 'S'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const avatarColor = computed(() => {
  const colors = [
    'linear-gradient(135deg, #2563eb, #1d4ed8)',
    'linear-gradient(135deg, #7c3aed, #6d28d9)',
    'linear-gradient(135deg, #059669, #047857)',
    'linear-gradient(135deg, #dc2626, #b91c1c)',
    'linear-gradient(135deg, #d97706, #b45309)'
  ]
  const idx = (form.value.fullName?.charCodeAt(0) || 0) % colors.length
  return colors[idx]
})

const activeClubs = computed(() => myClubs.value.filter(c => c.status === 'ACTIVE' || !c.status))
const organizerRoles = computed(() => myClubs.value.filter(c =>
  c.membershipRole && c.membershipRole.toUpperCase() !== 'MEMBER'
))

const categoryColors = {
  TECHNICAL: { bg: '#eff6ff', text: '#2563eb', border: '#bfdbfe' },
  CULTURAL: { bg: '#fdf4ff', text: '#7c3aed', border: '#e9d5ff' },
  SPORTS: { bg: '#f0fdf4', text: '#059669', border: '#bbf7d0' },
  ARTS: { bg: '#fff7ed', text: '#ea580c', border: '#fed7aa' },
  DEFAULT: { bg: '#f8fafc', text: '#475569', border: '#e2e8f0' }
}

function getCategoryStyle(category) {
  const c = categoryColors[(category || '').toUpperCase()] || categoryColors.DEFAULT
  return `background:${c.bg}; color:${c.text}; border:1px solid ${c.border};`
}

function getRoleBadgeStyle(role) {
  if (!role || role.toUpperCase() === 'MEMBER') {
    return 'background:#f0fdf4; color:#059669; border:1px solid #bbf7d0;'
  }
  return 'background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe;'
}

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

    const clubs = await getMyClubs().catch(() => [])
    myClubs.value = Array.isArray(clubs) ? clubs : []

    form.value = {
      fullName: u.fullName || u.name || '',
      phone: u.phone || u.phoneNumber || '',
      year: u.year || u.yearOfStudy || '3rd Year',
      bio: u.bio || '',
      department: u.department || 'Computer Science',
      email: u.email || '',
      registerNumber: u.registerNumber || u.rollNo || '',
      status: u.status || 'ACTIVE'
    }
  } catch (err) {
    console.error('Failed to load student profile', err)
  } finally {
    loading.value = false
  }
}

function openEditModal() {
  editForm.value = {
    fullName: form.value.fullName,
    phone: form.value.phone,
    year: form.value.year,
    bio: form.value.bio
  }
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
}

async function handleSaveProfile() {
  if (!userProfile.value?.id) return
  saving.value = true
  try {
    const updated = await updateUser(userProfile.value.id, {
      fullName: editForm.value.fullName,
      phone: editForm.value.phone,
      year: editForm.value.year,
      bio: editForm.value.bio
    })
    userProfile.value = { ...userProfile.value, ...updated }
    form.value = {
      ...form.value,
      fullName: editForm.value.fullName,
      phone: editForm.value.phone,
      year: editForm.value.year,
      bio: editForm.value.bio
    }

    const currentStored = JSON.parse(localStorage.getItem('user') || '{}')
    localStorage.setItem('user', JSON.stringify({ ...currentStored, ...updated }))

    showEditModal.value = false
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <StudentLayout>
    <section class="profile-page">

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading profile...</p>
      </div>

      <template v-else>

        <!-- Success Toast -->
        <div v-if="saveSuccess" class="toast-success">
          <i class="bi bi-check-circle-fill me-2"></i> Profile updated successfully!
        </div>

        <!-- ── HERO SECTION ── -->
        <div class="profile-hero">
          <div class="hero-bg-pattern"></div>

          <div class="hero-content">
            <div class="hero-left">
              <div class="avatar-ring">
                <div class="avatar" :style="{ background: avatarColor }">{{ avatarInitials }}</div>
              </div>
              <div class="hero-info">
                <div class="hero-name-row">
                  <h1 class="hero-name">{{ form.fullName || 'Student' }}</h1>
                  <span class="status-badge" :class="form.status === 'ACTIVE' ? 'active' : 'inactive'">
                    {{ form.status }}
                  </span>
                </div>
                <p class="hero-sub">{{ form.year }} · {{ form.department }}</p>
                <p class="hero-email"><i class="bi bi-envelope-fill me-1"></i>{{ form.email }}</p>
                <p v-if="form.registerNumber" class="hero-roll">
                  <i class="bi bi-person-badge-fill me-1"></i>{{ form.registerNumber }}
                </p>
              </div>
            </div>

            <div class="hero-right">
              <button class="edit-btn" @click="openEditModal">
                <i class="bi bi-pencil-square me-2"></i>Edit Profile
              </button>
            </div>
          </div>

          <!-- Stats Row -->
          <div class="hero-stats">
            <div class="stat-pill">
              <span class="stat-num">{{ myClubs.length }}</span>
              <span class="stat-lbl">Clubs Joined</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-pill">
              <span class="stat-num">{{ activeClubs.length }}</span>
              <span class="stat-lbl">Active Memberships</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-pill">
              <span class="stat-num">{{ organizerRoles.length }}</span>
              <span class="stat-lbl">Special Roles</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-pill">
              <span class="stat-num">{{ form.year || '—' }}</span>
              <span class="stat-lbl">Year of Study</span>
            </div>
          </div>
        </div>

        <!-- ── MAIN CONTENT GRID ── -->
        <div class="content-grid">

          <!-- LEFT: Info Card -->
          <div class="info-col">
            <div class="info-card">
              <h5 class="card-section-title">
                <i class="bi bi-person-lines-fill me-2 text-primary"></i>Profile Details
              </h5>
              <div class="info-list">
                <div class="info-row">
                  <span class="info-label">Full Name</span>
                  <span class="info-value">{{ form.fullName || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Email</span>
                  <span class="info-value">{{ form.email || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Phone</span>
                  <span class="info-value">{{ form.phone || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Department</span>
                  <span class="info-value">{{ form.department || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Year of Study</span>
                  <span class="info-value">{{ form.year || '—' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">Register No.</span>
                  <span class="info-value">{{ form.registerNumber || '—' }}</span>
                </div>
              </div>

              <div v-if="form.bio" class="bio-section">
                <h6 class="bio-title"><i class="bi bi-chat-quote-fill me-2 text-primary"></i>Bio</h6>
                <p class="bio-text">{{ form.bio }}</p>
              </div>
              <div v-else class="bio-empty" @click="openEditModal">
                <i class="bi bi-plus-circle me-2"></i>Add a bio
              </div>
            </div>
          </div>

          <!-- RIGHT: Club Memberships -->
          <div class="clubs-col">
            <div class="clubs-card">
              <div class="clubs-card-header">
                <h5 class="card-section-title">
                  <i class="bi bi-collection-fill me-2 text-primary"></i>Club Memberships
                </h5>
                <RouterLink to="/student/clubs" class="browse-link">
                  Browse Clubs <i class="bi bi-arrow-right ms-1"></i>
                </RouterLink>
              </div>

              <div v-if="myClubs.length === 0" class="clubs-empty">
                <div class="empty-icon">🎭</div>
                <p>You haven't joined any clubs yet.</p>
                <RouterLink to="/student/clubs" class="join-btn">Explore Clubs</RouterLink>
              </div>

              <div v-else class="clubs-grid">
                <div
                  v-for="club in myClubs"
                  :key="club.id"
                  class="club-card"
                >
                  <div class="club-card-top">
                    <div class="club-logo-wrap">
                      <img v-if="club.logo" :src="club.logo" :alt="club.name" class="club-logo-img" />
                      <div v-else class="club-logo-fallback">{{ (club.name || 'C')[0].toUpperCase() }}</div>
                    </div>
                    <div class="club-meta">
                      <h6 class="club-name">{{ club.name || club.clubName }}</h6>
                      <span
                        class="club-category-badge"
                        :style="getCategoryStyle(club.category)"
                      >{{ club.category || 'GENERAL' }}</span>
                    </div>
                  </div>

                  <div class="club-card-body">
                    <p class="club-desc">{{ (club.description || '').slice(0, 80) }}{{ (club.description || '').length > 80 ? '…' : '' }}</p>
                  </div>

                  <div class="club-card-footer">
                    <div class="club-footer-left">
                      <span class="role-badge" :style="getRoleBadgeStyle(club.membershipRole)">
                        {{ club.membershipRole || 'MEMBER' }}
                      </span>
                      <span class="member-count">
                        <i class="bi bi-people-fill me-1"></i>{{ club.activeMembers || club.totalMembers || 0 }}
                      </span>
                    </div>
                    <RouterLink :to="`/student/clubs/${club.id}`" class="club-view-btn">
                      View <i class="bi bi-arrow-right ms-1"></i>
                    </RouterLink>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </template>

      <!-- ── EDIT PROFILE MODAL ── -->
      <Teleport to="body">
        <Transition name="modal">
          <div v-if="showEditModal" class="modal-backdrop" @click.self="closeEditModal">
            <div class="modal-box">
              <div class="modal-header">
                <div class="modal-title-wrap">
                  <div class="modal-avatar" :style="{ background: avatarColor }">{{ avatarInitials }}</div>
                  <div>
                    <h4 class="modal-title">Edit Profile</h4>
                    <p class="modal-subtitle">Update your personal details</p>
                  </div>
                </div>
                <button class="modal-close" @click="closeEditModal">
                  <i class="bi bi-x-lg"></i>
                </button>
              </div>

              <div class="modal-body">
                <div class="modal-grid">
                  <div class="modal-field">
                    <label class="field-label">Full Name</label>
                    <input v-model="editForm.fullName" type="text" class="field-input" placeholder="Your full name" />
                  </div>
                  <div class="modal-field">
                    <label class="field-label">Phone Number</label>
                    <input v-model="editForm.phone" type="text" class="field-input" placeholder="+91 XXXXX XXXXX" />
                  </div>
                  <div class="modal-field">
                    <label class="field-label">Year of Study</label>
                    <select v-model="editForm.year" class="field-select">
                      <option value="1st Year">1st Year</option>
                      <option value="2nd Year">2nd Year</option>
                      <option value="3rd Year">3rd Year</option>
                      <option value="4th Year">4th Year</option>
                    </select>
                  </div>
                  <div class="modal-field readonly-field">
                    <label class="field-label">Email <span class="readonly-tag">Read-only</span></label>
                    <input :value="form.email" type="email" class="field-input" disabled />
                  </div>
                  <div class="modal-field readonly-field">
                    <label class="field-label">Department <span class="readonly-tag">Read-only</span></label>
                    <input :value="form.department" type="text" class="field-input" disabled />
                  </div>
                  <div class="modal-field readonly-field">
                    <label class="field-label">Register No. <span class="readonly-tag">Read-only</span></label>
                    <input :value="form.registerNumber" type="text" class="field-input" disabled />
                  </div>
                  <div class="modal-field full-width">
                    <label class="field-label">Bio</label>
                    <textarea v-model="editForm.bio" class="field-textarea" rows="3" placeholder="Tell us about yourself..."></textarea>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button class="modal-cancel-btn" @click="closeEditModal">Cancel</button>
                <button class="modal-save-btn" :disabled="saving" @click="handleSaveProfile">
                  <span v-if="saving"><i class="bi bi-arrow-repeat spin me-2"></i>Saving...</span>
                  <span v-else><i class="bi bi-check-circle me-2"></i>Save Changes</span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

    </section>
  </StudentLayout>
</template>

<style scoped>
.profile-page {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding-bottom: 40px;
}

/* ── Loading ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
  color: #64748b;
}
.spinner {
  width: 40px; height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ── Toast ── */
.toast-success {
  position: fixed;
  top: 24px; right: 24px; z-index: 9999;
  background: #052e16;
  color: #86efac;
  border: 1px solid #166534;
  padding: 14px 22px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  animation: slideInRight 0.3s ease;
}

/* ── Hero ── */
.profile-hero {
  position: relative;
  background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #2563eb 100%);
  border-radius: 24px;
  padding: 40px 40px 0;
  margin-bottom: 28px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(37, 99, 235, 0.25);
}
.hero-bg-pattern {
  position: absolute; inset: 0; z-index: 0;
  background-image: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 50%),
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.05) 0%, transparent 40%);
}
.hero-content {
  position: relative; z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  flex-wrap: wrap;
}
.hero-left {
  display: flex;
  align-items: center;
  gap: 24px;
}
.avatar-ring {
  padding: 3px;
  background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.1));
  border-radius: 50%;
  flex-shrink: 0;
}
.avatar {
  width: 90px; height: 90px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; font-weight: 800;
  color: white;
  border: 3px solid rgba(255,255,255,0.2);
}
.hero-info { color: white; }
.hero-name-row {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  margin-bottom: 6px;
}
.hero-name {
  font-size: 1.75rem; font-weight: 800;
  margin: 0; color: white;
}
.status-badge {
  font-size: 0.7rem; font-weight: 700;
  padding: 3px 10px; border-radius: 20px;
  letter-spacing: 0.5px; text-transform: uppercase;
}
.status-badge.active { background: rgba(74,222,128,0.2); color: #86efac; border: 1px solid rgba(74,222,128,0.3); }
.status-badge.inactive { background: rgba(248,113,113,0.2); color: #fca5a5; border: 1px solid rgba(248,113,113,0.3); }
.hero-sub { margin: 0 0 4px; color: rgba(255,255,255,0.8); font-size: 0.95rem; }
.hero-email, .hero-roll { margin: 0 0 3px; color: rgba(255,255,255,0.65); font-size: 0.85rem; }
.hero-right { display: flex; align-items: flex-start; padding-top: 4px; }
.edit-btn {
  padding: 10px 22px;
  background: rgba(255,255,255,0.15);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 12px;
  font-weight: 600; font-size: 0.9rem;
  cursor: pointer; transition: all 0.2s;
  backdrop-filter: blur(8px);
}
.edit-btn:hover {
  background: rgba(255,255,255,0.25);
  transform: translateY(-1px);
}

/* Stats Row */
.hero-stats {
  position: relative; z-index: 1;
  display: flex; align-items: center;
  gap: 0;
  margin-top: 32px;
  background: rgba(255,255,255,0.1);
  border-radius: 16px 16px 0 0;
  padding: 16px 24px;
  backdrop-filter: blur(8px);
}
.stat-pill {
  display: flex; flex-direction: column; align-items: center;
  flex: 1; gap: 2px;
}
.stat-num {
  font-size: 1.5rem; font-weight: 800; color: white;
  line-height: 1;
}
.stat-lbl {
  font-size: 0.72rem; color: rgba(255,255,255,0.65);
  font-weight: 500; text-align: center;
}
.stat-divider {
  width: 1px; height: 36px;
  background: rgba(255,255,255,0.2);
  margin: 0 8px;
}

/* ── Content Grid ── */
.content-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 24px;
}
@media (max-width: 900px) {
  .content-grid { grid-template-columns: 1fr; }
}

/* Info Card */
.info-card, .clubs-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(15,23,42,0.06);
}
.card-section-title {
  font-size: 1rem; font-weight: 700; color: #1e293b;
  margin: 0 0 20px;
}
.info-list { display: flex; flex-direction: column; gap: 0; }
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.info-row:last-child { border-bottom: none; }
.info-label { font-size: 0.82rem; color: #94a3b8; font-weight: 500; }
.info-value { font-size: 0.9rem; color: #1e293b; font-weight: 600; text-align: right; max-width: 60%; word-break: break-all; }

.bio-section { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
.bio-title { font-size: 0.85rem; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.bio-text { font-size: 0.88rem; color: #64748b; line-height: 1.6; margin: 0; }
.bio-empty {
  margin-top: 20px; padding: 14px;
  border: 2px dashed #e2e8f0; border-radius: 12px;
  text-align: center; color: #94a3b8; font-size: 0.85rem;
  cursor: pointer; transition: all 0.2s;
}
.bio-empty:hover { border-color: #2563eb; color: #2563eb; }

/* Clubs Card */
.clubs-card-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.browse-link {
  font-size: 0.82rem; color: #2563eb; font-weight: 600;
  text-decoration: none; transition: opacity 0.2s;
}
.browse-link:hover { opacity: 0.75; }

.clubs-empty {
  text-align: center; padding: 40px 20px;
  color: #94a3b8;
}
.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.clubs-empty p { margin-bottom: 16px; }
.join-btn {
  display: inline-block; padding: 10px 24px;
  background: #2563eb; color: white; border-radius: 12px;
  font-weight: 600; font-size: 0.88rem; text-decoration: none;
  transition: all 0.2s;
}
.join-btn:hover { background: #1d4ed8; }

.clubs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.club-card {
  border: 1px solid #e2e8f0; border-radius: 16px;
  padding: 18px; display: flex; flex-direction: column; gap: 12px;
  transition: all 0.2s; background: #fafbfc;
}
.club-card:hover {
  border-color: #2563eb;
  box-shadow: 0 6px 24px rgba(37,99,235,0.1);
  transform: translateY(-2px);
}
.club-card-top { display: flex; gap: 12px; align-items: flex-start; }
.club-logo-wrap { flex-shrink: 0; }
.club-logo-img {
  width: 44px; height: 44px; border-radius: 10px; object-fit: cover;
}
.club-logo-fallback {
  width: 44px; height: 44px; border-radius: 10px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: white; font-weight: 800; font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
}
.club-name { font-size: 0.92rem; font-weight: 700; color: #1e293b; margin: 0 0 6px; }
.club-category-badge {
  font-size: 0.68rem; font-weight: 700; padding: 2px 8px; border-radius: 8px;
  text-transform: uppercase; letter-spacing: 0.4px;
}
.club-card-body { flex: 1; }
.club-desc { font-size: 0.8rem; color: #64748b; line-height: 1.5; margin: 0; }
.club-card-footer {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 10px; border-top: 1px solid #e2e8f0;
}
.club-footer-left { display: flex; align-items: center; gap: 8px; }
.role-badge {
  font-size: 0.68rem; font-weight: 700; padding: 3px 8px; border-radius: 8px;
  text-transform: uppercase;
}
.member-count { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }
.club-view-btn {
  font-size: 0.78rem; font-weight: 700; color: #2563eb;
  text-decoration: none; transition: opacity 0.2s;
}
.club-view-btn:hover { opacity: 0.7; }

/* ── Modal ── */
.modal-backdrop {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(15, 23, 42, 0.6);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
  backdrop-filter: blur(4px);
}
.modal-box {
  background: white; border-radius: 24px;
  width: 100%; max-width: 620px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 24px 80px rgba(0,0,0,0.25);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24px 28px; border-bottom: 1px solid #f1f5f9;
}
.modal-title-wrap { display: flex; align-items: center; gap: 16px; }
.modal-avatar {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 800; font-size: 1.1rem;
  flex-shrink: 0;
}
.modal-title { font-size: 1.1rem; font-weight: 800; color: #1e293b; margin: 0 0 2px; }
.modal-subtitle { font-size: 0.8rem; color: #94a3b8; margin: 0; }
.modal-close {
  width: 36px; height: 36px; border-radius: 10px;
  background: #f8fafc; border: 1px solid #e2e8f0;
  color: #64748b; font-size: 0.9rem;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s; flex-shrink: 0;
}
.modal-close:hover { background: #fee2e2; color: #dc2626; border-color: #fecaca; }
.modal-body { padding: 24px 28px; }
.modal-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
.modal-field { display: flex; flex-direction: column; gap: 6px; }
.modal-field.full-width { grid-column: 1 / -1; }
.field-label {
  font-size: 0.8rem; font-weight: 700; color: #475569;
  display: flex; align-items: center; gap: 8px;
}
.readonly-tag {
  font-size: 0.65rem; font-weight: 600; background: #f1f5f9;
  color: #94a3b8; border-radius: 4px; padding: 1px 6px;
}
.field-input, .field-select, .field-textarea {
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.88rem; color: #1e293b;
  background: white; outline: none; transition: border 0.2s;
  font-family: inherit; resize: vertical;
}
.field-input:focus, .field-select:focus, .field-textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.08);
}
.field-input:disabled, .field-select:disabled {
  background: #f8fafc; color: #94a3b8; cursor: not-allowed;
}
.readonly-field .field-input { cursor: not-allowed; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 12px;
  padding: 20px 28px; border-top: 1px solid #f1f5f9;
}
.modal-cancel-btn {
  padding: 10px 24px; border-radius: 12px;
  background: #f8fafc; border: 1.5px solid #e2e8f0;
  color: #475569; font-weight: 600; font-size: 0.88rem;
  cursor: pointer; transition: all 0.2s;
}
.modal-cancel-btn:hover { background: #f1f5f9; }
.modal-save-btn {
  padding: 10px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white; border: none;
  font-weight: 700; font-size: 0.88rem;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(37,99,235,0.3);
}
.modal-save-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(37,99,235,0.4); }
.modal-save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* Modal transition */
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-box, .modal-leave-to .modal-box { transform: scale(0.95) translateY(10px); }

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes slideInRight {
  from { transform: translateX(100px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.spin { animation: spin 0.8s linear infinite; display: inline-block; }

/* Responsive */
@media (max-width: 768px) {
  .profile-hero { padding: 24px 20px 0; }
  .hero-left { flex-direction: column; align-items: flex-start; }
  .hero-content { flex-direction: column; }
  .hero-stats { gap: 0; padding: 14px 16px; }
  .modal-grid { grid-template-columns: 1fr; }
  .clubs-grid { grid-template-columns: 1fr; }
}
</style>
