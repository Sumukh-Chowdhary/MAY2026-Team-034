<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="edit-club-title" @click.stop>
      <button type="button" class="modal-close-btn" @click.stop="emit('close')" aria-label="Close edit club">
        ×
      </button>

      <div class="modal-header">
        <div class="modal-title-block">
          <span class="category">Edit Club</span>
          <h3 id="edit-club-title">Update club details</h3>
        </div>
      </div>

      <div class="modal-body">
        <label class="field">
          <span>Club Name</span>
          <input v-model="form.name" type="text" placeholder="e.g. Robotics Club" />
        </label>

        <label class="field">
          <span>Club Icon</span>

          <button
            type="button"
            class="icon-picker-btn"
            @click="showIconPicker = true"
          >
            <span class="material-symbols-rounded icon-preview">
              {{ form.logo }}
            </span>

            <div class="icon-text">
              <strong>{{ form.logo }}</strong>
              <small>Choose another icon</small>
            </div>
          </button>
        </label>

        <IconPickerModal
            v-if="showIconPicker"
            :model-value="form.logo"
            @close="showIconPicker = false"
            @select="selectIcon"
        />

        <label class="field">
        <span>Category</span>    
        <select v-model="form.category">
          <option disabled value="">
              Select a category
          </option>

          <option>Technology</option>
          <option>Academic</option>
          <option>Arts</option>
          <option>Sports</option>
          <option>Cultural</option>
          <option>Entrepreneurship</option>
          <option>Social Service</option>
          <option>General</option>
      </select>
      </label>

        <label class="field">
          <span>Description</span>
          <textarea v-model="form.description" rows="5" maxlength="500" placeholder="Update club description"></textarea>
        </label>

        <div
            v-if="canEditFaculty"
            class="field"
        >
          <FacultyPicker
              v-model="form.facultyCoordinatorIds"
              :faculty="faculty"
          />
        </div>
      </div>

      <div class="modal-actions">
        <button type="button" class="cancel-btn" @click.stop="emit('close')">Cancel</button>
        <button type="button" class="save-btn" @click.stop="submitForm">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch, onMounted, onUnmounted } from 'vue'
import IconPickerModal from './IconPickerModal.vue'
import FacultyPicker from './FacultyPicker.vue'
import { getFacultyDetails } from '@/api/clubs'

const showIconPicker = ref(false)
const faculty = ref([])

const props = defineProps({
  club: {
    type: Object,
    required: true
  },
  canEditFaculty: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close', 'submit'])

const form = reactive({
  id:null,
  name:'',
  logo:'groups',
  category:'',
  description:'',
  facultyCoordinatorIds:[]
})

watch(
  () => props.club,
  (club) => {
    if (club) {
      form.id = club.id
      form.name = club.name
      form.logo = club.logo
      form.category = club.category
      form.description = club.description
      form.facultyCoordinatorIds = club.faculty?.map(member => member.id) || []
    }
  },
  { immediate: true }
)

const submitForm = () => {
  if (!form.name.trim()) return

  emit('submit', {
    ...form,
    name: form.name.trim(),
    description: form.description.trim()
  })

}

async function loadFaculty() {
  try {
    faculty.value = await getFacultyDetails()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  if (props.canEditFaculty) {
    loadFaculty()
  }
})

function selectIcon(icon) {
  form.logo = icon
  showIconPicker.value = false
}

onMounted(() => {
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-overlay{
    position:fixed;
    inset:0;
    background:rgba(15,23,42,.68);
    display:flex;
    justify-content:center;
    align-items:flex-start;
    padding:40px 20px;
    overflow-y:auto;
    z-index:1100;
}

.modal-card{
    position:relative;
    width:min(100%,700px);
    max-height:90vh;
    background:#fff;
    border-radius:24px;
    padding:28px;
    display:flex;
    flex-direction:column;
    gap:20px;
    overflow-y:auto;
    box-shadow:0 20px 60px rgba(15,23,42,.28);
    scrollbar-width:none;
    -ms-overflow-style:none;
}

.modal-card::-webkit-scrollbar{
    display:none;
}

.modal-close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  border: none;
  background: #f3f4f6;
  width: 38px;
  height: 38px;
  border-radius: 999px;
  font-size: 24px;
  cursor: pointer;
  color: #475569;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-title-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.modal-title-block h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.4rem;
  font-weight: 700;
}

.category {
  background: #ecfdf5;
  color: #16a34a;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.modal-body{
    display:grid;
    gap:18px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #334155;
  font-size: 0.95rem;
  font-weight: 600;
}

.field input,
.field textarea,
.field select{
    border:1px solid #dce4ee;
    border-radius:12px;
    padding:12px 14px;
    font-size:.95rem;
    color:#0f172a;
    transition:.2s;
}

.field input:focus,
.field textarea:focus,
.field select:focus{
    outline:none;
    border-color:#2563eb;
    box-shadow:0 0 0 3px rgba(37,99,235,.12);
}

.field textarea {
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

.cancel-btn,
.save-btn {
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 600;
  cursor: pointer;
}

.cancel-btn {
  background: #f3f4f6;
  color: #475569;
}

.save-btn {
  background: #2563eb;
  color: white;
}

.icon-picker-btn{
    display:flex;
    align-items:center;
    gap:16px;
    width:100%;
    padding:14px 16px;
    border:1px solid #dce4ee;
    border-radius:12px;
    background:white;
    cursor:pointer;
    transition:.2s;
}

.icon-picker-btn:hover{
    border-color:#2563eb;
    background:#f8fbff;
}

.icon-preview{
    width:52px;
    height:52px;
    border-radius:14px;
    background:#eef4ff;
    display:grid;
    place-items:center;
    color:#2563eb;
    font-size:30px;
}

.icon-text{
    display:flex;
    flex-direction:column;
    align-items:flex-start;
}

.icon-text strong{
    color:#1e293b;
}

.icon-text small{
    color:#64748b;
}

.modal-actions{
    display:flex;
    justify-content:flex-end;
    gap:12px;
    margin-top:8px;
}

.cancel-btn,
.save-btn{
    border:none;
    border-radius:12px;
    padding:12px 20px;
    font-weight:600;
    cursor:pointer;
    transition:.2s;
}

.cancel-btn{
    background:#f3f4f6;
    color:#475569;
}

.cancel-btn:hover{
    background:#e5e7eb;
}

.save-btn{
    background:#2563eb;
    color:white;
}

.save-btn:hover{
    background:#1d4ed8;
}
</style>