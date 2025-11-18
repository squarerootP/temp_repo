import '@/index.css';
import { useState } from 'react';
import Redirects from './navbar_comp/redirects.jsx';
import UserArea from './navbar_comp/user_area.jsx';
import NavBarAppLogo from './navbar_comp/logo.jsx';
function NavBar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // const toggleMenu = () => {
  //   setIsMenuOpen(!isMenuOpen);
  // };

  return (
    <nav className='bg-primary py-2 shadow-lg max-h-16'>
      <div className='flex items-center justify-between max-w-7xl mx-auto'>
        <NavBarAppLogo></NavBarAppLogo>
        <Redirects></Redirects>
        <UserArea></UserArea>
      </div>
    </nav>
  );
}

export default NavBar;
