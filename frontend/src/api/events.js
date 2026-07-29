import api from './axios'

export const getEvents = async (params = {}) => {
  const response = await api.get('/events', { params })
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
