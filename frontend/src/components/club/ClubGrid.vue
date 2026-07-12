<template>
  <section class="club-grid">

    <ClubCard
      v-for="club in clubs"
      :key="club.id"
      :club="club"
    />

  </section>
</template>

<script setup>

import ClubCard from './ClubCard.vue'

defineProps({
  clubs: {
    type: Array,
    required: true,
    default: () => []
  }
})

</script>

<style scoped>

.club-grid{

    max-width:1240px;

    margin:0 auto;

    padding:0 12px;

    display:grid;

    grid-template-columns:repeat(auto-fit,minmax(300px,1fr));

    gap:28px;

}

@media (max-width:768px){

.club-grid{

    grid-template-columns:1fr;

}

}

</style>