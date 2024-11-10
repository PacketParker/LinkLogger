// Description: This file contains functions to access the API with JWT authentication.

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
    let response = await fetch(`/api${endpoint}`, {
        method: method,
        body: body,
    });

    if (response.ok) {
        let data = await response.json();
        data = await data;
        return data;

    }

    return false;
}