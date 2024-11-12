import { useState, FormEvent } from 'react';
import styles from '../styles/Login.module.css';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Login() {
  document.title = 'LinkLogger | Login';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await axios.post(
        '/api/auth/token',
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
        navigate('/dashboard');
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const customErrorMessage = error.response?.data?.detail || null;
        setPassword('');
        setError(customErrorMessage || 'An error occurred. Please try again.');
      } else {
        setPassword('');
        setError('Unknown error. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div id={styles.container}>
      <p id={styles.loginText}>Log In</p>
      <p id={styles.error} className={error ? 'visible' : 'hidden'}>
        {error}
      </p>
      <div>
        <header>
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
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </button>
          </form>
          <hr></hr>
          <p id={styles.bottomText}>
            Don't have an account?{' '}
            <Link to="/signup" className={styles.link}>
              Create one now
            </Link>
          </p>
        </header>
      </div>
    </div>
  );
}

export default Login;
