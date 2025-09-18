# API Migration Guide

## Overview

The photobooth application is migrating from Django forms to a REST API architecture. This provides better separation of concerns and enables future frontend framework integration.

## Available REST API Endpoints

### Authentication
- `POST /api/photobooth/auth/register/` - User registration

### Event Management
- `GET /api/photobooth/events/` - List user's events (authenticated)
- `POST /api/photobooth/events/create/` - Create new event (authenticated) 
- `GET /api/photobooth/events/{id}/` - Get event details (owner only)
- `PATCH /api/photobooth/events/{id}/` - Update event (owner only)
- `DELETE /api/photobooth/events/{id}/` - Delete event (owner only)
- `POST /api/photobooth/events/join/` - Join event with code (public)

### Gallery & Photos
- `GET /api/photobooth/events/{id}/gallery/` - Event gallery with pagination (public)
- `GET /api/photobooth/events/{id}/info/` - Event information (public)
- `POST /api/photobooth/photos/capture/` - Capture photo (public)
- `GET /api/photobooth/photos/{id}/` - Photo details (public)
- `PATCH /api/photobooth/photos/{id}/` - Update photo metadata (public)
- `GET /api/photobooth/photos/{id}/download/` - Download photo (public)

### Settings & Utilities
- `GET /api/photobooth/settings/camera/` - Camera settings (public)
- `GET /api/photobooth/qr/photo/{id}/` - Photo QR code (public)
- `GET /api/photobooth/qr/event/{id}/` - Event gallery QR code (public)

## JavaScript API Client

A JavaScript client (`PhotoboothAPI`) is available in `/static/js/photobooth-api.js`:

```javascript
const api = new PhotoboothAPI();

// Create an event
const event = await api.createEvent({
    name: "John & Jane Wedding",
    qr_base_url: "https://yourdomain.com"
});

// Join an event
const result = await api.joinEvent("ABC123");

// Capture a photo
const photoResult = await api.capturePhoto(
    eventId, 
    base64ImageData, 
    "Guest Name", 
    "guest@email.com"
);
```

## Migration Status

### ✅ Completed
- REST API endpoints for all core functionality
- JavaScript API client
- Updated photobooth camera to use new API
- Backward compatibility with existing form-based views

### 🔄 In Progress
- Frontend form replacement (currently both systems coexist)

### 📋 TODO
- Remove Django forms dependency completely
- Migrate all templates to use JavaScript API client
- Remove legacy API endpoints in photobooth/views.py
- Add comprehensive API documentation with OpenAPI/Swagger

## Usage Examples

### Event Creation (API)
```javascript
// Replace form submission with API call
const createEvent = async (eventName) => {
    const api = new PhotoboothAPI();
    try {
        const result = await api.createEvent({ name: eventName });
        window.location.href = `/photobooth/events/${result.event.id}/`;
    } catch (error) {
        console.error('Event creation failed:', error);
    }
};
```

### Photo Capture (API)
```javascript
// Camera integration uses new API
const capturePhoto = async (eventId, imageData) => {
    const api = new PhotoboothAPI();
    const result = await api.capturePhoto(eventId, imageData);
    return result.photo_id;
};
```

## Error Handling

The API returns consistent error responses:

```json
{
    "error": "Descriptive error message",
    "field_errors": {
        "field_name": ["Field-specific error"]
    }
}
```

## Authentication

- Uses Django session authentication for web interface
- Ready for JWT token authentication (configured in settings)
- CSRF protection enabled for state-changing operations
