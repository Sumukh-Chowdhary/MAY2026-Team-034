<template>
  <article class="club-card" @click="$emit('view', club)">
    <div class="club-header">
      <div class="club-image">
        <span class="material-symbols-rounded">
            {{ club.logo }}
        </span>
      </div>
      <span class="category">{{ club.category }}</span>
    </div>

    <div class="club-content">
      <h3>{{ club.name }}</h3>
      <p class="description">{{ club.description }}</p>
    </div>

    <div class="club-stats">
      <span
        class="status-chip"
        :class="club.status === 'ACTIVE' ? 'live' : 'inactive'"
      >
        <span class="status-badge"></span>
        {{ club.status === 'ACTIVE' ? 'Live Club' : 'Legacy' }}
      </span>
      <span class="member-chip">
        {{ club.activeMembers }} Active Members
      </span>
      <span class="member-chip">
        {{ club.totalMembers }} Members
      </span>
    </div>

    <div class="footer-actions">
      <button type="button" class="view-btn"@click.stop="$emit('view', club)">
        View Details
      </button>

      <button v-if="section === 'all-clubs' && !isMember" type="button" class="join-btn" @click.stop="$emit('join', club)">
        Join
      </button>
    </div>
  </article>
</template>

<script setup>
defineProps({
  club: {
    type: Object,
    required: true
  },
  section: {
    type: String,
    default: ""
  },
  isMember: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'view',
  'join',
  'leave'
])
</script>

<style scoped>
.club-stats{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin-top:8px;
}

.member-chip{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:6px 12px;
    border-radius:999px;
    background:#eef4ff;
    color:#2563eb;
    font-size:13px;
    font-weight:600;
}

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
    width:64px;
    height:64px;
    border-radius:16px;
    background:#eef4ff;
    display:flex;
    align-items:center;
    justify-content:center;
}

.club-image .material-symbols-rounded{
    font-size:34px;
    color:#2563eb;
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

.status-chip{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:6px 12px;
    border-radius:999px;
    font-size:13px;
    font-weight:600;
}

.status-chip.live{
    background:#dcfce7;
    color:#15803d;
}

.status-chip.inactive{
    background:#fef9c3;
    color:#a16207;
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

.join-btn{
    background:#16a34a;
    color:white;
    border:none;
    border-radius:10px;
    padding:10px 18px;
    font-weight:600;
    cursor:pointer;
    transition:.2s;
}

.join-btn:hover{
    background:#15803d;
}

.view-btn:hover{
    background:#1d4ed8;
}

.footer-actions{
    display:flex;
    flex-direction:column;
    gap:12px;
}

@media (max-width:576px){
.club-footer{
    flex-direction:column;
    align-items:stretch;
}

.view-btn,
.join-btn,
.leave-btn{
    width:100%;
}

.join-btn,
.leave-btn{
    border:none;
    border-radius:10px;
    color:#fff;
    padding:10px 18px;
    font-weight:600;
    cursor:pointer;
    transition:all .2s ease;
}

.join-btn{
    background:#16a34a;
}

.join-btn:hover{
    background:#15803d;
}

.leave-btn{
    background:#dc2626;
}

.leave-btn:hover{
    background:#b91c1c;
}
}
</style>