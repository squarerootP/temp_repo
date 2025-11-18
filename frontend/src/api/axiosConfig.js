import axios from "axios"

import {getToken, removeToken} from "@/services/tokenService"

const BASE_URL = "http://localhost:8000/v1"

const apiClient = axios.create({
    baseURL: BASE_URL,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json"
    }
})

apiClient.interceptors.request.use(
    (config) => {
        const token = getToken()
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    }, (error) => {
        return Promise.reject(error)
    }
);

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            removeToken()
            window.location.href = "/login"
        }
        return Promise.reject(error)
    }
)

export default apiClient

