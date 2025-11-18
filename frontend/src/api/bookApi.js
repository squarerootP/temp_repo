mport apiClient from './axiosConfig';

export const bookApi = {
  // Get all books
  getAllBooks: async (skip = 0, limit = 100) => {
    const response = await apiClient.get(`/books?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Search books
  searchBooks: async (query, skip = 0, limit = 100) => {
    const response = await apiClient.get(`/books/search?text_to_search=${query}&skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get book by ISBN
  getBookByIsbn: async (isbn) => {
    const response = await apiClient.get(`/books/${isbn}`);
    return response.data;
  },

  // Add book (admin only)
  addBook: async (bookData) => {
    const response = await apiClient.post('/books/', bookData);
    return response.data;
  },

  // Update book (admin only)
  updateBook: async (isbn, bookData) => {
    const response = await apiClient.put(`/books/${isbn}`, bookData);
    return response.data;
  },

  // Delete book (admin only)
  deleteBook: async (isbn) => {
    const response = await apiClient.delete(`/books/${isbn}`);
    return response.data;
  },
};