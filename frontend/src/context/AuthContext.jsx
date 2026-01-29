import { createContext, useState, useEffect } from 'react';

import { getToken, saveToken, removeToken } from '../services/tokenService';
import {userApi} from '../api/userApi'
export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(getToken());
  const [isLoading, setIsLoading] = useState(true)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  const login = (userData, token) => {
    setUser(userData);
    setToken(token);
    setIsLoggedIn(true)
    saveToken(token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setIsLoggedIn(false)
    removeToken();
  };

  useEffect(() => {
    const initalizeAuth = async () => {
      const storedToken = getToken()

      if (storedToken) {
        try {
          const userData = await userApi.getCurrentUser()
          setUser(userData)
          setIsLoggedIn(true)
          setToken(storedToken)
        }
        catch (error) {
          console.error("Failed to fetch user data:", error)
          removeToken()
          setToken(null)
          setUser(null)
          setIsLoggedIn(false)
        }
      }
      setIsLoading(false)
    }
    initalizeAuth()
  }, [])

  useEffect(() => {
    setIsLoggedIn(!!user && !!token)
  }, [token, user])

  const value = {
    user, token, isLoggedIn, isLoading, login, logout
  }
  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}
