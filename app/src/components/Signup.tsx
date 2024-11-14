import { useState, FormEvent } from 'react';
import styles from '../styles/Auth.module.css';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from './Navbar';

function Signup() {
  document.title = 'LinkLogger | Signup';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);

    if (password !== passwordConfirm) {
      setPassword('');
      setPasswordConfirm('');
      return setError('Passwords do not match.');
    }

    try {
      const res = await axios.post(
        '/api/users/register',
        new URLSearchParams({
          username: username,
          password: password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      if (res.status === 200) {
        navigate('/login');
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const customErrorMessage = error.response?.data?.detail || null;
        setUsername('');
        setPassword('');
        setPasswordConfirm('');
        setError(customErrorMessage || 'An error occurred. Please try again.');
      } else {
        setUsername('');
        setPassword('');
        setPasswordConfirm('');
        setError('Unknown error. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className={styles.container}>
        <h1>Sign up</h1>
        <h2 className={error ? 'errorVisible' : 'errorHidden'}>{error}</h2>
        <hr></hr>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            minLength={8}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="confirm password"
            value={passwordConfirm}
            minLength={8}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            required
          />
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
        </form>
        <hr></hr>
        <p className={styles.footnote}>
          Already have an account?{' '}
          <Link to="/login" className={styles.footnoteLink}>
            Log in here.
          </Link>
        </p>
      </div>
    </>
  );
}

export default Signup;
