<template>
  <article class="club-card" @click="$emit('view', club)">

    <div class="club-header">

      <div class="club-image">
        {{ club.emoji }}
      </div>

      <span class="category">
        {{ club.category }}
      </span>

    </div>

    <div class="club-content">

      <h3>{{ club.name }}</h3>

      <p class="description">
        {{ club.description }}
      </p>

    </div>

    <div class="club-footer">

      <span class="members">
        👥 {{ club.members }}
        {{ club.members === 1 ? 'Member' : 'Members' }}
      </span>

      <div class="footer-actions">
        <button
          type="button"
          class="view-btn"
          @click.stop="$emit('view', club)"
        >
          View Details
        </button>
      </div>

    </div>

  </article>
</template>

<script setup>

defineProps({
  club: {
    type: Object,
    required: true
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['view'])

</script>

<style scoped>

.club-card{

    background:#fff;

    border:1px solid #edf2f7;

    border-radius:18px;

    padding:24px;

    display:flex;

    flex-direction:column;

    justify-content:space-between;

    gap:20px;

    min-height:330px;

    transition:all .28s ease;

    box-shadow:0 8px 24px rgba(15,23,42,.06);

}

.club-card:hover{

    transform:translateY(-6px);

    border-color:#2563eb;

    box-shadow:0 18px 40px rgba(37,99,235,.12);

}

.club-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

}

.club-image{

    width:72px;

    height:72px;

    border-radius:50%;

    display:flex;

    justify-content:center;

    align-items:center;

    background:#eef4ff;

    font-size:38px;

}

.category{

    background:#eef4ff;

    color:#2563eb;

    padding:6px 12px;

    border-radius:999px;

    font-size:13px;

    font-weight:600;

}

.club-content h3{

    margin:0 0 12px;

    color:#1f2937;

    font-size:1.35rem;

    font-weight:700;

}

.description{

    margin:0;

    color:#6b7280;

    line-height:1.7;

    min-height:72px;

}

.club-footer{

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:16px;

}

.members{

    color:#64748b;

    font-size:14px;

    font-weight:500;

}

.view-btn{

    border:none;

    border-radius:10px;

    background:#2563eb;

    color:#fff;

    padding:10px 18px;

    font-weight:600;

    cursor:pointer;

    transition:all .2s ease;

}

.view-btn:hover{

    background:#1d4ed8;

}

@media (max-width:576px){

.club-footer{

    flex-direction:column;

    align-items:stretch;

}

.view-btn{

    width:100%;

}

}

</style>