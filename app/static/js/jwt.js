// Description: This file contains functions to access the API with JWT authentication.

/**
 * Accept a full URL, method, and body to send to the API.
 *  - If successful, return the response
 *  - If first fail, attempt to refresh JWT token and try again
 *  - If second fail, return false
 * @param {*} endpoint API endpoint
 * @param {*} method String (GET, POST, PUT, DELETE)
 * @param {*} body Data to send to the API
 * @returns boolean
 */
async function accessAPI(endpoint, method, body) {
    let response = await fetch(`/api${endpoint}`, {
        method: method,
        body: body,
    });

    if (response.ok) {
        let data = await response.json();
        data = await data;
        console.log(data);
        return data;
    } else if (response.status === 401) {
        console.log('REFRESHING TOKEN')
        if (await refreshAccessToken()) {
            // Try the request again
            let response = await fetch(`/api${endpoint}`, {
                method: method,
                body: body,
            });
            if (response.ok) {
                let data = await response.json();
                data = await data;
                console.log("REFRESHED DATA")
                return data;
            }
        }
    }
    return false;
}

/**
 * Attempt to refresh the JWT token
 * @returns boolean
 */
async function refreshAccessToken () {
    const response = await fetch('/api/auth/refresh', {
        method: 'POST',
    });
    if (response.ok) {
        console.log("TOKEN REFRESH")
        return true;
    } else {
        console.log("TOKEN REFRESH FAILED")
        return false;
    }
}