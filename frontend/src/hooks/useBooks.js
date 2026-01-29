import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { bookApi } from "@/api/bookApi";

export const bookKeys = {
    all: ["books"],
    lists: () => [...bookKeys.all, "list"],
    list: (filters) => [...bookKeys.lists(), { filters }],
    details: () => [...bookKeys.all, "detail"],
    detail: (isbn) => [...bookKeys.details(), isbn],
}

export const useBooks =({skip=0, limit=100} = {}) => {
    return useQuery({
        queryKey: bookKeys.list({skip, limit}),
        queryFn: () => bookApi.getAllBooks({skip, limit}),
        keepPreviousData: true,
    })
}


export const useSearchBooks =({query, skip=0, limit=100}={}) => {
    return useQuery({
        queryKey: bookKeys.list({skip, limit, query}),
        queryFn: () => bookApi.searchBooks({query, skip, limit}),
        enabled: !!query && query.length > 2,
        staleTime: 30*1000,
    })
}

export const useBook = (isbn) => {
    return useQuery({
        queryKey: bookKeys.detail(isbn),
        queryFn: () => bookApi.getBookByIsbn(isbn),
        enabled: !!isbn
    })
}

