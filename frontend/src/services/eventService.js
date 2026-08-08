import { io } from 'socket.io-client';
import api from '../api/axios';
import { getCurrentUser } from './authService';

class EventSocketService {
    constructor() {
        this.socket = null;
        this.listeners = {};
    }

    initSocket() {
        if (this.socket) return;
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';

        this.socket = io(baseUrl, {
            transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
            console.log('Connected to Event Socket Server');
            const user = getCurrentUser();
            if (user && user.id) {
                this.socket.emit('join', { userId: user.id });
            }
            this.socket.emit('join_events');
        });

        const socketEvents = [
            'event_created',
            'event_updated',
            'event_schedule_updated',
            'event_announcement_created',
            'event_attendance_updated',
            'event_volunteer_updated',
            'event_prize_updated'
        ];

        socketEvents.forEach(evt => {
            this.socket.on(evt, (data) => {
                if (this.listeners[evt]) {
                    this.listeners[evt].forEach(cb => cb(data));
                }
            });
        });
    }

    joinEventRoom(eventId) {
        if (this.socket && eventId) {
            this.socket.emit('join_event', { eventId });
        }
    }

    leaveEventRoom(eventId) {
        if (this.socket && eventId) {
            this.socket.emit('leave_event', { eventId });
        }
    }

    on(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
        }
        this.listeners[eventType].push(callback);
    }

    off(eventType, callback) {
        if (!this.listeners[eventType]) return;
        this.listeners[eventType] = this.listeners[eventType].filter(cb => cb !== callback);
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }
}

export const eventSocketService = new EventSocketService();

export async function fetchCalendarEvents() {
    const response = await api.get('/events/calendar');
    return response.data;
}

export async function createEventTicket(eventId, payload) {
    const response = await api.post(`/events/${eventId}/tickets`, payload);
    return response.data;
}

export async function applyEventVolunteer(eventId) {
    const response = await api.post(`/events/${eventId}/volunteers`);
    return response.data;
}

export async function updateVolunteerStatus(eventId, volunteerId, status) {
    const response = await api.patch(`/events/${eventId}/volunteers/${volunteerId}`, { status });
    return response.data;
}
