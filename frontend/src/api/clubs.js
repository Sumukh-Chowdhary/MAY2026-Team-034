import api from './axios'

export const getClubs = async () => {
  const response = await api.get('/admin/clubs')
  return response.data
}

/*
export const getClub = async (id) => {
  const response = await api.get(`/admin/clubs/${id}`)
  return response.data
}

export const createClub = async (club) => {
  const response = await api.post('/admin/clubs', club)
  return response.data
}

export const updateClub = async (id, club) => {
  const response = await api.put(`/admin/clubs/${id}`, club)
  return response.data
}

export const deleteClub = async (id) => {
  const response = await api.delete(`/admin/clubs/${id}`)
  return response.data
}*/