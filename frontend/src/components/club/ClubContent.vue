<script setup>
import ClubPanel from "./ClubPanel.vue";
import EditClubModal from "@/components/admin/club/EditClubModal.vue";
import CreateEventModal from "@/components/admin/events/CreateEventModal.vue";
import UserAvatar from "@/components/profile/UserAvatar.vue";
import UserProfileModal from "@/components/common/UserProfileModal.vue";
import { useRouter } from "vue-router";
import { ref, computed, onMounted } from "vue";
import { updateClub, updateFacultyClub } from "@/api/clubs";
import { getClub, getClubMembers, getClubEvents, updateClubMemberStatus } from "@/services/clubService";
import { getCurrentUser } from "@/services/authService";
import { getMySupervisedClubs } from "@/api/faculty";
import { useToast } from "@/composables/useToast";

const { showToast } = useToast();

const router = useRouter()
const currentUser = getCurrentUser()
const supervisedClubIds = ref([])

const showProfileModal = ref(false)
const selectedUserId = ref(null)

const props = defineProps({
    clubId: Number,
    userRole: {
        type: String,
        default: "GUEST"
    }
});

const club = ref(null);
const events = ref([]);
const members = ref([]);
const showLegacyMembers = ref(true);

const activeMembers = computed(() => {
    return (members.value || []).filter(m => !m.isLegacy && m.userStatus !== 'LEGACY' && m.membershipStatus === 'ACTIVE')
});

const legacyMembers = computed(() => {
    return (members.value || []).filter(m => m.isLegacy || m.userStatus === 'LEGACY' || m.membershipStatus === 'LEGACY' || m.membershipStatus === 'GRADUATED')
});

const showEditClubModal = ref(false);
const showCreateEventModal = ref(false);

function openEditModal() {
    showEditClubModal.value = true;
}

const facultyCoordinators = computed(() => {
    if (!club.value?.faculty) return [];
    if (Array.isArray(club.value.faculty)) return club.value.faculty;
    return [club.value.faculty];
});

function isImageUrl(url) {
    if (!url) return false;
    return url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/') || url.startsWith('data:');
}

function viewProfile(member) {
    const targetId = member?.userId || member?.id || member?.studentId || member?.facultyId
    if (targetId) {
        selectedUserId.value = targetId
        showProfileModal.value = true
    } else {
        showToast('User profile ID not available', 'warning')
    }
}

function viewRequests() {
    const prefix = props.userRole === "ADMIN" ? "/admin" : "/faculty"
    router.push(`${prefix}/requests`)
}

function viewEvent(event) {
    const prefix =
        props.userRole === "GUEST"
            ? ""
            : `/${props.userRole.toLowerCase()}`

    router.push(`${prefix}/events/${event.id}`)
}

async function toggleMembership(member) {
    try {
        await updateClubMemberStatus(
            props.clubId,
            member.id,
            member.membershipStatus !== "ACTIVE"
        )

        members.value = await getClubMembers(props.clubId)
        showToast('Member status updated successfully.', 'success');
    }
    catch (err) {
        console.error(err)
        const errMsg = err?.response?.data?.error || 'Permission Denied: Only the assigned Faculty Coordinator can manage members.'
        showToast(errMsg, 'error')
    }
}

async function handleSaveEdit(clubData) {
    try {
        if (props.userRole === 'ADMIN') {
            await updateClub(clubData.id, clubData);
        } else {
            await updateFacultyClub(clubData.id, clubData);
        }
        club.value = await getClub(props.clubId);
        showEditClubModal.value = false;
        showToast('Club updated successfully.', 'success');
    } catch (err) {
        console.error('Failed to update club', err);
        const errMsg = err?.response?.data?.error || 'Permission Denied: Only the assigned Faculty Coordinator can edit this club.'
        showToast(errMsg, 'error');
    }
}

async function handleEventCreated() {
    showCreateEventModal.value = false;
    events.value = await getClubEvents(props.clubId);
}

