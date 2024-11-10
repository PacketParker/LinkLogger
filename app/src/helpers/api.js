/**
 * Accept an API endpoint, method, and body to send to the API.
 *  - If successful, return the response
 *  - If not, return false
 * @param {*} endpoint API endpoint
 * @param {*} method String (GET, POST, PUT, DELETE)
 * @param {*} body Data to send to the API
 * @returns response.json or false
 */
async function accessAPI(endpoint, method, body) {
    let response = await fetch(`http://127.0.0.1:5252/api${endpoint}`, {
        method: method,
        credentials: 'include',
        body: body,
    });

    if (response.ok) {
        let data = await response.json();
        data = await data;
        return data;

    }

    return false;
}

export { accessAPI };