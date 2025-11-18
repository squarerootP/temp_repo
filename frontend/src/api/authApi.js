import apiClient from './axiosConfig';

export const loginApi = async (email, password) => {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const response = await apiClient.post("/token", params, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  });

  return {
    access_token: response.data.access_token,
    token_type: response.data.token_type
  };
};

export const signUpApi = async (userData) => {
  const response = await apiClient.post("/users/", userData);
  return response.data;
};