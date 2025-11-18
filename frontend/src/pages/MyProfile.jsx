import { useState, useEffect } from 'react';
import NavBar from '../components/layout/Navbar';
import '@/index.css';
import { userApi } from '../api/userApi';
import { SubmitButton } from '@components/forms/SubmitButton.jsx';
import UserCard from '../components/my_profile/UserCard';
import Logo from '../components/common/Logo.jsx';
import BadgeCard from '../components/my_profile/BadgeCard.jsx';
function MyProfile() {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await userApi.getCurrentUser();
        setUserData(response); // adjust if response.data is needed
      } catch (err) {
        console.error('Error fetching user data:', err);
        setError('Failed to load user data');
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  return (
    <div>
      <header>
        <NavBar />
        <div className='border-2 border-white'></div>
      </header>
      {/*  main container */}
      <section className='flex gap-x-10 md:gap-x-20 items-center justify-center p-10 bg-green-200'>
        {/* left side bar */}
        <div
          className='hidden md:flex flex-col h-[300px] min-w-[30vh] bg-green-50 shadow-md rounded-xl ring-green-200 ring-2 
            justify-center items-center'
        >
          <h1>Hello</h1>
        </div>
        {/* The right side detailed card*/}
        <div
          className='flex flex-1 h-[70vh] bg-green-600 rounded-xl ring-green-600 ring-2 ring-offset-[3px]
           mr-20 p-10 gap-x-[5%]'
        >
          {/* Left side user profile */}
          {userData && <UserCard userData={userData}></UserCard>}
          {/* Right sides badges and bla bla bla */}
          <div className='flex flex-1 flex-col items-center gap-y-10 '>
            <h2 className='font-bold text-2xl text-white'>Badges</h2>
            {/* Scrollable container */}
            <div className='h-96 overflow-y-auto w-full px-4'>
              <div className='grid grid-cols-2 md:grid-cols-3 place-items-center gap-10'>
                <BadgeCard img_path='/images/badges/badge_1.png' title='Badge 1' />
                <BadgeCard img_path='/images/badges/badge_2.png' title='Badge 2' />
                <BadgeCard img_path='/images/badges/badge_3.png' title='Badge 3' />
                <BadgeCard img_path='/images/badges/badge_4.png' title='Badge 4' />
                {/* Add more badges to test scrolling */}
                <BadgeCard img_path='/images/badges/badge_1.png' title='Badge 5' />
                <BadgeCard img_path='/images/badges/badge_2.png' title='Badge 6' />
                <BadgeCard img_path='/images/badges/badge_3.png' title='Badge 7' />
                <BadgeCard img_path='/images/badges/badge_4.png' title='Badge 8' />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default MyProfile;
