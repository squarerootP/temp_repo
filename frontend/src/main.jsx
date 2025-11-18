import React from 'react';
import ReactDOM from 'react-dom/client';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import { BrowserRouter, Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import LandingPage from '@pages/LandingPage';
import Book from '@pages/Book';
import MyProfile from '@pages/MyProfile';
import { AIModeProvider } from './context/AIModeContext';
import { AppProvider } from './context/AppContext';
function App() {
  return (
    <div>
      <AppProvider>
        <AIModeProvider>
          <AuthProvider>
            <BrowserRouter>
              <Routes>
                <Route path='/' element={<LandingPage />} />
                <Route path='/login' element={<Login />} />
                <Route path='/signup' element={<SignUp />} />
                <Route path='/home' element={<Home />} />
                <Route path='/books' element={<Book />} />
                <Route path='/my-profile' element={<MyProfile />} />
              </Routes>
            </BrowserRouter>
          </AuthProvider>
        </AIModeProvider>
      </AppProvider>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
