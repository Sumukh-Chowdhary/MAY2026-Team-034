import api from "./axios"

export const getAssignmentTickets = async (params = {}) => {
    const response = await api.get("/assignment-tickets", { params })
    return response.data
}

export const getAssignmentTicket = async (ticketId) => {
    const response = await api.get(`/assignment-tickets/${ticketId}`)
    return response.data
}

export const updateAssignmentTicket = async (ticketId, payload) => {
    // payload: { action: 'SUSPEND'|'REACTIVATE'|'TERMINATE'|'EDIT_DURATION', remarks?, durationType?, endsAt? }
    const response = await api.patch(`/assignment-tickets/${ticketId}`, payload)
    return response.data
}

export const getUserAssignments = async (targetUserId) => {
    const response = await api.get(`/assignment-tickets/user/${targetUserId}`)
    return response.data
}
