const API_BASE_URL = './api';

const api = {
    async request(endpoint, method = 'GET', data = null) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {};
        const token = localStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`; 
        }

        const options = {
            method,
            headers
        };

        if (data && !(data instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        } else if (data instanceof FormData) {
            // Browser will set Content-Type with boundary for FormData
            options.body = data;
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.error || error.message || 'API request failed');
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) { return this.request(endpoint, 'GET'); },
    post(endpoint, data) { return this.request(endpoint, 'POST', data); },
    put(endpoint, data) { 
    return this.request(endpoint, 'PUT', data); 
},
    patch(endpoint, data) { return this.request(endpoint, 'PATCH', data); },
    delete(endpoint) { return this.request(endpoint, 'DELETE'); }
};
