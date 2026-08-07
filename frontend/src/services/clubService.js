import axios from "axios";
import { getCurrentUser, isLoggedIn } from "./authService";

const API = "http://127.0.0.1:5000/api";

function getRolePrefix() {
    if (!isLoggedIn()) {
        return "";
    }

    const user = getCurrentUser();

    switch (user?.role) {
        case "ADMIN":
            return "/admin";

        case "FACULTY":
            return "/faculty";

        case "STUDENT":
            return "/student";

        default:
            return "";
    }
}

export async function getClub(clubId) {
    const response = await axios.get(
        `${API}${getRolePrefix()}/clubs/${clubId}`
    );

    return response.data;
}

export async function getClubMembers(clubId) {
    const response = await axios.get(
        `${API}${getRolePrefix()}/clubs/${clubId}/members`
    );

    return response.data;
}

export async function getClubEvents(clubId) {
    const response = await axios.get(
        `${API}${getRolePrefix()}/clubs/${clubId}/events`
    );

    return response.data;
}

export async function getClubs() {
    const response = await axios.get(
        `${API}${getRolePrefix()}/clubs`
    )

    return response.data
}

export async function updateClubMemberStatus(clubId, userId, active) {
    const endpoint = active ? "reactivate" : "deactivate"

    const response = await axios.patch(
        `${API}${getRolePrefix()}/clubs/${clubId}/members/${userId}/${endpoint}`
    )

    return response.data
}

