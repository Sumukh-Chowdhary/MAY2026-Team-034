import api from "./axios"

export const getClubs = async () => {
    const response = await api.get("/student/clubs")
    return response.data
}

export const getMyClubs = async () => {
    const response = await api.get("/student/my-clubs")
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
