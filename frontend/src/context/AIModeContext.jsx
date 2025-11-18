import { createContext } from "react";
import { useState } from "react";

const AIModeContext = createContext()


export function AIModeProvider({children}) {
    const [aiMode, setAIMode] = useState(false)

    const toggleAIMode = () => {
        setAIMode(!aiMode)
    }

    return (
        <AIModeContext.Provider value={{aiMode, toggleAIMode}}>
            {children}
        </AIModeContext.Provider>
    )
}


