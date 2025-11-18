import apiClient from './axiosConfig';

export const userApi = {
    getCurrentUser: async () => {
        const response =  await apiClient.get('/users/me');
        return response.data;
    },

    getAllUsers: async () => {
        const response =  await apiClient.get('/users');
    },

    createUser: async (userData) => {

        const response =  await apiClient.post('/users', userData);
        return response.data;
    }
}