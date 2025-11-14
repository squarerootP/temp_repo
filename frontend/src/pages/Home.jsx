import { styles } from '../styles/style_config.jsx';
import NavBar from '../components/layout/Navbar.jsx';
import Footer from '../components/layout/Footer.jsx';
import BookCard from '../components/Book/BookCard.jsx';
import Logo from '../components/common/Logo.jsx';
import '@/index.css';
import SearchBar from '../components/layout/SearchBar.jsx';
import ChatBotToggleButton from '../components/layout/SideChatBot/ChatBotToggleButton.jsx';
import Books from '/src/data/books.json';

function Home() {
  const maxBooksToShow = 5; // Limit the number of books to show
  return (
    <>
      <header>
        <NavBar></NavBar>
      </header>

      {/* The line that separates the nav and the main body */}
      <div className='border-2 border-white'></div>

      {/* First div - currently the main div*/}
      <div className='group relative mx-auto flex min-h-screen w-[calc(90vw)] items-center justify-center space-y-28 overflow-hidden'>
        <div className="absolute inset-0 bg-[url('src/assets/images/bg/home_bg_3.jpg')] bg-cover bg-center transition-transform duration-500 group-hover:scale-105"></div>

        {/* The content over the background */}
        <div className='relative z-10 mx-auto flex flex-col items-center justify-center space-y-8 p-6'>
          <div className='h-8'></div>
          <Logo size={260} />
          <SearchBar />
          <h1 className='text-outline text-4xl font-bold text-white'>Choose what to read today</h1>
          <div className='h-12'></div>

          {/* This show books horizontally */}
          <div className='flex flex-row space-x-8'>
            {Books.books.slice(0, maxBooksToShow).map((book, index) => (
              <BookCard
                key={index}
                book_title={book.book_title}
                img_path={book.img_path}
              ></BookCard>
            ))}
          </div>
          <div className='h-40'></div>
        </div>
      </div>

      <ChatBotToggleButton />
      <div className='border-2 border-white'></div>

      {/* The footer */}
      <Footer></Footer>
    </>
  );
}

export default Home;
