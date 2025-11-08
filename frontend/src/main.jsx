import React from 'react'
import ReactDOM from 'react-dom/client'
import { AuthProvider } from "./context/AuthContext";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import { BrowserRouter, Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import LandingPage from '@pages/LandingPage'

function App(){
  return (
    <div>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp/>} />
            <Route path="/home" element={<Home/>} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)