# Django Photobooth Project - AI Coding Instructions

## Architecture Overview

This is a **Django wedding photobooth system** with WebRTC camera integration, event management, and QR code sharing. The project follows a **multi-app Django structure** with distinct boundaries:

- **`photobooth/`** - Core photobooth functionality (Event/Photo models, camera API, image processing)
- **`accounts/`** - User management and authentication (extends django-allauth)
- **`pages/`** - Static pages and general content
- **`config/`** - Django project settings and URL routing

## Key Data Models & Relationships

```python
Event (UUID-based, owns multiple photos)
├── code (6-char random code for easy joining)  
├── created_by (User who owns the event)
└── photos (One-to-many relationship)

Photo (UUID-based, belongs to an Event)
├── session (ForeignKey to Event)
├── image (ImageField with upload_to=photo_upload_path)
├── guest_name/guest_email (optional metadata)
└── taken_at (timestamp)

PhotoboothSettings (singleton model)
├── camera settings (resolution, fps, quality)
├── UI settings (welcome message, countdown)  
└── technical settings (cleanup, limits)
```

## Critical Workflows & Commands

**Development setup:**
```bash
uv sync                                    # Install dependencies
uv run manage.py migrate                   # Apply migrations  
uv run manage.py runserver 0.0.0.0:8005   # Run server (note port 8005)
```

**Using Makefile (preferred):**
```bash
make migrate        # makemigrations + migrate
make runserver      # migrate + runserver on 8005
make test          # Run pytest
make flush         # Clear DB (DEBUG mode only)
```

**Model creation pattern:**
- Always use UUID primary keys for Event/Photo models
- Use `photo_upload_path()` function for consistent file organization
- Access settings via `PhotoboothSettings.get_settings()` (singleton pattern)

## Frontend Camera Integration

**WebRTC Implementation (`static/js/photobooth.js`):**
- Uses `navigator.mediaDevices.getUserMedia()` for camera access
- Implements countdown timer before capture
- Captures photos as base64 data and sends to Django API
- Handles flash effects and UI feedback

**Key API Endpoints:**
- `/api/capture/` - POST base64 image data to create Photo
- `/api/camera-settings/` - GET PhotoboothSettings for frontend
- `/api/event/<uuid>/info/` - GET Event details for active session

## URL Patterns & Navigation

**Event Flow:**
1. User creates Event → gets 6-char code
2. Guests join via code → `/join/` redirects to booth
3. Booth interface → `/event/<uuid>/booth/`
4. Gallery access → `/event/<uuid>/gallery/`

**Authentication:**
- Uses django-allauth for user management
- Event owners must be logged in to create/manage events
- Guest booth access is public (no auth required)

## File Upload & Media Handling

**Photo Storage:**
```python
# Upload path: media/photos/{event_id}/{uuid}.jpg
def photo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("photos", str(instance.session.id), filename)
```

**QR Code Generation:**
- Photos get individual QR codes for mobile download
- Events get gallery QR codes for full album access
- Generated in-memory using `qrcode` library

## Testing & Code Quality

**Test Structure:**
- Use `pytest-django` for testing
- Test files in `{app}/tests/` directories
- Factory Boy for model factories (`conftest.py` pattern)

**Common Patterns:**
- Use `get_object_or_404` for UUID lookups
- LoginRequiredMixin for owner-only views
- CSRF exempt for API endpoints receiving base64 data

## Environment & Deployment

**Key Settings:**
- Uses `django-environ` for configuration
- Redis for channels/WebSocket support (future use)
- PostgreSQL in production, SQLite in development
- WhiteNoise for static files in production

**Docker Setup:**
- `docker-compose.yml` includes web + postgres services  
- Development runs on port 8000 (Docker) or 8005 (local)

## Migration & Future Plans

**Current Tech Debt (see TODO.md):**
- Planning React frontend migration
- Moving to JWT authentication  
- S3 integration for photo storage
- WebSocket controller for mobile devices

**When Adding Features:**
- Follow the Event → Photo relationship hierarchy
- Use UUID fields consistently
- Implement proper error handling for camera/media operations
- Consider mobile responsiveness (touch interfaces)
