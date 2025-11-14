import { loginApi } from '@/api/authApi';
import { FormField } from '@/components/forms/FormField.jsx';
import { SubmitButton } from '@/components/forms/SubmitButton.jsx';
import { AuthContext } from '@/context/AuthContext';
import '@/index.css';
import { styles } from '@/styles/style_config.jsx';
import { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Login() {
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const data = await loginApi(email, password);
      login(data.user, data.access_token);
      navigate('/home');
    } catch (err) {
      setError('Invalid crendentials');
      navigate('/home');
    }
  };

  return (
    <div className={styles.main_bg}>
      <div className={styles.form_bg}>
        <h2 className={styles.main_form_header}>Login to your account</h2>
        <form onSubmit={handleSubmit} className='space-y-5'>
          <FormField
            label='Email'
            type='email'
            placeholder='you@example.com'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required={true}
          />
          <FormField
            label='Password'
            type='password'
            placeholder='***ehe'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required={true}
          />
          <SubmitButton text='Login' />

          {error && <p className='text-red-500'>{error}</p>}
        </form>
        <p className='text-sm text-center mt-4 '>
          Don't have an account?{' '}
          <Link to='/signup' className='text-green-600 hover:underline'>
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
export default Login;
