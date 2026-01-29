import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi } from '@/api/userApi';

export const userKeys = {
    all: ['user'],
    profile: () => [...userKeys.all, 'profile'],
    books: () => [...userKeys.all, 'books']
}

export const useCurrentUser = () => {
    return useQuery({
        queryKey: userKeys.profile(),
        queryFn: userApi.getCurrentUser,
        staletime: 10*60*1000
    })
}

export const useCreateUser = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: userApi.createUser,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: userKeys.all });
        }
    })
}