onMounted(async () => {
    club.value = await getClub(props.clubId);
    events.value = await getClubEvents(props.clubId);
    members.value = await getClubMembers(props.clubId);

    if (props.userRole === 'FACULTY') {
        try {
            const myClubs = await getMySupervisedClubs()
            supervisedClubIds.value = (myClubs || []).map(c => Number(c.id || c.clubId))
        } catch (err) {
            console.error('Failed to load supervised clubs for permission check', err)
        }
    }
});

const canManageClub = computed(() => {
    if (props.userRole === 'ADMIN') return true
    if (props.userRole === 'FACULTY') {
        const targetClubId = Number(props.clubId)
        if (!targetClubId) return false

        const isSupervised = supervisedClubIds.value.map(Number).includes(targetClubId)
        if (isSupervised) return true

        if (currentUser) {
            const currentUserId = Number(currentUser.id || currentUser.userId)
            const currentUserEmail = (currentUser.email || '').toLowerCase()
            const currentUserName = (currentUser.name || currentUser.username || '').toLowerCase()

            const isMatchedInCoordinators = facultyCoordinators.value.some(coord => {
                if (!coord) return false
                const coordId = Number(coord.id || coord.userId || coord.facultyId)
                if (coordId && currentUserId && coordId === currentUserId) return true
                if (coord.email && currentUserEmail && coord.email.toLowerCase() === currentUserEmail) return true
                if (coord.name && currentUserName && coord.name.toLowerCase() === currentUserName) return true
                return false
            })

            if (isMatchedInCoordinators) return true
        }

        return false
    }
    return false
})
</script>

