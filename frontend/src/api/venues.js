import api from './axios'

export const getVenues = async (params = {}) => {
  const response = await api.get('/venues', { params })
  return response.data
}

export const getVenue = async (id) => {
  const response = await api.get(`/venues/${id}`)
  return response.data
}

export const createVenue = async (data) => {
  const response = await api.post('/venues/create', data)
  return response.data
}

export const updateVenue = async (id, data) => {
  const response = await api.put(`/venues/${id}/edit`, data)
  return response.data
}

export const updateVenueStatus = async (id, status) => {
  const response = await api.patch(`/venues/${id}/status`, { status })
  return response.data
}
