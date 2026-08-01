import { io } from 'socket.io-client';
import api from '../api/axios'; // using existing axios instance
import { getCurrentUser } from './authService';

class NotificationService {
    constructor() {
        this.socket = null;
        this.listeners = [];
    }

    initSocket() {
        const user = getCurrentUser();
        if (!user || !user.id) return;

        // the base url where flask is running
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        
        this.socket = io(baseUrl, {
            transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
            console.log('Connected to socket server');
            this.socket.emit('join', { userId: user.id });
        });

        this.socket.on('new_notification', (data) => {
            this.listeners.forEach(cb => cb(data));
        });
    }

    onNotification(callback) {
        this.listeners.push(callback);
    }
    
    offNotification(callback) {
        this.listeners = this.listeners.filter(cb => cb !== callback);
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    async getNotifications() {
        const response = await api.get('/notifications');
        return response.data;
    }

    async markAsRead(id) {
        const response = await api.patch(`/notifications/${id}/read`);
        return response.data;
    }

    async markAllAsRead() {
        const response = await api.patch('/notifications/read-all');
        return response.data;
    }
}

export default new NotificationService();
