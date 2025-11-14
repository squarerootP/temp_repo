import NavBar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import Logo from '../components/common/Logo';
import DetailedBookCard from '../components/Book/DetailedBookCard';
import Books from '/src/data/books.json';
import SearchBar from '/src/components/layout/SearchBar.jsx';
import { Link } from 'react-router-dom';
import ChatBotToggleButton from '../components/layout/SideChatBot/ChatBotToggleButton';

function Book() {
  const BookList = [];
  return (
    <>
      <header>
        <NavBar></NavBar>
      </header>

      {/* The border between the header and the main parts */}
      <div className='border-2 border-white'></div>

      {/* The hero */}
      <section className='group relative h-[30vh] w-full overflow-hidden'>
        <div className="absolute inset-0 bg-[url('/src/assets/images/bg/books_bg.jpg')] bg-cover bg-center duration-300 group-hover:scale-105"></div>

        <div className='absolute inset-0 flex h-full items-center justify-between px-40'>
          <div className='flex flex-row'>
            <Logo size={69}></Logo>
            <h1 className='ml-4 text-6xl font-bold text-white shadow-slate-700'>Elib</h1>
          </div>
          <SearchBar></SearchBar>
        </div>
      </section>

      <main>
        {/* Here */}
        <section className='flex flex-col justify-center px-28'>
          <div className='flex flex-row py-5'>
            <Link className='text-md inline-block italic text-gray-500' to='/home'>
              Home {`>`}
            </Link>
            <Link className='text-md ml-4 inline-block font-semibold text-gray-900' to='/home'>
              Books
            </Link>
          </div>

          <div className='mt-5 flex justify-start gap-5 rounded-lg bg-green-200 py-2 pl-2'>
            <Logo size={30} mode='black'></Logo>
            <h1 className='text-xl font-semibold'>Featured Books</h1>
          </div>

          <div className='mt-2 border border-green-400'></div>

          <div></div>
          <div className='mb-60 mt-10 grid grid-cols-1 grid-rows-3 gap-6'>
            {Books.books.map((book, index) => (
              <DetailedBookCard
                key={index}
                img_path={book.img_path}
                book_title={book.book_title}
                author={book.author}
                summary={book.summary}
                published_year={book.published_year}
                rating={book.rating}
                genre={book.genre}
              />
            ))}
          </div>
        </section>
        {/* Feature */}
        {/* Content */}
      </main>
      <ChatBotToggleButton></ChatBotToggleButton>
      <footer>
        <Footer></Footer>
      </footer>
    </>
  );
}

export default Book;
