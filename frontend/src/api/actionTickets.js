import api from "./axios"

export const createActionTicket = async (ticketData) => {
    const response = await api.post("/action-tickets", ticketData)
    return response.data
}

export const getActionTickets = async (params = {}) => {
    const response = await api.get("/action-tickets", { params })
    return response.data
}

export const getActionTicket = async (ticketId) => {
    const response = await api.get(`/action-tickets/${ticketId}`)
    return response.data
}

export const approveActionTicket = async (ticketId) => {
    const response = await api.post(`/action-tickets/${ticketId}/approve`)
    return response.data
}

export const rejectActionTicket = async (ticketId, remarks = "") => {
    const response = await api.post(`/action-tickets/${ticketId}/reject`, { remarks })
    return response.data
}

export const requestChangesActionTicket = async (ticketId, remarks = "") => {
    const response = await api.post(`/action-tickets/${ticketId}/request-changes`, { remarks })
    return response.data
}

export const getActionTicketApprovals = async (ticketId) => {
    const response = await api.get(`/action-tickets/${ticketId}/approvals`)
    return response.data
}

export const updateTaskStatus = async (ticketId, action, remarks = "") => {
    const response = await api.patch(`/action-tickets/${ticketId}/task`, { action, remarks })
    return response.data
}

export const resubmitActionTicket = async (ticketId, payload) => {
    const response = await api.post(`/action-tickets/${ticketId}/resubmit`, payload)
    return response.data
}
