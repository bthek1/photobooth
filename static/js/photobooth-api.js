// REST API Client for Photobooth
class PhotoboothAPI {
    constructor(baseUrl = '/api/photobooth/') {
        this.baseUrl = baseUrl;
        this.csrfToken = this.getCSRFToken();
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async apiCall(endpoint, options = {}) {
        const url = this.baseUrl + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            credentials: 'same-origin',
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        return data;
    }

    // Authentication
    async registerUser(userData) {
        return this.apiCall('auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // Event Management
    async getEvents() {
        return this.apiCall('events/');
    }

    async createEvent(eventData) {
        return this.apiCall('events/create/', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    }

    async getEvent(eventId) {
        return this.apiCall(`events/${eventId}/`);
    }

    async updateEvent(eventId, eventData) {
        return this.apiCall(`events/${eventId}/`, {
            method: 'PATCH',
            body: JSON.stringify(eventData)
        });
    }

    async deleteEvent(eventId) {
        return this.apiCall(`events/${eventId}/`, {
            method: 'DELETE'
        });
    }

    async joinEvent(code) {
        return this.apiCall('events/join/', {
            method: 'POST',
            body: JSON.stringify({ code })
        });
    }

    // Gallery
    async getEventGallery(eventId, page = 1) {
        return this.apiCall(`events/${eventId}/gallery/?page=${page}`);
    }

    async getEventInfo(eventId) {
        return this.apiCall(`events/${eventId}/info/`);
    }

    // Photo Operations
    async capturePhoto(eventId, imageData, guestName = '', guestEmail = '') {
        return this.apiCall('photos/capture/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            body: JSON.stringify({
                event_id: eventId,
                image: imageData,
                guest_name: guestName,
                guest_email: guestEmail
            })
        });
    }

    async getPhoto(photoId) {
        return this.apiCall(`photos/${photoId}/`);
    }

    async updatePhotoMetadata(photoId, metadata) {
        return this.apiCall(`photos/${photoId}/`, {
            method: 'PATCH',
            body: JSON.stringify(metadata)
        });
    }

    // Settings
    async getCameraSettings() {
        return this.apiCall('settings/camera/');
    }

    // Utility methods for UI
    getPhotoDownloadUrl(photoId) {
        return `${this.baseUrl}photos/${photoId}/download/`;
    }

    getPhotoQRUrl(photoId) {
        return `${this.baseUrl}qr/photo/${photoId}/`;
    }

    getEventQRUrl(eventId) {
        return `${this.baseUrl}qr/event/${eventId}/`;
    }
}

// Example usage for Event Creation (replacing form)
class EventCreationManager {
    constructor() {
        this.api = new PhotoboothAPI();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const createEventBtn = document.getElementById('create-event-btn');
        if (createEventBtn) {
            createEventBtn.addEventListener('click', (e) => this.handleCreateEvent(e));
        }

        const joinEventBtn = document.getElementById('join-event-btn');
        if (joinEventBtn) {
            joinEventBtn.addEventListener('click', (e) => this.handleJoinEvent(e));
        }
    }

    async handleCreateEvent(e) {
        e.preventDefault();
        
        const nameInput = document.getElementById('event-name');
        const qrBaseUrlInput = document.getElementById('qr-base-url');
        
        if (!nameInput || !nameInput.value.trim()) {
            this.showError('Event name is required');
            return;
        }

        try {
            const eventData = {
                name: nameInput.value.trim(),
                qr_base_url: qrBaseUrlInput ? qrBaseUrlInput.value : ''
            };

            const result = await this.api.createEvent(eventData);
            this.showSuccess(result.message);
            
            // Redirect or update UI
            if (result.event) {
                window.location.href = `/photobooth/events/${result.event.id}/`;
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    async handleJoinEvent(e) {
        e.preventDefault();
        
        const codeInput = document.getElementById('event-code');
        
        if (!codeInput || !codeInput.value.trim()) {
            this.showError('Event code is required');
            return;
        }

        try {
            const result = await this.api.joinEvent(codeInput.value.trim().toUpperCase());
            this.showSuccess(result.message);
            
            // Redirect to booth
            if (result.redirect_url) {
                window.location.href = result.redirect_url;
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    showError(message) {
        // Replace with your preferred notification system
        const errorDiv = document.getElementById('error-messages');
        if (errorDiv) {
            errorDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        } else {
            alert('Error: ' + message);
        }
    }

    showSuccess(message) {
        // Replace with your preferred notification system
        const successDiv = document.getElementById('success-messages');
        if (successDiv) {
            successDiv.innerHTML = `<div class="alert alert-success">${message}</div>`;
        } else {
            alert('Success: ' + message);
        }
    }
}

// User Registration Manager (replacing form)
class UserRegistrationManager {
    constructor() {
        this.api = new PhotoboothAPI();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const registerBtn = document.getElementById('register-btn');
        if (registerBtn) {
            registerBtn.addEventListener('click', (e) => this.handleRegistration(e));
        }
    }

    async handleRegistration(e) {
        e.preventDefault();
        
        const form = document.getElementById('registration-form');
        if (!form) return;

        const formData = new FormData(form);
        const userData = {
            email: formData.get('email'),
            first_name: formData.get('first_name') || '',
            last_name: formData.get('last_name') || '',
            password1: formData.get('password1'),
            password2: formData.get('password2')
        };

        try {
            const result = await this.api.registerUser(userData);
            this.showSuccess(result.message);
            
            // Redirect to events page
            window.location.href = '/photobooth/events/';
        } catch (error) {
            this.showError(error.message);
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('error-messages');
        if (errorDiv) {
            errorDiv.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        }
    }

    showSuccess(message) {
        const successDiv = document.getElementById('success-messages');
        if (successDiv) {
            successDiv.innerHTML = `<div class="alert alert-success">${message}</div>`;
        }
    }
}

// Make API available globally immediately
window.PhotoboothAPI = PhotoboothAPI;

// Initialize managers when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize API-based managers
    window.eventManager = new EventCreationManager();
    window.userManager = new UserRegistrationManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PhotoboothAPI, EventCreationManager, UserRegistrationManager };
}
