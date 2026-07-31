import api from "./axios"

export const reseedDatabase = async () => {
    const response = await api.post("/admin/seed")
    return response.data
}
