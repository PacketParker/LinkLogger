import React, { useState, useEffect } from 'react';
import Axios from 'axios';
import styles from '../styles/Dashboard.module.css';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

function Dashboard() {
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
        Axios.get('/api/links').then((res) => {
            if (res.status === 200) {
                setLinks(res.data);
            } else {
                navigate('/login');
            }
        }).catch(() => {
            navigate('/login');
        });
    }, []);

    // Fetch logs from API
    useEffect(() => {
        Axios.get('/api/logs').then((res) => {
            if (res.status === 200) {
                setLogs(res.data);
            } else {
                navigate('/login');
            }
        }).catch(() => {
            navigate('/login');
        });
    }, []);


    const toggleLogRow = (link: string) => {
        setVisibleLog(visibleLog === link ? null : link);
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
                                <button onClick={() => toggleLogRow(link.link)} className={styles.linkButton}>{link.link}</button>
                            </td>
                            <td>{logs.filter((log) => log.link === link.link).length || 0}</td>
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
                                                        <td><FontAwesomeIcon icon={faTrash} className={styles.trashBin}/></td>
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
    )
}

export default Dashboard;