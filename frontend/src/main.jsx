import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import LandingPage from '@pages/LandingPage';
import Book from '@pages/Book';
import MyProfile from '@pages/MyProfile';
import { AIModeProvider } from './context/AIModeContext';
import { AppProvider } from './context/AppContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Data is fresh for 5 minutes
      cacheTime: 10 * 60 * 1000, // Cache persists for 10 minutes
      refetchOnWindowFocus: false, // Don't refetch on tab focus
      retry: 1, // Retry failed requests once
      refetchOnMount: true, // Refetch when component mounts
    },
    mutations: {
      retry: 0, // Don't retry mutations
    },
  },
});

function App() {
  return (
    <div>
      <QueryClientProvider client={queryClient}>
        <AppProvider>
          <AIModeProvider>
            <AuthProvider>
              <BrowserRouter>
                <Routes>
                  <Route path='/' element={<LandingPage />} />
                  <Route path='/login' element={<Login />} />
                  <Route path='/signup' element={<SignUp />} />
                  <Route
                    path='/home'
                    element={
                      <ProtectedRoute>
                        <Home />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path='/books'
                    element={
                      <ProtectedRoute>
                        <Book />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path='/my-profile'
                    element={
                      <ProtectedRoute>
                        <MyProfile />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/test"
                    element={
                      <MainLayout/>
                    }
                    />
                </Routes>
              </BrowserRouter>
            </AuthProvider>
          </AIModeProvider>
        </AppProvider>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
