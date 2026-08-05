<template>
  <div 
    class="modal-overlay" 
    @click.self="emit('close')"
  >
    <div 
      class="modal-card" 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="club-details-title" 
      @click.stop
    >
      <button 
        type="button" 
        class="modal-close-btn" 
        aria-label="Close details"
        @click.stop="emit('close')" 
      >
        ×
      </button>

      <div class="top-section">
        <div class="club-icon">
          <span class="material-symbols-rounded">
            {{ club.logo }}
          </span>
        </div>
        <div class="club-info">
          <h3 id="club-details-title">{{ club.name }}</h3>
          <div class="club-tags">
            <span class="club-category">{{ club.category }}</span>
          </div>
        </div>
      </div>

      <div class="body-section">
        <p class="club-description">{{ club.description }}</p>
        
        <hr class="section-divider" />
        
        <div class="detail-grid">
          <div>
            <span>Total Members</span>
            <strong>{{ club.totalMembers }}</strong>
          </div>
          
          <div>
            <span>Active Members</span>
            <strong>{{ club.activeMembers }}</strong>
          </div>
          
          <div>
            <span>Club Status</span>
            <strong>
              {{ club.status === 'ACTIVE' ? 'Live Club' : 'Legacy Club' }}
            </strong>
          </div>

          <div>
            <span>Created On</span>
            <strong>{{ formatDate(club.createdAt) }}</strong>
          </div>

          <div class="faculty-card">
            <span>Faculty Coordinators</span>

            <div
              v-if="club.faculty?.length"
              class="faculty-list"
            >
              <div
                v-for="advisor in club.faculty"
                :key="advisor.id"
                class="faculty-chip"
              >
                {{ advisor.name }}
              </div>
            </div>

            <strong v-else>
              Not Assigned
            </strong>
          </div>
        </div>

        <div class="actions-row">
          <button
            type="button"
            class="visit-btn"
            @click.stop="emit('visit')"
          >
            Visit Club Page
          </button>

          <div class="admin-actions">
            <button
              v-if="!isMember"
              type="button"
              class="edit-btn"
              @click.stop="emit('edit')"
            >
              Edit Club
            </button>
            <div v-if="!isMember">
              <button
                v-if="canArchive && club.status === 'ACTIVE'"
                type="button"
                class="archive-btn"
                @click.stop="emit('archive')"
              >
                Archive Club
              </button>


              <button
                  v-if="canArchive && club.status === 'INACTIVE'"
                  type="button"
                  class="restore-btn"
                  @click.stop="emit('restore')"
              >
                  Restore Club
              </button>
            </div>
          </div>

          <button
            v-if="isMember"
            type="button"
            class="leave-btn"
            @click.stop="emit('leave')"
          >
            Leave Club
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

const props = defineProps({
  club: {
    type: Object,
    required: true
  },
  isMember: {
    type: Boolean,
    default: false
  },
  canArchive: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'close',
  'visit',
  'edit',
  'archive',
  'restore',
  'leave'
])
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
  width: min(100%, 580px);
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
  align-items: flex-start;
  gap: 20px;
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

.club-icon .material-symbols-rounded {
  font-size: 42px;
  color: #2563eb;
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

.club-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  margin-left: 8px;
}

.club-status.live {
  background: #dcfce7;
  color: #15803d;
}

.club-status.inactive {
  background: #fef9c3;
  color: #a16207;
}

.body-section {
  color: #475569;
  line-height: 1.8;
}

.club-description {
  margin: 0 0 20px;
}

.section-divider {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 8px 0 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.detail-grid > div:not(.faculty-card) {
  background: #f8fafc;
  border-radius: 16px;
  padding: 18px;
  min-height: 90px;
  display: flex;
  flex-direction: column;
  justify-content: center;
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

.faculty-card {
  grid-column: 1 / -1;
  background: #f8fafc;
  border-radius: 18px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.faculty-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
}

.faculty-chip {
  background: #eef4ff;
  color: #2563eb;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  line-height: 1;
}

.actions-row {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 24px;
}

.admin-actions {
  display: flex;
  gap: 12px;
}

.admin-actions button {
  flex: 1;
}

.visit-btn,
.edit-btn,
.archive-btn,
.restore-btn,
.leave-btn {
  border: none;
  border-radius: 14px;
  padding: 13px 18px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.visit-btn {
  width: 100%;
  background: #2563eb;
  color: #fff;
}

.visit-btn:hover {
  background: #1d4ed8;
}

.edit-btn {
  background: #e2e8f0;
  color: #0f172a;
}

.edit-btn:hover {
  background: #cbd5e1;
}

.archive-btn {
  background: #dc2626;
  color: white;
}

.archive-btn:hover {
  background: #b91c1c;
}

.restore-btn {
  background: #16a34a;
  color: white;
}

.restore-btn:hover {
  background: #15803d;
}

.leave-btn {
  background: #dc2626;
  color: #fff;
}

.leave-btn:hover {
  background: #b91c1c;
}

@media (max-width: 640px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>