<template>
  <div class="club-page">
    <!-- Details Panel -->
    <ClubPanel title="Club Details" class="details-panel">
      <template #header-actions v-if="canManageClub">
        <button class="view-requests-btn me-2" @click="viewRequests">
          <span class="material-symbols-rounded">pending_actions</span>
          View Requests
        </button>
        <button class="edit-club-btn" @click="openEditModal">
          <span class="material-symbols-rounded">edit</span>
          Edit Club
        </button>
      </template>

      <div class="hero-container">
        <!-- Left Side -->
        <div class="hero-left">
          <div class="hero-title-row">
            <h1>{{ club?.name }}</h1>
            <span class="category-badge" v-if="club?.category">{{ club?.category }}</span>
          </div>

          <p class="description" v-if="club?.description">
            {{ club?.description }}
          </p>

          <!-- Statistics Cards Grid -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon-wrapper members-icon-bg">
                <span class="material-symbols-rounded">groups</span>
              </div>
              <div class="stat-info">
                <span class="stat-label">Active Members</span>
                <span class="stat-count">{{ activeMembers.length }}</span>
                <span v-if="legacyMembers.length" class="text-xs text-muted mt-1">({{ legacyMembers.length }} Legacy)</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon-wrapper events-icon-bg">
                <span class="material-symbols-rounded">calendar_month</span>
              </div>
              <div class="stat-info">
                <span class="stat-label">Events</span>
                <span class="stat-count">{{ events.length }}</span>
              </div>
            </div>

            <div class="stat-card">
              <div class="stat-icon-wrapper faculty-icon-bg">
                <span class="material-symbols-rounded">school</span>
              </div>
              <div class="stat-info">
                <span class="stat-label">Faculty Coordinators</span>
                <span class="stat-count">{{ facultyCoordinators.length }}</span>
              </div>
            </div>
          </div>

          <!-- Faculty Coordinators Highlight Box -->
          <div class="faculty-highlight-box">
            <div class="faculty-box-header">
              <span class="material-symbols-rounded text-primary">supervisor_account</span>
              <h4>Faculty Coordinators</h4>
            </div>
            
            <div v-if="facultyCoordinators.length" class="faculty-list-chips">
              <div 
                v-for="coord in facultyCoordinators" 
                :key="coord.id || coord.name" 
                class="faculty-chip cursor-pointer"
                @click="viewProfile(coord)"
                style="cursor: pointer;"
              >
                <UserAvatar size="list" :user="coord" />
                <span class="chip-name fw-semibold text-primary-hover ms-1">{{ coord.name }}</span>
              </div>
            </div>
            <div v-else class="empty-faculty-text">
              No faculty coordinator assigned
            </div>
          </div>
        </div>

        <!-- Right Side: Logo -->
        <div class="hero-right">
          <div class="logo-wrapper">
            <img 
              v-if="isImageUrl(club?.logo)" 
              :src="club.logo" 
              :alt="club?.name" 
              class="club-logo-img" 
            />
            <div v-else-if="club?.logo" class="club-logo-icon-placeholder">
              <span class="material-symbols-rounded">{{ club.logo }}</span>
            </div>
            <div v-else class="club-logo-initial-placeholder">
              <span>{{ club?.name?.charAt(0) || 'C' }}</span>
            </div>
          </div>
        </div>
      </div>
    </ClubPanel>

    <!-- Bottom Grid -->
    <div class="club-grid">

        <!-- ── Active Members Section ── -->
        <ClubPanel title="Active Members">
            <template #header-actions>
                <span class="badge bg-primary-subtle text-primary border px-2 py-1 text-xs fw-semibold">{{ activeMembers.length }} Active</span>
            </template>

            <div
                v-if="activeMembers.length"
                class="member-list"
            >
                <div class="member-card d-flex align-items-center justify-content-between p-2 mb-2 border rounded" v-for="member in activeMembers" :key="member.id">
                    <div class="d-flex align-items-center gap-2 cursor-pointer" @click="viewProfile(member)" style="cursor: pointer;">
                      <UserAvatar size="list" :user="member" />
                      <div class="member-info">
                          <div class="member-name text-primary-hover fw-bold">{{ member.name }}</div>
                          <div class="member-role text-muted text-xs">
                            <span v-if="member.registerNumber || member.rollNumber" class="fw-semibold text-dark me-1">{{ member.registerNumber || member.rollNumber }} •</span>
                            <span>{{ member.membershipRole }}</span>
                          </div>
                      </div>
                    </div>

                    <div class="member-actions d-flex gap-2 align-items-center">
                        <button
                          class="profile-btn btn btn-sm btn-outline-secondary"
                          @click="viewProfile(member)"
                        >
                          View Profile
                        </button>

                        <button
                          v-if="canManageClub"
                          :class="member.membershipStatus === 'ACTIVE'
                              ? 'deactivate-btn btn btn-sm btn-outline-danger'
                              : 'activate-btn btn btn-sm btn-outline-success'"
                          @click="toggleMembership(member)"
                        >
                          {{ member.membershipStatus === 'ACTIVE'
                              ? 'Deactivate'
                              : 'Activate' }}
                        </button>
                    </div>
                </div>
            </div>

            <div
                v-else
                class="empty-state"
            >
                <span class="material-symbols-rounded empty-icon members-icon">
                    groups
                </span>
                <h3>No active members</h3>
                <p>There are currently no active students in this club.</p>
            </div>
        </ClubPanel>

        <!-- ── Legacy Members Section ── -->
        <ClubPanel title="Legacy Members">
            <template #header-actions>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-warning-subtle text-warning border border-warning px-2 py-1 text-xs fw-semibold">{{ legacyMembers.length }} Legacy / Alumni</span>
                    <button class="btn btn-sm btn-outline-secondary py-0 px-2 text-xs" @click="showLegacyMembers = !showLegacyMembers">
                        <i class="bi" :class="showLegacyMembers ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                        {{ showLegacyMembers ? 'Collapse' : 'Expand' }}
                    </button>
                </div>
            </template>

            <div v-if="showLegacyMembers">
                <div
                    v-if="legacyMembers.length"
                    class="member-list"
                >
                    <div class="member-card legacy-member-card d-flex align-items-center justify-content-between p-2 mb-2 border border-warning-subtle rounded bg-light-subtle" v-for="member in legacyMembers" :key="member.id">
                        <div class="d-flex align-items-center gap-2 cursor-pointer" @click="viewProfile(member)" style="cursor: pointer;">
                          <UserAvatar size="list" :user="member" />
                          <div class="member-info">
                              <div class="member-name fw-bold d-flex align-items-center gap-1">
                                  {{ member.name }}
                                  <span class="badge bg-warning-subtle text-warning border border-warning text-xs">Graduated</span>
                              </div>
                              <div class="member-details text-xs text-muted">
                                  <span v-if="member.registerNumber || member.rollNumber" class="fw-semibold text-dark me-1">{{ member.registerNumber || member.rollNumber }}</span>
                                  <span>• Branch: {{ member.branchCode || member.department || '—' }}</span>
                                  <span v-if="member.batchYear || member.graduationYear"> • Batch: {{ member.batchYear || '—' }} (Grad: {{ member.graduationYear || '—' }})</span>
                              </div>
                              <div class="member-role text-xs text-muted mt-1">
                                  Former Role: <strong class="text-secondary">{{ member.membershipRole || 'Member' }}</strong>
                                  <span v-if="member.joinedAt"> • Joined: {{ new Date(member.joinedAt).toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) }}</span>
                              </div>
                          </div>
                        </div>

                        <div class="member-actions">
                            <button
                              class="profile-btn btn btn-sm btn-outline-primary"
                              @click="viewProfile(member)"
                            >
                              <i class="bi bi-person-lines-fill me-1"></i> View Profile
                            </button>
                            <!-- NO ACTIVE MANAGEMENT CONTROLS FOR LEGACY MEMBERS -->
                        </div>
                    </div>
                </div>

                <div
                    v-else
                    class="empty-state py-3"
                >
                    <i class="bi bi-mortarboard fs-2 text-muted mb-1"></i>
                    <h5 class="text-secondary mb-0">No legacy members</h5>
                    <p class="text-muted text-xs">Graduated/passed-out club members will appear here as historical records.</p>
                </div>
            </div>
        </ClubPanel>

        <ClubPanel title="Events">
            <template #header-actions v-if="canManageClub">
                <button class="create-event-btn" @click="showCreateEventModal = true">
                    <span class="material-symbols-rounded">add</span>
                    Create Event
                </button>
            </template>

            <div
                v-if="events.length"
                class="event-list"
            >

                <div
                    v-for="event in events"
                    :key="event.id"
                    class="event-card"
                >
                    <div class="event-info">
                        <div class="event-name">{{ event.name }}</div>
                        <div class="event-date">{{ event.startDate }}</div>
                    </div>

                    <button
                        v-if="userRole !== 'GUEST'"
                        class="event-details-btn"
                        @click="viewEvent(event)"
                    >
                        View Details
                    </button>
                </div>

            </div>

            <div
                v-else
                class="empty-state"
            >
                <span class="material-symbols-rounded empty-icon events-icon">
                    event_busy
                </span>

                <h3>No events yet</h3>

                <p>
                    This club hasn't scheduled any events yet.
                </p>
            </div>

        </ClubPanel>

    </div>

    <!-- Modals -->
    <EditClubModal
      v-if="showEditClubModal && club"
      :club="club"
      :canEditFaculty="userRole === 'ADMIN'"
      @close="showEditClubModal = false"
      @submit="handleSaveEdit"
    />

    <CreateEventModal
      v-if="showCreateEventModal"
      :fixedClubId="props.clubId"
      @close="showCreateEventModal = false"
      @created="handleEventCreated"
    />

    <UserProfileModal 
      :show="showProfileModal"
      :userId="selectedUserId"
      @close="showProfileModal = false"
    />

  </div>
