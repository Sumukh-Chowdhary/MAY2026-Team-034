import api from './axios'

// Admin APIs
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

// Faculty APIs
export const getFacultyClubs = async () => {
  const response = await api.get('/faculty/clubs')
  return response.data
}

export const updateFacultyClub = async (id, clubData) => {
    const response = await api.put(
        `/faculty/clubs/${id}/edit`,
        clubData
    )
    return response.data
}

// Student APIs
export const getStudentClubs = async () => {
  const response = await api.get('/student/clubs')
  return response.data
}

export const getMyClubs = async () => {
  const response = await api.get('/student/my-clubs')
  return response.data
}

export const getClubAnalytics = async (clubId) => {
  const response = await api.get(`/student/clubs/${clubId}/analytics`)
  return response.data
}

export const joinClub = async (clubId) => {
  const response = await api.post(`/student/clubs/${clubId}/join`)
  return response.data
}

export const leaveClub = async (clubId) => {
  const response = await api.post(`/student/clubs/${clubId}/leave`)
  return response.data
}