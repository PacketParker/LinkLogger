import React, { useState, useEffect, FormEvent } from 'react';
import axios from 'axios';
import styles from '../styles/Dashboard.module.css';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
import Navbar from './Navbar';

function Dashboard() {
  document.title = 'LinkLogger | Dashboard';

  interface Log {
    id: number;
    link: string;
    timestamp: string;
    ip: string;
    location: string;
    browser: string;
    os: string;
    userAgent: string;
    isp: string;
  }

  interface Link {
    link: string;
    owner: number;
    redirect_link: string;
    expire_date: string;
  }

  // Link creation states
  const [link, setLink] = useState('');
  const [url, setURL] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Log and link states
  const [links, setLinks] = useState<Link[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [visibleLog, setVisibleLog] = useState<string | null>(null);
  const [loadingLinks, setLoadingLinks] = useState<boolean>(true); // Track loading state for links
  const [loadingLogs, setLoadingLogs] = useState<boolean>(true); // Track loading state for logs
  const navigate = useNavigate();

  // Handle form submission to create a new link
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await axios.post('/api/links', { url });
      if (res.status === 200) {
        setLink(res.data.link);
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const customErrorMessage = error.response?.data?.error || null;
        setError(customErrorMessage || 'An error occurred. Please try again.');
        setIsSubmitting(false);
      } else {
        setError('Unknown error. Please try again.');
        setIsSubmitting(false);
      }
    }
  };

  // Copy the link to the clipboard
  const copyLink = () => {
    navigator.clipboard.writeText(`${window.location.origin}/c/${link}`);
    setIsCopied(true);
    // Wait 5 seconds, then set isCopied back to false
    setTimeout(() => {
      setIsCopied(false);
    }, 5000);
  };

  // Fetch links from API
  useEffect(() => {
    axios
      .get('/api/links')
      .then((res) => {
        if (res.status === 200) {
          setLinks(res.data);
        } else {
          navigate('/login');
        }
      })
      .catch((error: unknown) => {
        if (axios.isAxiosError(error)) {
          if (error.response?.status !== 404) {
            navigate('/login');
          }
        }
      })
      .finally(() => {
        setLoadingLinks(false); // Set loadingLinks to false once done
      });
  }, []);

  // Fetch logs from API
  useEffect(() => {
    axios
      .get('/api/logs')
      .then((res) => {
        if (res.status === 200) {
          setLogs(res.data);
        } else {
          navigate('/login');
        }
      })
      .catch((error: unknown) => {
        if (axios.isAxiosError(error)) {
          if (error.response?.status !== 404) {
            navigate('/login');
          }
        }
      })
      .finally(() => {
        setLoadingLogs(false); // Set loadingLogs to false once done
      });
  }, []);

  /**
   * Display or hide logs for a specific link
   * @param link The link to toggle logs for
   */
  const toggleLogRow = (link: string) => {
    setVisibleLog(visibleLog === link ? null : link);
  };

  /**
   * Delete a specific log
   * Gets the log ID from the SVG element's ID attribute
   * @param e The event object from the click
   * @returns void - updates state (setLogs) if successful
   */
  const deleteLog = (e: React.MouseEvent<SVGSVGElement>) => {
    const confirmDelete = confirm('Are you sure you want to delete this log?');
    if (!confirmDelete) return;

    const id = parseInt(e.currentTarget.id);
    axios
      .delete(`/api/logs/${id}`)
      .then((res) => {
        if (res.status === 200) {
          setLogs(logs.filter((log) => log.id !== id));
        }
      })
      .catch((error: unknown) => {
        if (axios.isAxiosError(error)) {
          // Return to login if we are unauthorized for some reason
          if (error.response?.status === 401) {
            navigate('/login');
          } else {
            alert('Failed to delete log. Please try again.');
          }
        }
      });
  };

  // Loading spinner component
  const LoadingSpinner = () => (
    <div className={styles.loadingSpinner}>
      <div className={styles.spinner}></div>
      <p>Loading...</p>
    </div>
  );

  return (
    <>
      <Navbar />

      <div className={styles.createContainer}>
        <h1>Create a new short link by entering the long URL below</h1>
        <form onSubmit={handleSubmit}>
          <input
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
        <p className={error ? styles.errorVisible : styles.errorHidden}>
          {error}
        </p>
      </div>

      {/* Show loading spinner if either links or logs are still loading */}
      {loadingLinks || loadingLogs ? (
        <LoadingSpinner />
      ) : (
        <table className={styles.mainTable}>
          <thead>
            <tr style={{ border: '2px solid #ccc' }}>
              <th>Link</th>
              <th>Visits</th>
              <th>Redirect</th>
              <th>Expire Date</th>
            </tr>
          </thead>
          <tbody>
            {/* If there are no links, put a special message */}
            {links.length === 0 && (
              <tr>
                <td colSpan={4}>
                  <div className={styles.noLinks}>
                    You do not have any shortened links, create one above.
                  </div>
                </td>
              </tr>
            )}

            {/* For every link and its logs */}
            {links.map((link) => (
              <React.Fragment key={link.link}>
                <tr className={styles.linkTableRow}>
                  <td>
                    <button
                      onClick={() => toggleLogRow(link.link)}
                      className={styles.linkButton}
                    >
                      {link.link}
                    </button>
                  </td>
                  <td>
                    {logs.filter((log) => log.link === link.link).length || 0}
                  </td>
                  <td>{link.redirect_link}</td>
                  <td>{new Date(link.expire_date).toLocaleDateString()}</td>
                </tr>

                {/* Conditionally render logs for this link */}
                {visibleLog === link.link && (
                  <tr className={styles.logTableRow}>
                    <td colSpan={6}>
                      <table>
                        <thead>
                          <tr>
                            <th>ID</th>
                            <th>Timestamp</th>
                            <th>IP</th>
                            <th>Location</th>
                            <th colSpan={2}>ISP</th>
                          </tr>
                        </thead>
                        <tbody>
                          {/* Render all logs for the link */}
                          {logs
                            .filter((log) => log.link === link.link)
                            .map((log, index, filteredLogs) => (
                              <tr key={log.id}>
                                <td>{filteredLogs.length - index}</td>
                                <td>
                                  {new Date(
                                    log.timestamp
                                  ).toLocaleTimeString() +
                                    ', ' +
                                    new Date(
                                      log.timestamp
                                    ).toLocaleDateString()}
                                </td>
                                <td>{log.ip}</td>
                                <td>{log.location}</td>
                                <td>{log.isp}</td>
                                <td>
                                  <FontAwesomeIcon
                                    icon={faTrash}
                                    className={styles.trashBin}
                                    id={log.id.toString()}
                                    onClick={deleteLog}
                                  />
                                </td>
                              </tr>
                            ))}
                          {/* If the link has no logs, put a special message */}
                          {logs.filter((log) => log.link === link.link)
                            .length === 0 && (
                            <tr>
                              <td colSpan={6}>
                                <div className={styles.noLogs}>
                                  No logs for this link
                                </div>
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

export default Dashboard;
