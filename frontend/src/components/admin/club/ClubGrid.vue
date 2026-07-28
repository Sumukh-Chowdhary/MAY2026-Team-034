<template>
  <section class="club-grid">
    <ClubCard
      v-for="club in clubs"
      :key="club.id"
      :club="club"
      :section="section"
      :isMember="myClubNames.includes(club.name)"
      @view="$emit('view', $event)"
      @join="$emit('join', $event)"
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
  },
    section: {
        type: String,
        default: ""
  },
  myClubNames: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view', 'join'])
</script>

<style scoped>
.club-grid{
    max-width:1240px;
    margin:0 auto;
    padding:0 12px;
    display:grid;
    grid-template-columns:repeat(3,minmax(360px,1fr));
    justify-content:center;
    gap:28px;
}

@media (max-width:1200px){
.club-grid{
    grid-template-columns:repeat(2,minmax(320px,1fr));
}
}

@media (max-width:768px){
.club-grid{
    grid-template-columns:1fr;
}
}

@media (max-width:768px){
.club-grid{
    grid-template-columns:1fr;
}
}
</style>