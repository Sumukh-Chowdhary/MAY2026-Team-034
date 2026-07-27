import axios from "axios";

const API = "http://127.0.0.1:5000/api/auth";

axios.interceptors.request.use(config => {
    const token = localStorage.getItem("token");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

export async function login(username, password) {
    const response = await axios.post(`${API}/login`, {
        username,
        password
    });

    const { token, user } = response.data;

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));

    return user;
}

export function getCurrentUser() {
    return JSON.parse(localStorage.getItem("user"));
}

export function isLoggedIn() {
    return !!localStorage.getItem("token");
}

export async function logout() {

    try {
        await axios.post(`${API}/logout`)
    } catch (e) {
        // Ignore errors
    }

    localStorage.removeItem("token")
    localStorage.removeItem("user")
}