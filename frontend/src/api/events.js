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

export const manageEventAttendance = async (id, data, replace = false) => {
  const method = replace ? 'put' : 'post'
  const response = await api[method](`/events/${id}/attendance`, data)
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
