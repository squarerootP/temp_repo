import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { ragApi } from '@/api/ragApi';

export const chatKeys = {
    all: ['chat'],
    sessions: () => {
        [...chatKeys.all, 'sessions']
    }
};


export const useChatSessions = () => {
    return useQuery({
        queryKey: chatKeys.sessions(),
        queryFn: ragApi.getSessions,
    })
}

export const useSendMessage = () =>{
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ragApi.sendMessage,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: chatKeys.sessions() });
        }
    })
}

export const useUploadDocument = () => {
    return useMutation ({
        mutationFn: ragApi.uploadDocument
    })
}

