<script setup>
const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  isEditing: {
    type: Boolean,
    default: false
  },
  saving: {
    type: Boolean,
    default: false
  },
  readOnlyEmail: {
    type: Boolean,
    default: true
  },
  readOnlyDept: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['save', 'update:user'])
</script>

<template>
  <div class="card border-0 shadow-sm rounded-4 p-4 h-100 user-info-card">
    <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
      <h5 class="fw-bold text-dark m-0 d-flex align-items-center gap-2">
        <span class="material-symbols-rounded text-primary">person</span>
        Personal Information
      </h5>
      <span class="badge bg-light text-muted border text-xs" v-if="!isEditing">
        Read-Only Mode
      </span>
      <span class="badge bg-primary-subtle text-primary border text-xs" v-else>
        Editing Mode
      </span>
    </div>

    <form @submit.prevent="emit('save')" class="d-flex flex-column gap-3">
      <!-- Full Name -->
      <div>
        <label class="form-label text-xs fw-bold text-uppercase text-muted">Full Name / Display Name</label>
        <input 
          type="text" 
          class="form-control rounded-3" 
          v-model="user.fullName" 
          :disabled="!isEditing"
          required 
        />
      </div>

      <!-- Registration No / Employee ID -->
      <div v-if="user.registerNumber || user.rollNo || user.employeeId">
        <label class="form-label text-xs fw-bold text-uppercase text-muted d-flex align-items-center gap-1">
          {{ user.role === 'FACULTY' ? 'Employee ID' : 'Registration Number' }}
          <span class="material-symbols-rounded fs-6 text-muted" title="Institutional ID">lock</span>
        </label>
        <input 
          type="text" 
          class="form-control rounded-3 bg-light text-secondary" 
          :value="user.registerNumber || user.rollNo || user.employeeId" 
          disabled 
        />
      </div>

      <!-- Phone -->
      <div v-if="user.phone || isEditing">
        <label class="form-label text-xs fw-bold text-uppercase text-muted">Phone Number</label>
        <input 
          type="text" 
          class="form-control rounded-3" 
          v-model="user.phone" 
          :disabled="!isEditing"
          placeholder="+91 XXXXX XXXXX" 
        />
      </div>

      <!-- Year of Study (Students) -->
      <div v-if="user.role === 'STUDENT' || user.year">
        <label class="form-label text-xs fw-bold text-uppercase text-muted">Year of Study</label>
        <select 
          v-if="isEditing" 
          class="form-select rounded-3" 
          v-model="user.year"
        >
          <option value="1st Year">1st Year</option>
          <option value="2nd Year">2nd Year</option>
          <option value="3rd Year">3rd Year</option>
          <option value="4th Year">4th Year</option>
        </select>
        <input 
          v-else 
          type="text" 
          class="form-control rounded-3" 
          :value="user.year || '—'" 
          disabled 
        />
      </div>

      <!-- Designation (Faculty) -->
      <div v-if="user.role === 'FACULTY' || user.designation">
        <label class="form-label text-xs fw-bold text-uppercase text-muted">Designation</label>
        <input 
          type="text" 
          class="form-control rounded-3" 
          v-model="user.designation" 
          :disabled="!isEditing"
          placeholder="e.g. Associate Professor" 
        />
      </div>

      <!-- Email -->
      <div>
        <label class="form-label text-xs fw-bold text-uppercase text-muted d-flex align-items-center gap-1">
          Email Address
          <span v-if="readOnlyEmail" class="material-symbols-rounded fs-6 text-muted" title="Read-only field">lock</span>
        </label>
        <input 
          type="email" 
          class="form-control rounded-3"
          :class="readOnlyEmail ? 'bg-light text-secondary' : ''"
          v-model="user.email" 
          :disabled="readOnlyEmail || !isEditing" 
        />
      </div>

      <!-- Department -->
      <div>
        <label class="form-label text-xs fw-bold text-uppercase text-muted d-flex align-items-center gap-1">
          Department
          <span v-if="readOnlyDept" class="material-symbols-rounded fs-6 text-muted" title="Read-only field">lock</span>
        </label>
        <input 
          type="text" 
          class="form-control rounded-3"
          :class="readOnlyDept ? 'bg-light text-secondary' : ''"
          v-model="user.department" 
          :disabled="readOnlyDept || !isEditing" 
        />
      </div>

      <!-- Bio -->
      <div>
        <label class="form-label text-xs fw-bold text-uppercase text-muted">Bio / About Me</label>
        <textarea 
          class="form-control rounded-3" 
          rows="3" 
          v-model="user.bio" 
          :disabled="!isEditing"
          placeholder="Share a brief bio or description..."
        ></textarea>
      </div>

      <!-- Footer Actions -->
      <div v-if="isEditing" class="pt-2">
        <button type="submit" class="btn btn-success rounded-pill px-4 font-semibold text-xs" :disabled="saving">
          <i class="bi bi-check-circle me-1"></i> {{ saving ? 'Saving...' : 'Save Profile Changes' }}
        </button>
      </div>

      <slot name="footer-actions"></slot>
    </form>
  </div>
</template>
