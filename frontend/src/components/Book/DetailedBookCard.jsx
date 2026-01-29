import { Link } from 'react-router-dom';
import { FaStar } from 'react-icons/fa';
import genres from '../../data/genre_icon_mapper.json';

function DetailedBookCard({
  img_path,
  book_title,
  author,
  summary,
  published_year,
  rating,
  genre,
}) {
  const sub_path = '/books' + '/' + book_title.toLowerCase().replace(/ /g, '_') + '.html';

  return (
    <div
      className='flex p-3 bg-green-50 rounded-xl hover:bg-green-100 border-l-2 border-b-2 
    group
    border-green-500 justify-between min-w-[250px]'
    >
      {/* Images + book meta data - left side */}
      <div className='flex gap-3 md:gap-5 max-w-[80%]'>
        {/* Image */}
        <div className='hidden md:flex w-24 h-full shrink-0 overflow-hidden'>
          <img className='w-full h-full object-cover' src={img_path} alt='detailed_book_card' />
        </div>
        {/* content */}
        <div className='flex flex-col '>
          <div className='flex space-x-5'>
            <h2 className='text-base font-bold text-green-900 '>{book_title}</h2>
            <div className='hidden md:flex mt-1'>
              {[...Array(rating)].map((_, i) => (
                <FaStar key={i} className='text-yellow-500' />
              ))}
            </div>
          </div>
          {/* <h2 className="text-base font-bold text-green-900 ">{book_title}</h2>
                    <span>Hello</span> */}
          <h3 className='text-sm italic text-green-700'>by {author}</h3>
          <p className=' text-sm italic'>{published_year}</p>
          <div className='relative max-h-20 overflow-hidden'>
            <p className='text-sm'>{summary}</p>
            <div className='absolute bottom-0 left-0 right-0 h-6 bg-linear-to-t from-green-50 to-transparent group-hover:from-green-100'></div>
          </div>
          <Link className='italic underline inline-block  text-green-800 mt-4' to={sub_path}>
            Learn more
          </Link>
        </div>
      </div>

      {/* genre and languages */}
      <div className='hidden md:grid grid-cols-2 w-24 text-center mt-1'>
        <div className='rounded-sm bg-green-200 w-[90%] h-10 p-2'>
          <img
            src={genres.genres.find((g) => g.genre === genre)?.img_path}
            alt={genre}
            className='w-full h-full object-contain'
          />
        </div>
        <div className='rounded-sm bg-green-200 w-[90%] h-10 p-2'>
          <img
            src='/images/book_language_icons/english.png'
            alt='language'
            className='w-full h-full object-contain'
          />
        </div>
      </div>
    </div>
  );
}
export default DetailedBookCard;
