<script setup>
import AdminLayout from '@/layouts/AdminLayout.vue'
import ClubSearch from '@/components/admin/club/ClubSearch.vue'
import ClubGrid from '@/components/admin/club/ClubGrid.vue'
import AddClubModal from '@/components/admin/club/AddClubModal.vue'
import EditClubModal from '@/components/admin/club/EditClubModal.vue'
import DeleteClubModal from '@/components/admin/club/DeleteClubModal.vue'
import ClubDetailsModal from '@/components/admin/club/ClubDetailsModal.vue'

import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { getClubs } from '@/api/clubs'

const clubList = ref([])
const selectedStatus = ref("ALL")
const search = ref('')
const selectedClub = ref(null)
const showAddModal = ref(false)
const showDetailsModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const currentPage = ref(1)
const itemsPerPage = 3
const editingPage = ref(false)
const pageInput = ref(1)
const pageInputRef = ref(null)

const fetchClubs = async () => {
  try {
    clubList.value = await getClubs()
  } catch (error) {
    console.error('Failed to fetch clubs:', error)
  }
}

onMounted(() => {
  fetchClubs()
})

const filteredClubs = computed(() => {
    let filtered = clubList.value

    if (search.value.trim()) {
        const keyword = search.value.toLowerCase()

        filtered = filtered.filter(club =>
            club.name.toLowerCase().includes(keyword) ||
            club.category.toLowerCase().includes(keyword)
        )
    }

    if (selectedStatus.value !== "ALL") {
        filtered = filtered.filter(
            club => club.status === selectedStatus.value
        )
    }

    return filtered
})

const openAddModal = () => {
  showAddModal.value = true
}

const closeAddModal = () => {
  showAddModal.value = false
}

const addClub = (club) => {
  clubList.value = [club, ...clubList.value]
  closeAddModal()
}

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

const openDeleteModal = (club) => {
  if (!club) return
  selectedClub.value = { ...club }
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  selectedClub.value = null
}

const handleEditFromDetails = () => {
  const clubToEdit = selectedClub.value
  closeDetailsModal()
  openEditModal(clubToEdit)
}

const handleDeleteFromDetails = () => {
  const clubToDelete = selectedClub.value
  closeDetailsModal()
  openDeleteModal(clubToDelete)
}

const confirmDelete = () => {
  if (!selectedClub.value) return
  clubList.value = clubList.value.filter((club) => club.id !== selectedClub.value.id)
  closeDeleteModal()
}

const activeCount = computed(() =>
    clubList.value.filter(c => c.status === "ACTIVE").length
)

const legacyCount = computed(() =>
    clubList.value.filter(c => c.status === "INACTIVE").length
)

watch([search, selectedStatus], () => {
    currentPage.value = 1
})

const paginatedClubs = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage

    return filteredClubs.value.slice(
        start,
        start + itemsPerPage
    )
})

const totalPages = computed(() =>
    Math.max(
        1,
        Math.ceil(filteredClubs.value.length / itemsPerPage)
    )
)

function previousPage() {
    if (currentPage.value > 1) {
        currentPage.value--
    }
}

function nextPage() {
    if (currentPage.value < totalPages.value) {
        currentPage.value++
    }
}

function savePage() {
    let page = Number(pageInput.value)
    if (isNaN(page)) {
        page = currentPage.value
    }

    page = Math.max(1, Math.min(page, totalPages.value))
    currentPage.value = page
    editingPage.value = false
}

function cancelEditingPage() {
    editingPage.value = false
}

async function startEditingPage() {
    editingPage.value = true
    pageInput.value = currentPage.value
    await nextTick()
    pageInputRef.value.focus()
    pageInputRef.value.select()
}
</script>

