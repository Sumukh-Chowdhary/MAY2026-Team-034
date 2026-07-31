<script setup>
import { ref, computed } from 'vue'
import FacultyLayout from '@/layouts/FacultyLayout.vue'
import ClubSearch from '@/components/admin/club/ClubSearch.vue'
import ClubGrid from '@/components/admin/club/ClubGrid.vue'
import EditClubModal from '@/components/admin/club/EditClubModal.vue'
// import DeleteClubModal from '@/components/admin/club/DeleteClubModal.vue'
import ClubDetailsModal from '@/components/admin/club/ClubDetailsModal.vue'
import { clubs } from '@/data/clubs'

const search = ref('')
const clubList = ref([...clubs])
const selectedClub = ref(null)
const showDetailsModal = ref(false)
const showEditModal = ref(false)
// const showDeleteModal = ref(false)

const filteredClubs = computed(() => {
  const query = search.value.trim().toLowerCase()

  if (!query) return clubList.value

  return clubList.value.filter((club) =>
    club.name.toLowerCase().includes(query) ||
    club.category.toLowerCase().includes(query)
  )
})

const openDetailsModal = (club) => {
  selectedClub.value = { ...club }
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedClub.value = null
}

const openEditModal = (club) => {
  if (!club) return
  selectedClub.value = { ...club }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  selectedClub.value = null
}

const saveEdit = (updatedClub) => {
  clubList.value = clubList.value.map((club) => (club.id === updatedClub.id ? updatedClub : club))
  closeEditModal()
}

/*
const openDeleteModal = (club) => {
  if (!club) return
  selectedClub.value = { ...club }
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  selectedClub.value = null
}
*/

const handleEditFromDetails = () => {
  const clubToEdit = selectedClub.value
  closeDetailsModal()
  openEditModal(clubToEdit)
}


/*
const handleDeleteFromDetails = () => {
  const clubToDelete = selectedClub.value
  closeDetailsModal()
  openDeleteModal(clubToDelete)
}
*/


/*
const confirmDelete = () => {
  if (!selectedClub.value) return
  clubList.value = clubList.value.filter((club) => club.id !== selectedClub.value.id)
  closeDeleteModal()
}
*/
</script>

<template>
  <FacultyLayout>
    <section class="faculty-clubs-page">
      <div class="page-top">
        <div>
          <p class="eyebrow">Faculty Dashboard</p>
          <h2 class="fw-bold mb-2">Clubs Management</h2>
          <p class="subtitle">
            Manage your student club, its members, and club activities from one place.
          </p>
        </div>
      </div>

      <div class="toolbar">
        <div class="search-wrap">
          <ClubSearch v-model="search" />
        </div>
      </div>

      <div class="grid-panel">
        <ClubGrid
          :clubs="filteredClubs"
          :isFaculty="true"
          @view="openDetailsModal"
        />
      </div>

      <div v-if="filteredClubs.length === 0" class="empty-state">
        <h3>No clubs matched your search.</h3>
        <p>Try searching with another keyword.</p>
      </div>

      <AddClubModal v-if="showAddModal" @close="closeAddModal" @submit="addClub" />
      <ClubDetailsModal
        v-if="showDetailsModal && selectedClub"
        :club="selectedClub"
        :isAdmin="false"
        :isFaculty="true"
        @close="closeDetailsModal"
        @visit="closeDetailsModal"
        @edit="handleEditFromDetails"
   <!-- @delete="handleDeleteFromDetails" -->
      />
      <EditClubModal v-if="showEditModal && selectedClub" :club="selectedClub" @close="closeEditModal" @submit="saveEdit" />
    <!--  <DeleteClubModal v-if="showDeleteModal && selectedClub" :club="selectedClub" @close="closeDeleteModal" @confirm="confirmDelete" /> -->
    </section>
  </FacultyLayout>
</template>

<style scoped>
.faculty-clubs-page {
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