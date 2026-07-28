<script setup>
import { ref, computed, onMounted } from 'vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import ClubSearch from '@/components/admin/club/ClubSearch.vue'
import ClubGrid from '@/components/admin/club/ClubGrid.vue'
import ClubDetailsModal from '@/components/admin/club/ClubDetailsModal.vue'
import { getStudentClubs, getMyClubs } from '@/api/clubs'

const search = ref('')
const clubList = ref([])
const myClubs = ref([])
const selectedClub = ref(null)
const showDetailsModal = ref(false)

onMounted(async () => {
  console.log("Clubs page mounted")

  try {
    console.log("Fetching clubs...")

    clubList.value = await getStudentClubs()

    console.log("Fetched all clubs")

    myClubs.value = await getMyClubs()

    console.log("Fetched my clubs")

  } catch (error) {
    console.error(error)
  }
})

const myClubNames = computed(() =>
  myClubs.value.map(club => club.name)
)

const filteredMyClubs = computed(() => {
  const query = search.value.trim().toLowerCase()

  return myClubs.value.filter(club => {
    return (
      !query ||
      club.name.toLowerCase().includes(query) ||
      club.category.toLowerCase().includes(query)
    )
  })
})

const filteredAllClubs = computed(() => {
    const query = search.value.trim().toLowerCase()

    return clubList.value.filter(club => {
        const matchesSearch =
            !query ||
            club.name.toLowerCase().includes(query) ||
            club.category.toLowerCase().includes(query)

        return matchesSearch
    })
})

const openDetailsModal = (club) => {
  selectedClub.value = { ...club }
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedClub.value = null
}


</script>

<template>
  <StudentLayout>
    <section class="student-clubs-page">
      <div class="page-top">
        <div>
          <p class="eyebrow">Student Dashboard</p>
          <h2 class="fw-bold mb-2">Clubs Management</h2>
          <p class="subtitle">
            Browse clubs, manage your memberships, and discover communities across campus.
          </p>
        </div>
      </div>

      <div class="toolbar">
        <div class="search-wrap">
          <ClubSearch v-model="search" />
        </div>
      </div>

      <div class="grid-panel">
        <h3 class="section-title">My Clubs</h3>
        <ClubGrid
          :clubs="filteredMyClubs"
          :myClubNames="myClubNames"
          :isAdmin="false"
          :isFaculty="false"
          section="my-clubs"
          @view="openDetailsModal"
        />

        <h3 class="section-title">All Clubs</h3>
        <ClubGrid
          :clubs="filteredAllClubs"
          :myClubNames="myClubNames"
          :isAdmin="false"
          :isFaculty="false"
          section="all-clubs"
          @view="openDetailsModal"
        />
      </div>

      <div v-if="filteredMyClubs.length === 0 && filteredAllClubs.length === 0" class="empty-state">
        <h3>No clubs matched your search.</h3>
        <p>Try searching with another keyword.</p>
      </div>
      
      <ClubDetailsModal
          v-if="showDetailsModal"
          :club="selectedClub"
          :isMember="myClubNames.includes(selectedClub?.name)"
          @close="closeDetailsModal"
      />

    </section>
  </StudentLayout>
</template>

<style scoped>
.student-clubs-page {
  width: 100%;
}

.page-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
  padding: 24px 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.eyebrow {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.subtitle {
  margin: 0;
  color: #64748b;
  max-width: 720px;
  line-height: 1.7;
}

.add-btn {
  border: none;
  background: #2563eb;
  color: #ffffff;
  border-radius: 12px;
  padding: 12px 18px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.2);
  cursor: pointer;
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.search-wrap {
  flex: 1;
}

.grid-panel {
  background: #ffffff;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.empty-state {
  text-align: center;
  padding: 70px 20px;
  color: #6b7280;
}

.empty-state h3 {
  color: #1f2937;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .page-top {
    flex-direction: column;
    align-items: stretch;
  }

  .add-btn {
    width: 100%;
  }
}
</style>