import styles from '../styles/Navbar.module.css';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <div className={styles.navbar}>
      <div className={styles.navbarLeft}>
        <Link to={'/login'}>
          <a className={styles.navbarLink}>Login</a>
        </Link>
        <Link to={'/signup'}>
          <a className={styles.navbarLink}>Signup</a>
        </Link>
      </div>
      <div className={styles.navbarRight}>
        <Link to={'/status'}>
          <a className={styles.navbarLink}>API Status</a>
        </Link>
      </div>
    </div>
  );
}

export default Navbar;
