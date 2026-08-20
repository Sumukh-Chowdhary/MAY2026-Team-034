import api from "./axios"

export const reseedDatabase = async () => {
    const response = await api.post("/admin/seed")
    return response.data
}

export const getAdminAnalytics = async () => {
    const response = await api.get("/admin/analytics")
    return response.data
}
