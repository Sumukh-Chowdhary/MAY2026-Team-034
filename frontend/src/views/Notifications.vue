<template>
  <component :is="layoutComponent">
    <div class="notif-page-wrapper">
      <div class="notif-header">
        <div class="notif-title-group">
          <h1 class="notif-title">Notifications</h1>
          <span class="notif-count-badge" v-if="unreadCount > 0">{{ unreadCount }} New</span>
        </div>
        <button 
          v-if="unreadCount > 0"
          @click="markAllAsRead" 
          class="btn-mark-all"
        >
          <svg class="notif-btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="18" height="18">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          Mark all as read
        </button>
      </div>

      <div v-if="loading" class="notif-loading">
        <div class="spinner"></div>
      </div>

      <div v-else-if="notifications.length === 0" class="notif-empty-state">
        <div class="empty-icon-wrapper">
          <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="64" height="64">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </div>
        <h3>No notifications</h3>
        <p>You're all caught up on your alerts and updates!</p>
      </div>

      <div v-else class="notif-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notif-card"
          :class="{'is-unread': !notification.isRead}"
        >
          <div class="notif-card-indicator">
            <div class="status-dot"></div>
          </div>
          
          <div class="notif-card-content">
            <div class="notif-card-header">
              <h4 class="notif-card-title">{{ notification.title }}</h4>
              <span class="notif-card-date">{{ formatDate(notification.createdAt) }}</span>
            </div>
            
            <p class="notif-card-message">{{ notification.message }}</p>
            
            <div class="notif-card-actions">
              <button 
                v-if="notification.referenceUrl" 
                @click="goToLink(notification)"
                class="btn-action primary-action"
              >
                View Details
              </button>
              <button 
                v-if="!notification.isRead" 
                @click="markAsRead(notification)"
                class="btn-action secondary-action"
              >
                Mark as read
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </component>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import notificationService from '../services/notification.service';
import { getCurrentUser } from '@/services/authService';

import AdminLayout from '@/layouts/AdminLayout.vue';
import FacultyLayout from '@/layouts/FacultyLayout.vue';
import StudentLayout from '@/layouts/StudentLayout.vue';

const user = getCurrentUser();
const layoutComponent = computed(() => {
  if (user?.role === 'ADMIN') return AdminLayout;
  if (user?.role === 'FACULTY') return FacultyLayout;
  return StudentLayout;
});

const router = useRouter();
const notifications = ref([]);
const loading = ref(true);

const unreadCount = computed(() => notifications.value.filter(n => !n.isRead).length);

const fetchNotifications = async () => {
  loading.value = true;
  try {
    const res = await notificationService.getNotifications();
    if (res.success) {
      notifications.value = res.data;
    }
  } catch (error) {
    console.error("Failed to fetch notifications:", error);
  } finally {
    loading.value = false;
  }
};

const markAllAsRead = async () => {
  try {
    const res = await notificationService.markAllAsRead();
    if (res.success) {
      notifications.value.forEach(n => n.isRead = true);
    }
  } catch (error) {
    console.error("Failed to mark all as read:", error);
  }
};

const markAsRead = async (notification) => {
  if (notification.isRead) return;
  try {
    const res = await notificationService.markAsRead(notification.id);
    if (res.success) {
      notification.isRead = true;
    }
  } catch (error) {
    console.error("Failed to mark as read:", error);
  }
};

const goToLink = async (notification) => {
  if (!notification.isRead) {
    await markAsRead(notification);
  }
  router.push(notification.referenceUrl);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    return new Date(dateString).toLocaleString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'
    });
  } catch(e) {
    return dateString;
  }
};

onMounted(() => {
  fetchNotifications();
});
</script>

<style scoped>
/* Premium Typography & Variables */
.notif-page-wrapper {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Header Section */
.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 20px;
}

.notif-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notif-title {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
  margin: 0;
}

.notif-count-badge {
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  border: 1px solid #bfdbfe;
}

.btn-mark-all {
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 8px;
  color: #475569;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.btn-mark-all:hover {
  background: #f8fafc;
  color: #0f172a;
  border-color: #cbd5e1;
}

/* Loading State */
.notif-loading {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.notif-empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  border: 1px dashed #cbd5e1;
}
.empty-icon-wrapper {
  background: #f8fafc;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: #94a3b8;
}
.notif-empty-state h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}
.notif-empty-state p {
  color: #64748b;
  margin: 0;
}

/* Notification List & Cards */
.notif-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notif-card {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.notif-card:hover {
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  transform: translateY(-2px);
  border-color: #cbd5e1;
}

.is-unread {
  background: #f8fafc;
  border-color: #bfdbfe;
}
.is-unread::before {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 4px;
  background: #3b82f6;
}

.notif-card-indicator {
  margin-right: 16px;
  margin-top: 6px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e2e8f0;
}

.is-unread .status-dot {
  background: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

.notif-card-content {
  flex: 1;
  min-width: 0;
}

.notif-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.notif-card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #475569;
  margin: 0;
  line-height: 1.4;
}

.is-unread .notif-card-title {
  color: #0f172a;
  font-weight: 700;
}

.notif-card-date {
  font-size: 0.85rem;
  color: #94a3b8;
  white-space: nowrap;
  margin-left: 16px;
}

.notif-card-message {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.notif-card-actions {
  display: flex;
  gap: 12px;
}

.btn-action {
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.primary-action {
  background: #3b82f6;
  color: white;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}
.primary-action:hover {
  background: #2563eb;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
}

.secondary-action {
  background: transparent;
  color: #64748b;
}
.secondary-action:hover {
  background: #f1f5f9;
  color: #334155;
}
</style>
