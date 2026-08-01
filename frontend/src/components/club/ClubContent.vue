<script setup>
import ClubPanel from "./ClubPanel.vue";
import { ref, onMounted } from "vue";
import { getClub, getClubEvents, getClubMembers } from "@/services/clubService";

const props = defineProps({
    clubId: Number
});

const club = ref(null);
const events = ref([]);
const members = ref([]);

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
      <div class="details-placeholder">
        <h1>{{ club?.name }}</h1>

        <p class="category">
          {{ club?.category }}
        </p>

        <p class="description">
          {{ club?.description }}
        </p>

        <div class="club-meta">
          <div>
            <strong>Faculty Coordinator:</strong>
            {{ club?.faculty[0]?.name || "N/A" }}
          </div>

          <div>
            <strong>Members:</strong>
            {{ club?.activeMembers || 0 }}
          </div>

          <div>
            <strong>Events:</strong>
            {{ events.length }}
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

                <div
                    v-for="member in members"
                    :key="member.id"
                    class="member-card"
                >

                    <div class="member-avatar">
                        {{ member.name.charAt(0) }}
                    </div>

                    <div class="member-info">

                        <div class="member-name">
                            {{ member.name }}
                        </div>

                        <div class="member-role">
                            {{ member.membershipRole }}
                        </div>

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

            <div
                v-if="events.length"
                class="event-list"
            >

                <div
                    v-for="event in events"
                    :key="event.id"
                    class="event-card"
                >

                    <div class="event-name">
                        {{ event.name }}
                    </div>

                    <div class="event-date">
                        {{ event.startDate }}
                    </div>

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

  </div>
</template>

<style scoped>

.club-page {
  max-width: 1300px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

.club-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.details-placeholder {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.details-placeholder h1 {
  margin: 0;
  font-size: 2rem;
  color: #1f2937;
}

.details-panel {
    width: 100%;
}

.category {
  display: inline-block;
  width: fit-content;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  background: #eef2ff;
  color: #4338ca;
  font-weight: 600;
}

.description {
  color: #4b5563;
  line-height: 1.6;
}

.club-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-top: 0.5rem;
}

.event-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    max-height: 360px;
    overflow-y: auto;

    padding-right: 0.35rem;
}

.event-card {
    border: 1px solid #3b82f6;
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    background: #ffffff;
    transition: all 0.2s ease;
}

.event-card:hover {
    background: #eff6ff;
    transform: translateY(-1px);
}

.event-name {
    font-weight: 600;
    color: #1f2937;
}

.event-date {
    font-size: 0.9rem;
    color: #6b7280;
    margin-top: 0.25rem;
}

@media (max-width: 900px) {

  .club-grid {
    grid-template-columns: 1fr;
  }

}

.member-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    max-height: 360px;
    overflow-y: auto;

    padding-right: 0.35rem;
}

.member-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;

    border: 1px solid #e5e7eb;
    border-radius: 10px;

    padding: 0.75rem;

    transition: all 0.2s ease;
}

.member-card:hover {
    background: #f8fafc;
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
}

.member-name {
    font-weight: 600;
    color: #1f2937;
}

.member-role {
    font-size: 0.9rem;
    color: #6b7280;
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

.member-card.organizer .member-avatar {
    background: #f59e0b;
}

.member-card.coordinator .member-avatar {
    background: #10b981;
}

.member-list,
.event-list {
    scroll-behavior: smooth;
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

</style>