<template>
  <AdminLayout>
    <section class="admin-clubs-page">
      <div class="page-top">
        <div>
          <p class="eyebrow">Admin Dashboard</p>
          <h2 class="fw-bold mb-2">Clubs Management</h2>
          <p class="subtitle">
            Manage student clubs, discover new interests, and keep club details up to date from one place.
          </p>
        </div>
        <button type="button" class="add-btn" @click="openAddModal">+ Add Club</button>
      </div>

      <div class="toolbar">
        <div class="search-wrap">
          <ClubSearch v-model="search" />
        </div>
        <div class="status-tabs">
          <button
            :class="{ active: selectedStatus === 'ALL' }"
            @click="selectedStatus = 'ALL'"
          >
            All
            <span>{{ clubList.length }}</span>
          </button>

          <button
            :class="{ active: selectedStatus === 'ACTIVE' }"
            @click="selectedStatus = 'ACTIVE'"
          >
            Live
            <span>{{ activeCount }}</span>
          </button>

          <button
            :class="{ active: selectedStatus === 'INACTIVE' }"
            @click="selectedStatus = 'INACTIVE'"
          >
            Legacy
            <span>{{ legacyCount }}</span>
          </button>
        </div>
      </div>

      <ClubGrid :clubs="paginatedClubs" @view="openDetailsModal"/>

      <div v-if="filteredClubs.length" class="pagination-bar">
        <button @click="previousPage" :disabled="currentPage === 1">← Previous</button>
        <div class="page-indicator" @dblclick="startEditingPage">
          <span v-if="!editingPage">{{ currentPage }}</span>
          <input
              v-else
              ref="pageInputRef"
              v-model.number="pageInput"
              class="page-input"
              type="number"
              min="1"
              :max="totalPages"
              @keyup.enter="savePage"
              @keyup.esc="cancelEditingPage"
              @blur="savePage"
          />
        </div>
        <button @click="nextPage":disabled="currentPage === totalPages">Next →</button>
      </div>

      <div v-if="filteredClubs.length === 0" class="empty-state">
        <h3>No clubs matched your search.</h3>
        <p>Try searching with another keyword.</p>
      </div>

      <AddClubModal v-if="showAddModal" @close="closeAddModal" @submit="addClub" />
      <ClubDetailsModal
        v-if="showDetailsModal && selectedClub"
        :club="selectedClub"
        @close="closeDetailsModal"
        @visit="closeDetailsModal"
        @edit="handleEditFromDetails"
        @delete="handleDeleteFromDetails"
      />
      <EditClubModal v-if="showEditModal && selectedClub" :club="selectedClub" @close="closeEditModal" @submit="saveEdit" />
      <DeleteClubModal v-if="showDeleteModal && selectedClub" :club="selectedClub" @close="closeDeleteModal" @confirm="confirmDelete" />
    </section>
  </AdminLayout>
</template>

<style scoped>
.admin-clubs-page {
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

.toolbar{
    display:grid;
    grid-template-columns:minmax(0, 1fr) auto;
    align-items:center;
    gap:24px;
    margin-bottom:32px;
}

.search-wrap{
    width:100%;
    max-width:850px;
}

.status-tabs{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:6px;
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:18px;
    justify-self:end;
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

.status-tabs button{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    min-width:88px;
    height:50px;
    border:none;
    border-radius:14px;
    background:transparent;
    font-weight:600;
    color:#475569;
    cursor:pointer;
    transition:.2s;
}

.status-tabs button span{
    width:28px;
    height:28px;
    display:grid;
    place-items:center;
    border-radius:50%;
    background:#eef2ff;
    color:#2563eb;
    font-size:13px;
    font-weight:700;
}

.status-tabs button.active{
    background:#2563eb;
    color:white;
}

.status-tabs button.active span{
    background:white;
    color:#2563eb;
}

.pagination-bar{
    display:flex;
    justify-content:center;
    align-items:center;
    gap:18px;
    margin-top:40px;
}

.pagination-bar button{
    border:none;
    background:#fff;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:12px 18px;
    font-weight:600;
    cursor:pointer;
    transition:.2s;
}

.pagination-bar button:hover:not(:disabled){
    background:#2563eb;
    color:#fff;
}

.pagination-bar button:disabled{
    opacity:.5;
    cursor:not-allowed;
}

.page-indicator{
    width:56px;
    height:56px;
    display:grid;
    place-items:center;
    border-radius:16px;
    background:#2563eb;
    color:white;
    font-size:18px;
    font-weight:700;
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

@media (max-width:900px){
    .toolbar{
        grid-template-columns:1fr;
    }

    .search-wrap{
        max-width:100%;
    }

    .status-tabs{
        justify-self:start;
    }
}

.page-indicator{
    width:64px;
    height:56px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:16px;
    background:#eff6ff;
    color:#2563eb;
    font-size:20px;
    font-weight:700;
    cursor:pointer;
    transition:.2s;
}

.page-indicator:hover{
    background:#dbeafe;
}

.page-input{
    width:100%;
    height:100%;
    border:none;
    outline:none;
    background:transparent;
    color:#2563eb;
    text-align:center;
    font-size:20px;
    font-weight:700;
}

.page-input::-webkit-outer-spin-button,
.page-input::-webkit-inner-spin-button{
    -webkit-appearance:none;
    margin:0;
}

.page-input{
    appearance:textfield;
    -moz-appearance:textfield;
}
</style>