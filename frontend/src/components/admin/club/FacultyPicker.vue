<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  faculty: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const search = ref('')

const selectedFaculty = computed(() =>
  props.faculty.filter(member =>
    props.modelValue.includes(member.id)
  )
)

const availableFaculty = computed(() => {
  return props.faculty.filter(member => {
    const selected = props.modelValue.includes(member.id)

    const matches =
      member.name.toLowerCase().includes(search.value.toLowerCase()) ||
      member.department?.toLowerCase().includes(search.value.toLowerCase()) ||
      member.designation?.toLowerCase().includes(search.value.toLowerCase())

    return !selected && matches
  })
})

function addFaculty(id) {
  emit('update:modelValue', [...props.modelValue, id])
}

function removeFaculty(id) {
  emit(
    'update:modelValue',
    props.modelValue.filter(value => value !== id)
  )
}
</script>

<template>
  <div class="faculty-picker">
    <label class="picker-label">
      Faculty Coordinators
    </label>

    <input
      v-model="search"
      type="text"
      class="search-input"
      placeholder="Search faculty..."
    >

    <div
      v-if="selectedFaculty.length"
      class="selected-section"
    >
      <h6>Selected</h6>
      <div class="selected-list">
        <div
          v-for="member in selectedFaculty"
          :key="member.id"
          class="faculty-chip"
        >
          <div>
            <strong>{{ member.name }}</strong>
            <small>
              {{ member.designation }}
            </small>
          </div>
          <button
            type="button"
            class="remove-btn"
            @click="removeFaculty(member.id)"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div class="available-section">
      <h6>Available Faculty</h6>
      <div
        v-if="availableFaculty.length"
        class="faculty-list"
      >
        <div
          v-for="member in availableFaculty"
          :key="member.id"
          class="faculty-card"
          @click="addFaculty(member.id)"
        >
          <div>
            <strong>{{ member.name }}</strong>
            <p>{{ member.designation }}</p>
            <small>{{ member.department }}</small>
          </div>
          <button type="button" class="add-btn">Add</button>
        </div>
      </div>
      <p v-else class="empty-text">No faculty found.</p>
    </div>
  </div>
</template>

<style scoped>
.faculty-picker{
    display:flex;
    flex-direction:column;
    gap:16px;
}

.picker-label{
    font-weight:600;
    color:#1e293b;
}

.search-input{
    width:100%;
    padding:12px 14px;
    border:1px solid #d1d5db;
    border-radius:10px;
    outline:none;
    transition:.2s;
}

.search-input:focus{
    border-color:#2563eb;
}

.selected-section,
.available-section{
    display:flex;
    flex-direction:column;
    gap:12px;
}

.selected-list{
    display:flex;
    flex-direction:column;
    gap:10px;
}

.faculty-chip{
    display:flex;
    justify-content:space-between;
    align-items:center;
    background:#eff6ff;
    border:1px solid #bfdbfe;
    border-radius:10px;
    padding:10px 14px;
}

.faculty-chip strong{
    display:block;
}

.faculty-chip small{
    color:#64748b;
}

.remove-btn{
    border:none;
    background:none;
    font-size:20px;
    cursor:pointer;
    color:#dc2626;
}

.faculty-list{
    display:flex;
    flex-direction:column;
    gap:10px;
    max-height:250px;
    overflow-y:auto;
}

.faculty-card{
    display:flex;
    justify-content:space-between;
    align-items:center;
    border:1px solid #e5e7eb;
    border-radius:10px;
    padding:12px 14px;
    cursor:pointer;
    transition:.2s;
}

.faculty-card:hover{
    background:#f8fafc;
}

.faculty-card p{
    margin:2px 0;
    color:#475569;
}

.faculty-card small{
    color:#64748b;
}

.add-btn{
    background:#2563eb;
    color:white;
    border:none;
    border-radius:8px;
    padding:6px 14px;
    cursor:pointer;
}

.empty-text{
    text-align:center;
    color:#94a3b8;
}
</style>