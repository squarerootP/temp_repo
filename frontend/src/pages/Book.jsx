import NavBar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import Logo from '../components/common/Logo';
import DetailedBookCard from '../components/Book/DetailedBookCard';
// import Books from '/src/data/books.json';
import SearchBar from '/src/components/layout/SearchBar.jsx';
import { Link } from 'react-router-dom';
import ChatBotToggleButton from '../components/layout/SideChatBot/ChatBotToggleButton';
import { useBooks, useSearchBooks } from '@/hooks/useBooks';
import { useState, useSyncExternalStore } from 'react';
import { AIModeProvider } from '@/context/AIModeContext';
import { useAIMode } from '@/context/AIModeContext';
import { useEffect } from 'react';

export default function Book() {
  const [page, setPage] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const { aiMode, toggleAIMode } = useAIMode();
  const ITEMS_PER_PAGE = 4;

  const { data: searchResults, isLoading: isSearching } = useSearchBooks({ query: searchQuery });
  const {
    data: paginatedBooks,
    isLoading: isLoadingBooks,
    error,
    isFetching,
  } = useBooks({
    skip: page * ITEMS_PER_PAGE,
    limit: ITEMS_PER_PAGE,

  });

  const books = searchQuery ? searchResults : paginatedBooks;
  const bookCount = 20
  const isLoading = searchQuery ? isSearching : isLoadingBooks;

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div> Error: {error.message}</div>;

  function handleSearch(query) {
    if (aiMode) {
      console.log('AI searching:', query);
    } else {
      console.log('Normal searching: ', query);
      setSearchQuery(query);
    }
  }
  for (let i = 0; i < books.length; i++) {
    console.log('Book', i, books[i]);
  }
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
          <div className='flex-row hidden md:flex'>
            <Logo size={69}></Logo>
            <h1 className='ml-4 text-6xl font-bold text-white shadow-slate-700'>Elib</h1>
          </div>
          <SearchBar onSearch={(e) => handleSearch(e.mode)}></SearchBar>
        </div>
      </section>

      <main>
        {/* Here */}
        <section className='flex flex-col justify-center px-28'>
          <div className='flex flex-row py-5'>
            <Link className='text-md flex italic text-gray-500' to='/home'>
              Home <span className='flex'>{'>'}</span>
            </Link>
            <Link className='text-md ml-4 flex font-semibold text-gray-900' to=''>
              Books
            </Link>
          </div>

          <div className='mt-5 flex min-w-[250px] justify-start gap-5 rounded-lg bg-green-200 py-2 pl-2'>
            <Logo size={30} mode='black'></Logo>
            <h1 className='text-xl font-semibold'>Featured Books</h1>
          </div>

          <div className='mt-2 min-w-[250px] border border-green-400'></div>

          <div></div>
          <div className='mb-10 mt-10 grid grid-cols-1 grid-rows-3 gap-6'>
            {books?.map((book, index) => (
              <DetailedBookCard
                key={index}
                img_path={book.img_path.trim()}
                book_title={book.title}
                author={book.author_name}
                summary={book.summary}
                published_year={book.published_year}
                rating={book.rating}
                genre={book.genre}
              />
            ))}
          </div>
        </section>
        {/* Book page navigation */}
        <section>
          <div className='hidden md:flex justify-center space-x-4 pb-10'>
            {Array.from({ length: Math.ceil(bookCount / ITEMS_PER_PAGE) }, (_, i) => (
              <button
                key={i}
                onClick={() => setPage(i)}
                className={`px-4 py-2 rounded ${
                  page === i ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </section>
      </main>
      <ChatBotToggleButton></ChatBotToggleButton>
      <footer>
        <Footer></Footer>
      </footer>
    </>
  );
}

