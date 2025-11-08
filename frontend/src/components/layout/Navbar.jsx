import "@/index.css"
import { use, useState } from "react"
import Logo from "../common/Logo"
import { Link } from "react-router-dom"

function NavBar(){
    const [isMenuOpen, setIsMenuOpen] = useState(false)
    const [isLoggedin, setIsLoggedin] = useState(false)

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen)
    }

    return (
        <nav className="bg-green-500 p-4 shadow-lg">
            <div className="flex items-center justify-between max-w-7xl mx-auto flex-row" > 
                <Link to="/home" className="text-2xl font-bold text-white tracking-wider flex flex-row">
                    <Logo size={40}></Logo>E-Lib
                </Link> 
                
                <div className="hidden md:flex flex-grow items-center justify-center space-x-10"> 
                    <Link to="/home" className="text-white hover:text-green-200 transition duration-150">Home</Link>
                    <Link to="/books" className="text-white hover:text-green-200 transition duration-150">Books</Link>
                    <Link to="/about" className="text-white hover:text-green-200 transition duration-150">About</Link>
                    <Link to="/contact" className="text-white hover:text-green-200 transition duration-150">Contact</Link>
                </div>
                { !isLoggedin ? 
                <div className="hidden md:flex items-center space-x-4">
                    <Link to="/login" 
                     className="px-4 py-2 text-sm rounded text-white  hover:bg-white hover:text-green-600 transition duration-150">
                        Login
                    </Link>
                    <Link to="/signup" 
                    className="px-4 py-2 text-sm rounded bg-green-700 text-white hover:bg-green-800 transition duration-150">
                        Sign Up
                    </Link>
                </div>
                : <div className="rounded">
                    <p className="text-white">User</p>
                </div>
                }   
                
            </div>
        </nav>
    )
}

export default NavBar