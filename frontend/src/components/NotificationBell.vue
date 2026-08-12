<template>
  <div class="nb-container" ref="dropdownRef">
    <button 
      @click="toggleDropdown" 
      class="nb-trigger"
      aria-label="Notifications"
    >
      <!-- Bell Icon -->
      <svg xmlns="http://www.w3.org/2000/svg" class="nb-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="24" height="24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      <!-- Unread Badge -->
      <span v-if="unreadCount > 0" class="nb-badge">
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Dropdown Panel -->
    <transition name="nb-fade-slide">
      <div v-if="isOpen" class="nb-dropdown">
        <div class="nb-dropdown-header">
          <h3>Notifications</h3>
          <button v-if="unreadCount > 0" @click="markAllAsRead" class="nb-mark-all">
            Mark all as read
          </button>
        </div>

        <div class="nb-dropdown-body">
          <div v-if="notifications.length === 0" class="nb-empty">
            <svg class="nb-empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="32" height="32">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <p>You're all caught up!</p>
          </div>
          
          <div 
            v-for="notification in notifications.slice(0, 15)" 
            :key="notification.id"
            @click="handleNotificationClick(notification)"
            class="nb-item"
            :class="{'nb-item-unread': !notification.isRead}"
          >
            <div class="nb-item-top">
              <span class="nb-item-title">{{ notification.title }}</span>
              <span v-if="!notification.isRead" class="nb-dot"></span>
            </div>
            <p class="nb-item-message">{{ notification.message }}</p>
            <span class="nb-item-time">{{ formatDate(notification.createdAt) }}</span>
          </div>
        </div>

        <div class="nb-dropdown-footer">
          <router-link :to="notificationsPath" class="nb-view-all" @click="isOpen = false">
            View all notifications
          </router-link>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useNotifications } from '../stores/useNotifications';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const notificationStore = useNotifications();
const authStore = useAuthStore();
const { notifications, unreadCount } = storeToRefs(notificationStore);

const isOpen = ref(false);
const dropdownRef = ref(null);

const notificationsPath = computed(() => {
  const role = authStore.user?.role || 'STUDENT';
  if (role === 'ADMIN') return '/admin/notifications';
  if (role === 'FACULTY') return '/faculty/notifications';
  return '/student/notifications';
})

import { handleNotificationDetails, resolveNotificationAction } from '@/utils/notificationNavigation';

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    isOpen.value = false;
  }
};

const markAllAsRead = async () => {
  await notificationStore.markAllAsRead();
};

const handleNotificationClick = async (notification) => {
  isOpen.value = false;
  const role = authStore.user?.role || 'STUDENT';
  const action = resolveNotificationAction(notification, role);
  if (action) {
    await handleNotificationDetails(notification, router, notificationStore);
  } else {
    if (!notification.isRead) {
      await notificationStore.markAsRead(notification.id);
    }
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    return new Date(dateString).toLocaleDateString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'
    });
  } catch(e) {
    return dateString;
  }
};

onMounted(() => {
  notificationStore.fetchInitial();
  if (authStore.user?.id) {
    notificationStore.connectSocket(authStore.user.id);
  }
  document.addEventListener('click', closeDropdown);
});

onUnmounted(() => {
  notificationStore.disconnectSocket();
  document.removeEventListener('click', closeDropdown);
});
</script>

<style scoped>
.nb-container {
  position: relative;
  display: inline-block;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.nb-trigger {
  position: relative;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 10px;
  border-radius: 50%;
  cursor: pointer;
  outline: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
  backdrop-filter: blur(8px);
}

.nb-trigger:hover {
  background: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.08);
  border-color: rgba(37, 99, 235, 0.3);
}

.nb-icon {
  color: #475569;
  transition: color 0.3s ease;
}

.nb-trigger:hover .nb-icon {
  color: #2563eb;
}

.nb-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  height: 20px;
  min-width: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
  animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.nb-dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 360px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.4);
  overflow: hidden;
  z-index: 100;
}

.nb-dropdown-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(248, 250, 252, 0.8);
}

.nb-dropdown-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.01em;
}

.nb-mark-all {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.nb-mark-all:hover {
  background: rgba(37, 99, 235, 0.1);
}

.nb-dropdown-body {
  max-height: 400px;
  overflow-y: auto;
}

.nb-dropdown-body::-webkit-scrollbar {
  width: 6px;
}
.nb-dropdown-body::-webkit-scrollbar-track {
  background: transparent;
}
.nb-dropdown-body::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}

.nb-empty {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
}
.nb-empty-icon {
  margin: 0 auto 12px;
  color: #cbd5e1;
}

.nb-item {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.nb-item:hover {
  background: rgba(248, 250, 252, 0.9);
}

.nb-item-unread {
  background: #eff6ff; /* More prominent blue */
  border-left: 3px solid #3b82f6; /* Left border highlight */
}
.nb-item-unread:hover {
  background: #dbeafe;
}

.nb-item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
}

.nb-item-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
  margin-right: 12px;
}
.nb-item-unread .nb-item-title {
  color: #0f172a;
  font-weight: 700;
}

.nb-dot {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 5px;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.nb-item-message {
  margin: 0 0 8px 0;
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.nb-item-time {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.nb-dropdown-footer {
  padding: 12px 20px;
  text-align: center;
  background: rgba(248, 250, 252, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.nb-view-all {
  display: block;
  text-decoration: none;
  color: #2563eb;
  font-size: 0.85rem;
  font-weight: 600;
  transition: color 0.2s;
}

.nb-view-all:hover {
  color: #1d4ed8;
}

/* Animations */
.nb-fade-slide-enter-active,
.nb-fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-origin: top right;
}
.nb-fade-slide-enter-from,
.nb-fade-slide-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

@keyframes popIn {
  0% { transform: scale(0); }
  80% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

@media (max-width: 480px) {
  .nb-dropdown {
    width: 300px;
    right: -20px;
  }
}
</style>
