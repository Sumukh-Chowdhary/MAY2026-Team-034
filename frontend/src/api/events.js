import api from './axios'

export const getEvents = async (params = {}) => {
  const response = await api.get('/events', { params })
  return response.data
}

export const getMyEvents = async (scope = 'registered') => {
  const response = await api.get('/events/me', { params: { scope } })
  return response.data
}

export const getEvent = async (id) => {
  const response = await api.get(`/events/${id}`)
  return response.data
}

export const createEvent = async (data) => {
  const response = await api.post('/events/create', data)
  return response.data
}

export const updateEvent = async (id, data) => {
  const response = await api.put(`/events/${id}/edit`, data)
  return response.data
}

export const updateEventStatus = async (id, status) => {
  const response = await api.patch(`/events/${id}/status`, { status })
  return response.data
}

export const assignVenue = async (id, venueId) => {
  const response = await api.post(`/events/${id}/venue`, { venueId })
  return response.data
}

export const registerForEvent = async (id) => {
  const response = await api.post(`/events/${id}/register`)
  return response.data
}

export const getScheduleConflicts = async (id) => {
  const response = await api.get(`/events/${id}/schedule-conflicts`)
  return response.data
}

export const getCalendarEvents = async () => {
  const response = await api.get('/events/calendar')
  return response.data
}

export const createEventTicket = async (id, data) => {
  const response = await api.post(`/events/${id}/tickets`, data)
  return response.data
}

export const manageEventSchedule = async (id, data, replace = false) => {
  const method = replace ? 'put' : 'post'
  const response = await api[method](`/events/${id}/schedule`, data)
  return response.data
}

export const manageEventAnnouncements = async (id, data, replace = false) => {
  const method = replace ? 'put' : 'post'
  const response = await api[method](`/events/${id}/announcements`, data)
  return response.data
}

export const getEventSessions = async (eventId) => {
  const response = await api.get(`/events/${eventId}/sessions`)
  return response.data
}

export const createEventSession = async (eventId, sessionData) => {
  const response = await api.post(`/events/${eventId}/sessions`, sessionData)
  return response.data
}

export const getEventAttendance = async (eventId, sessionId = null) => {
  const params = sessionId ? { sessionId } : {}
  const response = await api.get(`/events/${eventId}/attendance`, { params })
  return response.data
}

export const saveEventAttendance = async (eventId, payload) => {
  const response = await api.post(`/events/${eventId}/attendance`, payload)
  return response.data
}

export const manageEventAttendance = async (id, data, replace = false) => {
  const method = replace ? 'put' : 'post'
  const response = await api[method](`/events/${id}/attendance`, data)
  return response.data
}

export const shortlistSessionParticipants = async (eventId, sessionId, shortlistData) => {
  const response = await api.post(`/events/${eventId}/sessions/${sessionId}/shortlist`, shortlistData)
  return response.data
}

export const updateSessionStatus = async (eventId, sessionId, status) => {
  const response = await api.patch(`/events/${eventId}/sessions/${sessionId}/status`, { status })
  return response.data
}

export const getParticipantProgress = async (eventId) => {
  const response = await api.get(`/events/${eventId}/participant-progress`)
  return response.data
}

export const declareEventResults = async (eventId, resultsData) => {
  const response = await api.post(`/events/${eventId}/results`, resultsData)
  return response.data
}

export const announceEventWinners = async (eventId) => {
  const response = await api.post(`/events/${eventId}/announce-winners`)
  return response.data
}

export const manageEventPrizes = async (id, data, replace = false) => {
  const method = replace ? 'put' : 'post'
  const response = await api[method](`/events/${id}/prizes`, data)
  return response.data
}

export const manageEventOrganizers = async (id, data) => {
  const response = await api.post(`/events/${id}/organizers`, data)
  return response.data
}

export const manageEventVolunteers = async (id, data) => {
  const response = await api.post(`/events/${id}/volunteers`, data)
  return response.data
}

export const updateVolunteerStatus = async (id, volunteerId, status) => {
  const response = await api.patch(`/events/${id}/volunteers/${volunteerId}`, { status })
  return response.data
}
