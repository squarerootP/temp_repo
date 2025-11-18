import '@/index.css';
function UserCard({ userData }) {
  return (
    <div className='relative flex flex-col rounded-xl bg-white w-80 h-full overflow-hidden border-2 border-white items-center'>
      <img
        src='/images/user_images/dinosaur.png'
        alt=''
        className='size-40 rounded-full shink-0 mt-10 border-green-400  bg-white border-[3px] absolute z-10'
      />
      <div className='relative h-[50%] bg-white w-full'>
        <button className='absolute right-[10%] top-[10%]'>
          <img src='/images/icons/settings.png' alt='' className='size-8 shrink-0 '  />
        </button>
      </div>
      <div className=' bg-green-600 w-full h-full'>
        {/* user info fields */}
        <div className='h-[30%]'></div>
        <div className='flex flex-col h-[70%] px-[10%] text-white font-semibold gap-y-4'>
          <p>
            <strong>Username:</strong> {userData.user_name}
          </p>
          <p>
            <strong>Name:</strong> {userData.first_name} {userData.second_name}
          </p>
          <p>
            <strong>Email:</strong> {userData.email}
          </p>
          <p>
            <strong>Phone:</strong> {userData.phone}
          </p>
        </div>
      </div>
    </div>
  );
}

export default UserCard;
