<script setup>
import { computed, ref } from 'vue'
import { clubIcons } from './clubIcons'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'groups'
  }
})

const emit = defineEmits([
  'close',
  'select'
])

const search = ref('')

const filteredCategories = computed(() => {
  if (!search.value.trim()) {
    return clubIcons
  }

  const keyword = search.value.toLowerCase()

  return clubIcons
    .map(category => ({
      ...category,
      icons: category.icons.filter(icon =>
        icon.toLowerCase().includes(keyword)
      )
    }))
    .filter(category => category.icons.length)
})

const chooseIcon = (icon) => {
  emit('select', icon)
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Select Club Icon</h3>
        <button
          class="close-btn"
          @click="emit('close')"
        >
          ×
        </button>
      </div>

      <input
        v-model="search"
        class="search-box"
        type="text"
        placeholder="Search icons..."
      >

      <div class="icon-content">
        <section
          v-for="category in filteredCategories"
          :key="category.category"
        >
          <h5>{{ category.category }}</h5>
          <div class="icon-grid">
            <button
              v-for="icon in category.icons"
              :key="icon"
              class="icon-btn"
              :class="{ selected: icon === modelValue }"
              @click="chooseIcon(icon)"
            >
              <span class="material-symbols-rounded">{{ icon }}</span>
            </button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay{
  position:fixed;
  inset:0;
  background:rgba(15,23,42,.65);
  display:flex;
  justify-content:center;
  align-items:center;
  z-index:1200;
}

.modal-card{
  width:min(760px,95vw);
  max-height:80vh;
  overflow:hidden;
  background:white;
  border-radius:20px;
  padding:24px;
  display:flex;
  flex-direction:column;
}

.modal-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:16px;
}

.close-btn{
  border:none;
  background:none;
  font-size:28px;
  cursor:pointer;
}

.search-box{
  width:100%;
  padding:12px;
  border:1px solid #dbe3ef;
  border-radius:10px;
  margin-bottom:20px;
}

.icon-content{
  overflow:auto;
}

.icon-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(60px,1fr));
  gap:12px;
  margin-bottom:24px;
}

.icon-btn{
  height:60px;
  border:1px solid #e5e7eb;
  border-radius:12px;
  background:white;
  cursor:pointer;
}

.icon-btn:hover{
  border-color:#2563eb;
}

.icon-btn.selected{
  background:#eff6ff;
  border-color:#2563eb;
}

.icon-btn .material-symbols-rounded{
  font-size:30px;
}
</style>