<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    default: null
  },
  style: {
    type: String,
    default: ''
  },
  seed: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  role: {
    type: String,
    default: ''
  },
  size: {
    type: [Number, String],
    default: 'card' // Preset string ('sidebar', 'list', 'table', 'comment', 'card', 'header') or number
  },
  editable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit'])

const hasError = ref(false)

// Size Presets Standard Mapping
const sizePresetMap = {
  sidebar: 48,
  list: 36,
  table: 32,
  comment: 32,
  card: 48,
  header: 96
}

const resolvedPxSize = computed(() => {
  if (typeof props.size === 'number') return props.size
  if (typeof props.size === 'string' && sizePresetMap[props.size]) {
    return sizePresetMap[props.size]
  }
  const parsed = parseInt(props.size, 10)
  return isNaN(parsed) ? 48 : parsed
})

// Extract Effective User Information
const effectiveName = computed(() => {
  return props.name || props.user?.fullName || props.user?.name || props.user?.username || props.user?.email || 'User'
})

const effectiveRole = computed(() => {
  return (props.role || props.user?.role || props.user?.designation || '').toUpperCase()
})

const isPrincipal = computed(() => {
  const r = effectiveRole.value
  const des = (props.user?.designation || '').toLowerCase()
  return r === 'PRINCIPAL' || r === 'PRINCIPAL_EXECUTIVE' || des.includes('principal')
})

const isAdmin = computed(() => {
  return effectiveRole.value === 'ADMIN' || effectiveRole.value === 'ADMINISTRATOR'
})

// Reserved & Custom Avatar Strategy
const avatarUrl = computed(() => {
  const customStyle = props.style || props.user?.avatarStyle
  const customSeed = props.seed || props.user?.avatarSeed

  // If custom avatar style or seed is specified, always use it
  if (customStyle) {
    const seedVal = customSeed || effectiveName.value || 'User'
    return `https://api.dicebear.com/7.x/${customStyle}/svg?seed=${encodeURIComponent(seedVal)}`
  }

  // 1. Reserved Principal Avatar
  if (isPrincipal.value) {
    return `https://api.dicebear.com/7.x/personas/svg?seed=${encodeURIComponent('Principal Executive')}`
  }

  // 2. Reserved System Administrator Avatar
  if (isAdmin.value) {
    return `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent('System Administrator')}`
  }

  // 3. Normal DiceBear Avatar
  const activeSeed = customSeed || effectiveName.value || 'User'
  return `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(activeSeed)}`
})

// Initial Fallback
const initialLetter = computed(() => {
  return effectiveName.value.charAt(0).toUpperCase()
})

function handleImageError() {
  hasError.value = true
}

watch(() => avatarUrl.value, () => {
  hasError.value = false
})

const containerStyle = computed(() => ({
  width: `${resolvedPxSize.value}px`,
  height: `${resolvedPxSize.value}px`,
  fontSize: `${Math.max(12, Math.round(resolvedPxSize.value * 0.45))}px`
}))
</script>

<template>
  <div 
    class="user-avatar-wrapper position-relative flex-shrink-0 d-inline-flex align-items-center justify-content-center"
    :style="containerStyle"
  >
    <!-- Inner Circle Wrapper with overflow-hidden for the avatar image -->
    <div class="w-100 h-100 rounded-circle overflow-hidden border bg-white d-flex align-items-center justify-content-center shadow-xs">
      <!-- DiceBear SVG Avatar -->
      <img 
        v-if="!hasError" 
        :src="avatarUrl" 
        :alt="effectiveName" 
        class="w-100 h-100 rounded-circle avatar-img bg-white"
        @error="handleImageError" 
      />

      <!-- Graceful Initial Fallback on Image Load Error -->
      <div 
        v-else 
        class="w-100 h-100 rounded-circle d-flex align-items-center justify-content-center fw-bold text-white avatar-fallback-bg"
      >
        {{ initialLetter }}
      </div>
    </div>

    <!-- Camera Edit Trigger (Floats outside overflow-hidden inner circle) -->
    <button 
      v-if="editable" 
      class="btn btn-sm btn-primary rounded-circle position-absolute p-0 d-flex align-items-center justify-content-center avatar-edit-btn"
      @click="emit('edit')"
      title="Change Avatar"
    >
      <span class="material-symbols-rounded text-xs" style="font-size: 15px;">photo_camera</span>
    </button>
  </div>
</template>

<style scoped>
.user-avatar-wrapper {
  background-color: transparent;
}

.avatar-img {
  object-fit: cover;
}

.avatar-fallback-bg {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  user-select: none;
}

.avatar-edit-btn {
  width: 28px;
  height: 28px;
  bottom: -2px;
  right: -2px;
  z-index: 10;
  border: 2px solid #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease;
}

.avatar-edit-btn:hover {
  transform: scale(1.1);
}
</style>
