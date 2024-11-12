import React, { useState, useEffect } from 'react';
import axios from 'axios';
import styles from '../styles/Dashboard.module.css';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

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

  const [links, setLinks] = useState<Link[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [visibleLog, setVisibleLog] = useState<string | null>(null);
  const navigate = useNavigate();

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

      // Catch 404 error = user has no links

      .catch(() => {
        navigate('/login');
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

      // Catch 404 error = user has no logs

      .catch(() => {
        navigate('/login');
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

  return (
    <table id={styles.mainTable}>
      <thead>
        <tr style={{ border: '2px solid #ccc' }}>
          <th>Link</th>
          <th>Visits</th>
          <th>Redirect</th>
          <th>Expire Date</th>
        </tr>
      </thead>
      <tbody>
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
              <td>{link.expire_date}</td>
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
                      {/* Render logs only if visibleLog matches the link */}
                      {logs
                        .filter((log) => log.link === link.link)
                        .map((log, index, filteredLogs) => (
                          <tr key={log.id}>
                            <td>{filteredLogs.length - index}</td>
                            <td>{log.timestamp}</td>
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
                    </tbody>
                  </table>
                </td>
              </tr>
            )}
          </React.Fragment>
        ))}
      </tbody>
    </table>
  );
}

export default Dashboard;
