import api from "./axios"

export const getMySupervisedClubs = async () => {
    const response = await api.get("/faculty/my-clubs")
    return response.data
}

export const leaveFacultyRole = async (clubId) => {
    const response = await api.post(`/faculty/clubs/${clubId}/leave`)
    return response.data
}