</template>

<style scoped>

.club-page {
  max-width: 1300px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

.details-panel :deep(.panel-body) {
  min-height: auto;
}

/* Header Action Buttons */
.view-requests-btn,
.edit-club-btn,
.create-event-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-club-btn {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
}

.edit-club-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.view-requests-btn {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
}

.view-requests-btn:hover {
  background: #fde68a;
  color: #92400e;
}

.edit-club-btn .material-symbols-rounded,
.view-requests-btn .material-symbols-rounded,
.create-event-btn .material-symbols-rounded {
  font-size: 1.1rem;
}

.create-event-btn {
  background: #10b981;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.create-event-btn:hover {
  background: #059669;
}

/* Hero Section Layout */
.hero-container {
  display: grid;
  grid-template-columns: 1fr 160px;
  gap: 2rem;
  align-items: start;
  padding: 0.5rem 0;
}

.hero-left {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-title-row h1 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.category-badge {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  background: #eef2ff;
  color: #2563eb;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.description {
  margin: 0;
  color: #475569;
  font-size: 1rem;
  line-height: 1.6;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 0.25rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  background: #ffffff;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
  border-color: #cbd5e1;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrapper .material-symbols-rounded {
  font-size: 24px;
}

.members-icon-bg {
  background: #eff6ff;
  color: #2563eb;
}

.events-icon-bg {
  background: #fff7ed;
  color: #ea580c;
}

.faculty-icon-bg {
  background: #f0fdf4;
  color: #16a34a;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-count {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

/* Faculty Highlight Box */
.faculty-highlight-box {
  background: linear-gradient(135deg, #f8fafc, #eff6ff);
  border: 1px solid #dbeafe;
  border-radius: 14px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.faculty-box-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.faculty-box-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
}

.faculty-list-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.faculty-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #ffffff;
  border: 1px solid #bfdbfe;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.06);
}

.chip-icon {
  font-size: 1.1rem;
  color: #2563eb;
}

.chip-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1e293b;
}

.empty-faculty-text {
  font-size: 0.9rem;
  color: #64748b;
  font-style: italic;
}

/* Right Side Logo Styling */
.hero-right {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.logo-wrapper {
  width: 160px;
  height: 160px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
  border: 4px solid #ffffff;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.club-logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
}

.club-logo-icon-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #eef2ff, #dbeafe);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
}

.club-logo-icon-placeholder .material-symbols-rounded {
  font-size: 80px;
}

.club-logo-initial-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 4rem;
  font-weight: 800;
}

/* Bottom Grid Layout */
.club-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.event-list,
.member-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-height: 360px;
    overflow-y: auto;
    padding-right: 0.35rem;
    scroll-behavior: smooth;
}

