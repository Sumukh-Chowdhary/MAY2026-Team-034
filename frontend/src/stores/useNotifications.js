import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/axios'
import { io } from 'socket.io-client'

export const useNotifications = defineStore('notifications', () => {
    const notifications = ref([])
    const unreadCount = ref(0)
    const socket = ref(null)

    const connectSocket = (userId) => {
        if (socket.value) return // already connected
        
        socket.value = io(import.meta.env.VITE_API_URL || 'http://localhost:5000', {
            path: '/socket.io',
            transports: ['websocket', 'polling']
        })

        socket.value.on('connect', () => {
            console.log('Notification socket connected')
            socket.value.emit('join', { userId })
        })

        socket.value.on('new_notification', (notification) => {
            notifications.value.unshift(notification)
            unreadCount.value++
            // keep array size reasonable
            if (notifications.value.length > 50) notifications.value.pop()
        })
    }

    const disconnectSocket = () => {
        if (socket.value) {
            socket.value.disconnect()
            socket.value = null
        }
    }

    const fetchInitial = async () => {
        try {
            const [notifsRes, countRes] = await Promise.all([
                api.get('/notifications'),
                api.get('/notifications/unread-count')
            ])
            if (notifsRes.data.success) {
                notifications.value = notifsRes.data.data
            }
            if (countRes.data.success) {
                unreadCount.value = countRes.data.count
            }
        } catch (error) {
            console.error('Failed to fetch notifications', error)
        }
    }

    const markAsRead = async (id) => {
        const notif = notifications.value.find(n => n.id === id)
        if (notif && !notif.isRead) {
            notif.isRead = true
            unreadCount.value = Math.max(0, unreadCount.value - 1)
            try {
                await api.patch(`/notifications/${id}/read`)
            } catch (error) {
                // rollback on failure
                notif.isRead = false
                unreadCount.value++
                console.error('Failed to mark notification as read', error)
            }
        }
    }

    const markAllAsRead = async () => {
        notifications.value.forEach(n => { n.isRead = true })
        unreadCount.value = 0
        try {
            await api.patch('/notifications/read-all')
        } catch (error) {
            console.error('Failed to mark all as read', error)
        }
    }

    return {
        notifications,
        unreadCount,
        socket,
        connectSocket,
        disconnectSocket,
        fetchInitial,
        markAsRead,
        markAllAsRead
    }
})
