<template>
  <div class="notifications-page">
    <div class="header-section">
      <h1>Notifications</h1>
      <button v-if="unreadCount > 0" class="btn btn-outline-primary" @click="markAllAsRead">
        Mark All as Read
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
        @click="handleNotificationClick(notification)"
      >
        <div class="card-content">
          <div class="card-header">
            <h3>{{ notification.title }}</h3>
            <span class="time">{{ formatDate(notification.createdAt) }}</span>
          </div>
          <p>{{ notification.message }}</p>
        </div>
        <div v-if="!notification.isRead" class="unread-indicator"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useNotifications } from '../stores/useNotifications';

const router = useRouter();
const notificationStore = useNotifications();
const { notifications, unreadCount } = storeToRefs(notificationStore);

onMounted(() => {
  notificationStore.fetchInitial();
});

const markAllAsRead = async () => {
  await notificationStore.markAllAsRead();
};

const handleNotificationClick = async (notification) => {
  if (!notification.isRead) {
    await notificationStore.markAsRead(notification.id);
  }
  if (notification.referenceUrl) {
    router.push(notification.referenceUrl);
  }
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
