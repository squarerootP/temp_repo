import { useContext } from 'react';
import { Navigate } from "react-router-dom";

import {AuthContext} from  '/src/context/AuthContext.jsx'
export const ProtectedRoute = ({children}) => {
    const { user, loading} = useContext(AuthContext)

    if (loading) return <div>Loading...</div>
    // if (!user) return <Navigate to="/login" replace></Navigate>

    return children
}