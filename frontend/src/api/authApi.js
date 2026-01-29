import apiClient from './axiosConfig';

export const authApi = {
  login: async (email, password) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    
    const response = await apiClient.post('/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    const {access_token} = response.data

    const userResponse = await apiClient.get('/users/me', {
      headers: {
        Authorization: `Bearer ${access_token}`
      }
    })
    return {
      access_token, 
      user: userResponse.data
    }
  },

  register: async (userData) => {
    const response = await apiClient.post('/users/', userData);
    return response.data;
  },

  getCurrentUser: async() => {
    const response =  await apiClient.get('/users/me');
    return response.data;
  } 
}
