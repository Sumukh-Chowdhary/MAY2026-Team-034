import api from "./axios"

export const createRequest = async (requestData) => {
    const response = await api.post("/requests", requestData)
    return response.data
}

export const getRequests = async (params = {}) => {
    const response = await api.get("/requests", { params })
    return response.data
}

export const getRequest = async (requestId) => {
    const response = await api.get(`/requests/${requestId}`)
    return response.data
}

export const updateRequest = async (requestId, requestData) => {
    const response = await api.patch(`/requests/${requestId}`, requestData)
    return response.data
}

export const approveRequest = async (requestId, remarks = "") => {
    const response = await api.post(`/requests/${requestId}/approve`, { remarks })
    return response.data
}

export const rejectRequest = async (requestId, remarks = "") => {
    const response = await api.post(`/requests/${requestId}/reject`, { remarks })
    return response.data
}

export const requestChanges = async (requestId, remarks = "") => {
    const response = await api.post(`/requests/${requestId}/request-changes`, { remarks })
    return response.data
}

export const getApprovals = async (requestId) => {
    const response = await api.get(`/requests/${requestId}/approvals`)
    return response.data
}

// Dashboard Endpoints
export const getStudentRequestsDashboard = async () => {
    const response = await api.get("/student/requests/dashboard")
    return response.data
}

export const getFacultyRequestsDashboard = async () => {
    const response = await api.get("/faculty/requests/dashboard")
    return response.data
}

export const getAdminRequestsDashboard = async () => {
    const response = await api.get("/admin/requests/dashboard")
    return response.data
}

export const resubmitRequest = async (requestId, payload) => {
    const response = await api.post(`/requests/${requestId}/resubmit`, payload)
    return response.data
}