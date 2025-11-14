import Logo from '../common/Logo';
import { Link } from 'react-router-dom';

function BookCard({ book_title, summary, img_path }) {
  const sub_path = '/books' + '/' + book_title.toLowerCase().replace(/ /g, '_') + '.html';

  return (
    <div className='w-60 h-90 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col px-4 py-4 justify-center'>
      <div className='flex items-center justify-center gap-2 w-full mb-2 space-x-2'>
        <Logo size={20} mode='b'></Logo>
        <h3 className='text-sm font-semibold text-gray-900 mb-2 text-center truncate w-full'>
          {book_title}
        </h3>
      </div>
      {/* <div className="border-2 border-green-900 w-[95%]"></div> */}

      <div className='items-center justify-between'>
        <img src={img_path} alt='' className='h-60 w-full overflow-hidden rounded-md' />
      </div>

      <Link
        to={sub_path}
        className='w-full mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition flex items-center justify-center'
      >
        Read
      </Link>
    </div>
  );
}
export default BookCard;
