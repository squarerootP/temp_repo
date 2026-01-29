import { useState } from 'react';
import { useContext } from 'react';
import { AuthContext } from '../../../context/AuthContext';
import { Link } from 'react-router-dom';
function UserArea() {
  const [isOpen, setIsOpen] = useState(false);
  const { isLoggedIn, logout } = useContext(AuthContext);

  const [curColorMode, setCurColorMode] = useState('light');
  const handleClick = () => {
    setIsOpen(!isOpen);
  };
  const switchColorMode = (e) => {
    // Implement color mode switching logic here
  };
  return (
    <div className='relative'>
      {!isLoggedIn ? (
        <div className='hidden md:flex items-center space-x-4'>
          <Link
            to='/login'
            className='px-4 py-2 text-sm rounded-sm text-white  hover:bg-white hover:text-green-600 transition duration-150'
          >
            Login
          </Link>
          <Link
            to='/signup'
            className='px-4 py-2 text-sm rounded-sm bg-green-700 text-white hover:bg-green-800 transition duration-150'
          >
            Sign Up
          </Link>
        </div>
      ) : (
        <button
          className='flex rounded-full ring-2 ring-offset-white ring-offset-2 border-2 border-green-600  bg-white 
            size-10 justify-center items-center overflow-hidden'
          onClick={(e) => handleClick(e)}
        >
          <img src='/images/user_images/boy.png' alt='' />
        </button>
      )}
      {isOpen && isLoggedIn && (
        <div
          className='absolute z-500 grid grid-cols-1 border-2 border-green-600 divide-y-2 divide-green-60 
            place-items-center w-36 bg-white rounded-md'
        >
          <Link to='/my-profile/'>View profile</Link>
          <button onClick={(e) => switchColorMode(e)}>Toggle {curColorMode == "light" ? "dark" : "light"} mode</button>
          <button onClick={(e) => logout(e)}>Logout</button>
        </div>
      )}
    </div>
  );
}

export default UserArea;
