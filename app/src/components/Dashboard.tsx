import { useState, useEffect } from 'react';
import Axios from 'axios';
import styles from '../styles/Dashboard.module.css';
// import { accessAPI } from '../helpers/api';


function Dashboard() {
    // Get the links from the API
    const [links, setLinks] = useState([]);
    useEffect(() => {
        Axios.get('/api/links')
            .then((res) => {
                setLinks(res.data);
            })
            .catch((err) => {
                console.log(err);
            });
    }, []);


    return (
        <div id={styles.container}>
            <table>
                <thead>
                    <tr style={{ border: '2px solid #ccc' }}>
                        <th>Link</th>
                        <th>Visits</th>
                        <th>Redirect</th>
                        <th>Expire Date</th>
                    </tr>
                </thead>
                <tbody>
                    {/* {links.map((link: any) => (
                        <tr key={link.id}>
                            <td>{link.url}</td>
                            <td>{link.visits}</td>
                            <td>{link.redirect}</td>
                            <td>{link.expire_date}</td>
                        </tr>
                    ))} */}
                </tbody>
            </table>
        </div>
    )
}

export default Dashboard;