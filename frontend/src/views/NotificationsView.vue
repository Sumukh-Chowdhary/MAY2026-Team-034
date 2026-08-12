<template>
  <div class="notifications-page">
    <div class="header-section d-flex align-items-center justify-content-between mb-4">
      <div class="d-flex align-items-center gap-2">
        <h1 class="m-0 fw-bold fs-3">Notifications</h1>
        <span v-if="unreadCount > 0" class="badge bg-primary rounded-pill px-3 py-1 text-xs">{{ unreadCount }} New</span>
      </div>
      <button v-if="unreadCount > 0" class="btn btn-sm btn-outline-secondary rounded-pill px-3 fw-medium" @click="markAllAsRead">
        Mark all as read
      </button>
    </div>

    <div class="notifications-list">
      <div v-if="notifications.length === 0" class="empty-state">
        <i class="bi bi-bell-slash"></i>
        <p>No notifications yet</p>
      </div>

      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        class="notification-card"
        :class="{ 'unread': !notification.isRead }"
        @click="handleCardClick(notification)"
      >
        <div class="unread-indicator-dot" :class="{ 'is-active': !notification.isRead }"></div>
        <div class="card-content flex-grow-1">
          <div class="card-header d-flex justify-content-between align-items-start mb-1">
            <h3 class="fw-bold fs-6 m-0 text-dark">{{ notification.title }}</h3>
            <span class="time text-muted text-xs ms-2">{{ formatDate(notification.createdAt) }}</span>
          </div>
          <p class="text-secondary text-sm mb-2">{{ notification.message }}</p>
          
          <div v-if="notification.context" class="context-line text-xs fw-semibold text-slate-600 mb-2">
            {{ notification.context }}
          </div>

          <div v-if="getAction(notification)" class="card-actions mt-2">
            <button 
              @click.stop="onActionClick(notification)"
              class="btn btn-sm btn-primary fw-semibold px-3 rounded-2 text-xs"
            >
              {{ getAction(notification).label }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useNotifications } from '../stores/useNotifications';
import { handleNotificationDetails, resolveNotificationAction } from '@/utils/notificationNavigation';
import { getCurrentUser } from '@/services/authService';

const router = useRouter();
const notificationStore = useNotifications();
const { notifications, unreadCount } = storeToRefs(notificationStore);
const currentUser = getCurrentUser();

function getAction(notification) {
  return resolveNotificationAction(notification, currentUser?.role);
}

onMounted(() => {
  notificationStore.fetchInitial();
});

const markAllAsRead = async () => {
  await notificationStore.markAllAsRead();
};

const handleCardClick = async (notification) => {
  if (!notification.isRead) {
    await notificationStore.markAsRead(notification.id);
  }
};

const onActionClick = async (notification) => {
  if (!notification.isRead) {
    await notificationStore.markAsRead(notification.id);
  }
  await handleNotificationDetails(notification, router, notificationStore);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'
    });
  } catch(e) {
    return dateString;
  }
};
</script>

<style scoped>
.notifications-page {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-section h1 {
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid transparent;
}

.notification-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.notification-card.unread {
  border-left-color: #3b82f6;
  background: #f8fafc;
}

.card-content {
  flex-grow: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.5rem;
}

.card-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.time {
  font-size: 0.85rem;
  color: #64748b;
}

.card-content p {
  color: #475569;
  margin: 0;
  font-size: 0.95rem;
}

.unread-indicator {
  width: 10px;
  height: 10px;
  background-color: #3b82f6;
  border-radius: 50%;
  margin-left: 1rem;
  margin-top: 0.25rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #94a3b8;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}
</style>
