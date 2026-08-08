<script setup>
import UserAvatar from './UserAvatar.vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  editableAvatar: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['edit-avatar'])
</script>

<template>
  <div class="card border-0 shadow-sm rounded-4 overflow-hidden user-profile-header-card">
    <div class="header-banner" style="height: 90px; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);"></div>
    <div class="card-body p-4 pt-0 position-relative">
      <div class="d-flex flex-wrap align-items-end justify-content-between gap-3">
        
        <div class="d-flex align-items-end gap-3 avatar-header-group">
          <div class="avatar-wrapper" style="margin-top: -48px;">
            <UserAvatar 
              size="header"
              :user="user"
              :editable="editableAvatar"
              @edit="emit('edit-avatar')"
            />
          </div>

          <div class="user-identity mb-1">
            <h3 class="fw-bold text-dark m-0">{{ user.fullName || user.name || 'User' }}</h3>
            <div class="d-flex align-items-center gap-2 mt-1 flex-wrap">
              <span class="badge bg-primary-subtle text-primary border px-2.5 py-1 text-xs font-semibold">
                {{ user.role || 'Member' }}
              </span>
              <span class="badge bg-light text-dark border px-2.5 py-1 text-xs">
                {{ user.department || 'General' }}
              </span>
              <span class="badge" :class="user.status === 'ACTIVE' ? 'bg-success-subtle text-success border' : 'bg-danger-subtle text-danger border'">
                ● {{ user.status || 'ACTIVE' }}
              </span>
            </div>
            <small class="text-secondary text-xs d-block mt-1">
              <i class="bi bi-envelope me-1"></i>{{ user.email }}
            </small>
          </div>
        </div>

        <!-- Custom Actions Slot -->
        <div class="d-flex flex-wrap align-items-center gap-2 ms-auto">
          <slot name="actions"></slot>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.user-profile-header-card {
  background: white;
}
</style>
