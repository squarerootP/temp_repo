import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/api/authApi';
import { saveToken, removeToken, getToken } from '@/services/tokenService';
import { useNavigate } from 'react-router-dom';

export const authKeys = {
    currentUser: ['auth', 'currentUser']
}

export const useLogin = ()=>{
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({
            email, password
        }) => authApi.login(email, password),
        onSuccess: (data) => {
            console.log('Login response:', data)
            if (!data || !data.access_token) {
                throw new Error("invalid login response")
            }
            saveToken(data.access_token)
            queryClient.setQueryData(authKeys.currentUser, data.user)
            
            navigate('/home')
        },
        onError: (error) => {
            console.error("login failed", error)
        }

    })
}

export const useCurrentUser = () => {
    return useQuery({
        queryKey: authKeys.currentUser,
        queryFn: authApi.getCurrentUser,
        enabled: !!getToken(),
        retry: false, 
        staleTime: 10 * 60 * 1000
    })
}
export const useLogout = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      removeToken();
      queryClient.clear(); // Clear all cached data
    },
    onSuccess: () => {
      navigate('/login');
    },
  });
};

// Register mutation
export const useRegister = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (userData) => authApi.register(userData),
    onSuccess: () => {
      navigate('/login');
    },
  });
};