import api from './axios'

export const getClubs = async () => {
  const response = await api.get('/admin/clubs')
  return response.data
}

export const updateClubStatus = async (id, status) => {
  const response = await api.patch(`/admin/clubs/${id}/status`, {
    status
  })
  return response.data
}

export const getFacultyDetails = async () => {
  const response = await api.get('/admin/clubs/faculty-details')
  return response.data
}

export const createClub = async (clubData) => {
  const response = await api.post('/admin/clubs/create', clubData)
  return response.data
}

export const updateClub = async (id, clubData) => {
    const response = await api.put(
        `/admin/clubs/${id}/edit`,
        clubData
    )
    return response.data
}