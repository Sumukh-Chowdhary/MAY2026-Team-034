<script setup>
const model = defineModel()

const tabs = [
  {
    id: 'tickets',
    label: 'My Tickets',
    count: 3
  },
  {
    id: 'incoming',
    label: 'Incoming Requests',
    count: 2
  }
]
</script>

<template>
  <div class="toggle-container">

    <button
      v-for="tab in tabs"
      :key="tab.id"
      class="toggle-btn"
      :class="{ active: model === tab.id }"
      @click="model = tab.id"
    >
      {{ tab.label }}

      <span class="count">
        {{ tab.count }}
      </span>

    </button>

  </div>
</template>

<style scoped>
.toggle-container{
    display:inline-flex;
    width:fit-content;
    background:#fff;
    border:1px solid #dbe3ef;
    border-radius:18px;
    padding:8px;
    gap:8px;
}

.toggle-btn{
    border:none;
    background:transparent;
    padding:14px 28px;
    border-radius:14px;
    font-weight:600;
    display:flex;
    align-items:center;
    gap:12px;
    transition:.25s;
}

.toggle-btn:hover{
    background:#f4f7fb;
}

.toggle-btn.active{
    background:#2563eb;
    color:white;
}

.count{
    background:white;
    color:#2563eb;
    border-radius:999px;
    min-width:28px;
    height:28px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:.85rem;
    font-weight:700;
}

.toggle-btn:not(.active) .count{
    background:#eef2ff;
}

</style>