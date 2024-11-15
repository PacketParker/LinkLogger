import { useState, useEffect } from 'react';
import styles from '../styles/Navbar.module.css';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCircleUp, faCircleDown } from '@fortawesome/free-solid-svg-icons';

function Navbar() {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAPIStatus = async () => {
      try {
        const res = await fetch('/api/ping');

        if (res.status === 200) {
          setIsOnline(true);
        } else {
          setIsOnline(false);
        }
      } catch (error) {
        setIsOnline(false);
      }
    };

    checkAPIStatus();
  }, []);

  return (
    <div className={styles.navbar}>
      <div className={styles.left}>
        <Link to={'/login'}>
          <a className={styles.link}>Login</a>
        </Link>
        <Link to={'/signup'}>
          <a className={styles.link}>Signup</a>
        </Link>
      </div>
      <div className={styles.right}>
        <a
          className={styles.link}
          title={
            isOnline === null
              ? 'Loading...'
              : isOnline
              ? 'API is online'
              : 'API is offline'
          }
        >
          API Status:{' '}
          {isOnline === null ? (
            'Loading...'
          ) : isOnline ? (
            <FontAwesomeIcon icon={faCircleUp} className={styles.circleUp} />
          ) : (
            <FontAwesomeIcon
              icon={faCircleDown}
              className={styles.circleDown}
            />
          )}
        </a>
      </div>
    </div>
  );
}

export default Navbar;
