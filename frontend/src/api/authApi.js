import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL;

export const loginApi = async (email, password) => {
  const response = await axios.post(`${BASE_URL}/token`, { email, password });
  return response.data;
};
