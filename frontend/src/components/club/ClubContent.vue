<script setup>
import ClubPanel from "./ClubPanel.vue";
import EditClubModal from "@/components/admin/club/EditClubModal.vue";
import CreateEventModal from "@/components/admin/events/CreateEventModal.vue";
import { useRouter } from "vue-router";
import { ref, computed, onMounted } from "vue";
import { getClub, getClubEvents, getClubMembers, updateClubMemberStatus } from "@/services/clubService";
import { updateClub, updateFacultyClub } from "@/api/clubs";

const router = useRouter()

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
    console.log("TODO profile page", member)
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
    }
    catch (err) {
        console.error(err)
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
    } catch (err) {
        console.error('Failed to update club', err);
        alert('Failed to update club.');
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
});
</script>

<template>
  <div class="club-page">

    <!-- Details Panel -->
    <ClubPanel title="Club Details" class="details-panel">
      <template #header-actions v-if="userRole === 'ADMIN' || userRole === 'FACULTY'">
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
                <span class="stat-label">Members</span>
                <span class="stat-count">{{ club?.activeMembers || members.length || 0 }}</span>
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
              <div v-for="coord in facultyCoordinators" :key="coord.id || coord.name" class="faculty-chip">
                <span class="material-symbols-rounded chip-icon">person</span>
                <span class="chip-name">{{ coord.name }}</span>
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

        <ClubPanel title="Members">

            <div
                v-if="members.length"
                class="member-list"
            >

                <div class="member-card" v-for="member in members" :key="member.id">

                    <div class="member-avatar">
                        {{ member.name.charAt(0) }}
                    </div>

                    <div class="member-info">
                        <div class="member-name">{{ member.name }}</div>
                        <div class="member-role">{{ member.membershipRole }}</div>
                    </div>

                    <div
                        v-if="props.userRole === 'ADMIN' || props.userRole === 'FACULTY'"
                        class="member-actions"
                    >
                        <button
                        class="profile-btn"
                        @click="viewProfile(member)"
                        >
                        View Profile
                        </button>

                        <button
                        :class="member.membershipStatus === 'ACTIVE'
                            ? 'deactivate-btn'
                            : 'activate-btn'"
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

                <h3>No members yet</h3>

                <p>
                    Nobody has joined this club yet.
                </p>
            </div>

        </ClubPanel>

        <ClubPanel title="Events">
            <template #header-actions v-if="userRole === 'ADMIN' || userRole === 'FACULTY'">
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

.edit-club-btn .material-symbols-rounded,
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