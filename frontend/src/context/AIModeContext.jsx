import { createContext } from 'react';
import { useState } from 'react';
import {useContext} from 'react'

const AIModeContext = createContext();

export function AIModeProvider({ children }) {
  const [aiMode, setAIMode] = useState(false);

  const toggleAIMode = () => {
    setAIMode(!aiMode);
  };

  return (
    <AIModeContext.Provider value={{ aiMode, toggleAIMode }}>{children}</AIModeContext.Provider>
  );
}

export function useAIMode() {
    const context = useContext(AIModeContext)
    if (!context) {
        throw new Error('useAIMode must be used within AIModeProvider')
    }
    return context
}