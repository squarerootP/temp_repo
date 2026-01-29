import '@/index.css'
import {Link} from 'react-router-dom'
import Logo from '/src/components/common/Logo';

function NavBarAppLogo() {
    return (
        <Link to='/home' className='hidden sm:flex items-center text-2xl font-bold text-white tracking-wider gap-x-2'>
          <Logo size={40}></Logo> <span className=''>E-lib</span>
        </Link>
    )
}

export default NavBarAppLogo;