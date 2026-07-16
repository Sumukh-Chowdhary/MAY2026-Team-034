<script setup>
import { ref, computed } from 'vue'
import ClubSearch from '@/components/club/ClubSearch.vue'
import ClubGrid from '@/components/club/ClubGrid.vue'
import { clubs } from '@/data/clubs'

const search = ref('')
const clubList = ref(clubs)

const filteredClubs = computed(() => {
  const query = search.value.trim().toLowerCase()

  if (!query) {
    return clubList.value
  }

  return clubList.value.filter((club) =>
    club.name.toLowerCase().includes(query) ||
    club.category.toLowerCase().includes(query)
  )
})
</script>

<template>
  <div class="container py-5">
    <section class="hero">
      <h1>Explore Student Clubs</h1>
      <p>
        Explore student clubs, discover new interests, and connect with
        communities across the campus.
      </p>
    </section>

    <ClubSearch v-model="search" />
    <ClubGrid :clubs="filteredClubs" />

    <div
      v-if="filteredClubs.length === 0"
      class="empty-state"
    >
      <h3>No clubs matched your search.</h3>
      <p>Try searching with another keyword.</p>
    </div>
  </div>
</template>
<style scoped>

.hero{
    text-align:center;
    margin-bottom:55px;
}

.hero h1{
    color:#1f2937;
    font-size:3rem;
    font-weight:800;
}

.hero p{
    max-width:720px;
    margin:18px auto 0;
    color:#6b7280;
    font-size:1.1rem;
    line-height:1.8;
}

.empty-state{
    text-align:center;
    padding:70px 20px;
    color:#6b7280;
}

.empty-state h3{
    color:#1f2937;
    margin-bottom:10px;
}
</style>