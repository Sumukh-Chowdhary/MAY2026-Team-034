<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="club-details-title" @click.stop>
      <button type="button" class="modal-close-btn" @click.stop="emit('close')" aria-label="Close details">
        ×
      </button>

      <div class="top-section">
        <div class="club-icon">{{ club.emoji }}</div>
        <div class="club-info">
          <h3 id="club-details-title">{{ club.name }}</h3>
          <p class="club-category">{{ club.category }}</p>
        </div>
      </div>

      <div class="body-section">
        <p class="club-description">{{ club.description }}</p>

        <div class="detail-grid">
          <div>
            <span>Members</span>
            <strong>{{ club.members }} {{ club.members === 1 ? 'Member' : 'Members' }}</strong>
          </div>
          <div>
            <span>Status</span>
            <strong>{{ club.status || 'Active' }}</strong>
          </div>
          <div>
            <span>Coordinator</span>
            <strong>{{ club.facultyCoordinator || 'TBD' }}</strong>
          </div>
        </div>
      </div>

      <div class="actions-row">
        <button type="button" class="visit-btn" @click.stop="emit('visit')">Visit Club Page</button>
        <button type="button" class="edit-btn" @click.stop="emit('edit')">Edit</button>
        <button type="button" class="delete-btn" @click.stop="emit('delete')">Delete</button>
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

const emit = defineEmits(['close', 'visit', 'edit', 'delete'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1100;
}

.modal-card {
  position: relative;
  width: min(100%, 620px);
  background: #ffffff;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 999px;
  background: #f3f4f6;
  color: #475569;
  font-size: 24px;
  cursor: pointer;
}

.top-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.club-icon {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  background: #eef4ff;
  font-size: 2rem;
}

.club-info h3 {
  margin: 0 0 8px;
  font-size: 1.6rem;
  color: #0f172a;
}

.club-category {
  margin: 0;
  display: inline-flex;
  padding: 8px 14px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.9rem;
  font-weight: 600;
}

.body-section {
  color: #475569;
  line-height: 1.8;
}

.club-description {
  margin: 0 0 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.detail-grid div {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
}

.detail-grid span {
  display: block;
  color: #64748b;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.detail-grid strong {
  color: #0f172a;
  font-size: 1rem;
}

.actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.visit-btn,
.edit-btn,
.delete-btn {
  border: none;
  border-radius: 14px;
  padding: 12px 18px;
  font-weight: 700;
  cursor: pointer;
}

.visit-btn {
  background: #2563eb;
  color: #fff;
}

.edit-btn {
  background: #e2e8f0;
  color: #0f172a;
}

.delete-btn {
  background: #dc2626;
  color: #fff;
}

.visit-btn:hover {
  background: #1d4ed8;
}

.edit-btn:hover {
  background: #cbd5e1;
}

.delete-btn:hover {
  background: #b91c1c;
}

@media (max-width: 640px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>