.event-card,
.member-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    min-height: 90px;
    border: 1px solid #dbeafe;
    border-radius: 12px;
    background: white;
    transition: all 0.2s ease;
}

.member-card {
    gap: 1rem;
}

.member-card:hover,
.event-card:hover {
    background: #f8fafc;
}

.event-name,
.member-name {
    font-weight: 600;
    color: #1f2937;
}

.event-date,
.member-role {
    font-size: 0.9rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

.member-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #2563eb;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.member-info {
    display: flex;
    flex-direction: column;
    flex: 1;
}

.member-actions {
    display: flex;
    gap: 0.6rem;
    margin-left: auto;
    align-items: center;
}

.profile-btn,
.deactivate-btn,
.activate-btn,
.event-details-btn {
    padding: 0.45rem 0.9rem;
    min-width: 110px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.profile-btn,
.event-details-btn {
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #3b82f6;
}

.profile-btn:hover,
.event-details-btn:hover {
    background: #dbeafe;
}

.deactivate-btn {
    background: #fee2e2;
    color: #dc2626;
    border: 1px solid #e27373;
}

.deactivate-btn:hover {
    background: #fecaca;
}

.activate-btn {
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #548365;
}

.activate-btn:hover {
    background: #bbf7d0;
}

.empty-state {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #6b7280;
}

.empty-icon {
    font-size: 48px;
    color: #9ca3af;
    margin-bottom: 0.75rem;
}

.empty-state h3 {
    margin: 0;
    color: #374151;
    font-size: 1.1rem;
}

.empty-state p {
    margin-top: 0.5rem;
    font-size: 0.95rem;
}

.members-icon {
    color: #3b82f6;
}

.events-icon {
    color: #f59e0b;
}

.member-list::-webkit-scrollbar,
.event-list::-webkit-scrollbar {
    width: 8px;
}

.member-list::-webkit-scrollbar-track,
.event-list::-webkit-scrollbar-track {
    background: #f3f4f6;
    border-radius: 8px;
}

.member-list::-webkit-scrollbar-thumb,
.event-list::-webkit-scrollbar-thumb {
    background: #2563eb;
    border-radius: 8px;
}

.member-list::-webkit-scrollbar-thumb:hover,
.event-list::-webkit-scrollbar-thumb:hover {
    background: #1d4ed8;
}

@media (max-width: 900px) {
  .hero-container {
    grid-template-columns: 1fr;
  }

  .hero-right {
    order: -1;
    justify-content: flex-start;
    margin-bottom: 0.5rem;
  }

  .club-grid {
    grid-template-columns: 1fr;
  }
}

</style>