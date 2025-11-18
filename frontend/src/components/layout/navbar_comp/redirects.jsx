import '@/index.css'
import {Link} from 'react-router-dom'
function Redirects() {
    return (
        <div className='hidden md:flex flex-grow items-center justify-center space-x-10'>
          <Link to='/home' className='link_with_moving_underline'>
            Home
          </Link>
          <Link to='/books' className='link_with_moving_underline'>
            Books
          </Link>
          <Link to='/about' className='link_with_moving_underline'>
            About
          </Link>
          <Link to='/contact' className='link_with_moving_underline'>
            Contact
          </Link>
        </div>
    )
}

export default Redirects