<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="delete-club-title" @click.stop>
      <button type="button" class="modal-close-btn" @click.stop="emit('close')" aria-label="Close delete club">
        ×
      </button>

      <div class="modal-header">
        <div class="modal-title-block">
          <span class="category">Delete Club</span>
          <h3 id="delete-club-title">Remove this club?</h3>
        </div>
      </div>

      <div class="modal-body">
        <p>
          Are you sure you want to delete
          <strong>{{ club?.name }}</strong>?
          This action cannot be undone.
        </p>
      </div>

      <div class="modal-actions">
        <button type="button" class="cancel-btn" @click.stop="emit('close')">Cancel</button>
        <button type="button" class="delete-btn" @click.stop="emit('confirm')">Delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  club: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'confirm'])
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
  width: min(100%, 520px);
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
  background: #fee2e2;
  color: #b91c1c;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.modal-body p {
  margin: 0;
  color: #334155;
  line-height: 1.8;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-btn,
.delete-btn {
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

.delete-btn {
  background: #dc2626;
  color: white;
}
</style>