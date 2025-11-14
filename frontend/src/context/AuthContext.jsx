import { createContext, useState, useEffect } from 'react';

import { getToken, saveToken, removeToken } from '../services/tokenService';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(getToken());

  const login = (userData, token) => {
    setUser(userData);
    setToken(token);
    saveToken(token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    removeToken();
  };

  useEffect(() => {
    if (token) {
    }
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>
  );
}
