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
          <span>Emoji</span>
          <input v-model="form.emoji" type="text" maxlength="2" placeholder="🤖" />
        </label>

        <label class="field">
          <span>Category</span>
          <input v-model="form.category" type="text" placeholder="Technology" />
        </label>

        <label class="field">
          <span>Description</span>
          <textarea v-model="form.description" rows="3" placeholder="Update club description"></textarea>
        </label>

        <label class="field">
          <span>Faculty Coordinator</span>
          <input v-model="form.facultyCoordinator" type="text" placeholder="Dr. Jane Smith" />
        </label>
      </div>

      <div class="modal-actions">
        <button type="button" class="cancel-btn" @click.stop="emit('close')">Cancel</button>
        <button type="button" class="save-btn" @click.stop="submitForm">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  club: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'submit'])

const form = reactive({
  id: null,
  name: '',
  emoji: '',
  category: '',
  description: '',
  facultyCoordinator: ''
})

watch(
  () => props.club,
  (club) => {
    if (club) {
      form.id = club.id
      form.name = club.name
      form.emoji = club.emoji
      form.category = club.category
      form.description = club.description
      form.facultyCoordinator = club.facultyCoordinator
    }
  },
  { immediate: true }
)

const submitForm = () => {
  if (!form.name.trim()) return

  emit('submit', {
    ...form,
    name: form.name.trim(),
    category: form.category.trim() || 'General',
    description: form.description.trim() || 'Updated club details.',
    facultyCoordinator: form.facultyCoordinator.trim() || 'TBD'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.68);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1100;
}

.modal-card {
  position: relative;
  width: min(100%, 620px);
  background: #fff;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.28);
  display: flex;
  flex-direction: column;
  gap: 18px;
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

.modal-body {
  display: grid;
  gap: 12px;
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
.field select {
  border: 1px solid #dce4ee;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 0.95rem;
  color: #0f172a;
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
</style>