import { useState, FormEvent, useEffect } from 'react';
import createStyles from '../styles/Create.module.css';
import styles from '../styles/Auth.module.css';
import { Link } from 'react-router-dom';
import axios from 'axios';
import Navbar from './Navbar';
import { useNavigate } from 'react-router-dom';

function CreateLink() {
  document.title = 'LinkLogger | Create Short Link';

  const [link, setLink] = useState('');
  const [url, setURL] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Get /api/users/me to make sure the user is logged in, and
  // to get the username for rendering on screen
  useEffect(() => {
    axios
      .get('/api/users/me')
      .then((res) => {
        if (res.status != 200) {
          navigate('/login');
        }
      })
      .catch(() => {
        navigate('/login');
      });
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await axios.post('/api/links', { url });
      if (res.status === 200) {
        setLink(res.data.link);
      }
    } catch (error) {
      setError('STRANGE');
    }
  };

  const copyLink = () => {
    navigator.clipboard.writeText(`${window.location.origin}/c/${link}`);
    setIsCopied(true);
    // Wait 5 seconds, then set isCopied back to false
    setTimeout(() => {
      setIsCopied(false);
    }, 5000);
  };

  return (
    <>
      <Navbar />
      <div className={styles.container}>
        <h1>Create a new short link by entering the long URL below</h1>
        <p className={error ? styles.errorVisible : styles.errorHidden}>
          {error}
        </p>
        <hr></hr>
        <form onSubmit={handleSubmit}>
          <input
            className={createStyles.createInput}
            type="text"
            placeholder="Full URL"
            value={url}
            onChange={(e) => setURL(e.target.value)}
            required
          />
          {link.length === 0 ? (
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create'}
            </button>
          ) : (
            <button type="button" onClick={copyLink}>
              {isCopied ? (
                <em>Copied!</em>
              ) : (
                `Click to copy: ${window.location.origin}/c/${link}`
              )}
            </button>
          )}
        </form>
        <hr></hr>
        <p className={styles.footnote}>
          <Link to="/dashboard" className={styles.footnoteLink}>
            Click here
          </Link>{' '}
          to visit your dashboard.
        </p>
      </div>
    </>
  );
}

export default CreateLink;
