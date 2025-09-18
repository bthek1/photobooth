# 📸 Wedding Photobooth System

A professional, Django-powered wedding photobooth system with webcam integration, real-time photo capture, gallery management, and QR code sharing. Perfect for weddings, events, and parties!

![Photobooth Interface](static/images/photobooth-preview.png)

## ✨ Features

### 📷 Core Photobooth Features
- **Live Camera Preview** - Real-time webcam feed with professional interface
- **Countdown Timer** - Configurable countdown before photo capture
- **Flash Effect** - Visual feedback when photos are taken
- **Guest Information** - Optional name and email collection
- **Session Management** - Support for multiple events/sessions

### 🖼️ Gallery & Sharing
- **Photo Gallery** - Beautiful grid layout with pagination
- **QR Code Generation** - Instant QR codes for photo downloads and gallery access
- **Direct Downloads** - One-click photo downloads
- **Responsive Design** - Works on all devices and screen sizes

### ⚙️ Professional Features
- **Admin Dashboard** - Full Django admin for session and photo management
- **Configurable Settings** - Camera resolution, countdown timer, messages
- **Photo Metadata** - Timestamps, guest names, session tracking
- **Bulk Operations** - Admin tools for managing large photo collections

### 🎨 Wedding-Ready Design
- **Professional UI** - Clean, modern interface perfect for events
- **Wedding Themes** - Beautiful gradient color schemes
- **Mobile Responsive** - Touch-friendly interface for tablets
- **Full-Screen Mode** - Immersive photobooth experience

## � Table of Contents

- [Quick Start](#quick-start)
- [Hardware Requirements](#hardware-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Administration](#administration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Hardware Requirements

**Minimum Setup:**
- Computer with webcam (laptop or desktop)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for initial setup

**Recommended Setup:**
- Dedicated computer/laptop for photobooth
- External USB webcam (1080p or higher)
- Large external monitor (24" or larger)
- Stable internet connection
- Optional: Wireless keyboard/mouse for setup

**Professional Setup:**
- Raspberry Pi 4 or dedicated mini PC
- High-quality USB webcam (4K recommended)
- Touchscreen monitor for guest interaction
- Professional lighting setup
- Wireless network for guest access

## 📖 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/photobooth.git
cd photobooth
```

### 2. Install Dependencies (using uv)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

### 3. Database Setup

```bash
# Run migrations
uv run manage.py migrate

# Create a superuser account for admin access
uv run manage.py createsuperuser

# Load initial photobooth settings
uv run manage.py shell -c "
from photobooth.models import PhotoboothSettings
PhotoboothSettings.get_settings()
print('Photobooth settings initialized!')
"
```

### 4. Start the Development Server

```bash
uv run manage.py runserver 0.0.0.0:8000
```

Your photobooth will be available at `http://localhost:8000/photobooth/`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,your-domain.com

# Database (default is SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Email Settings (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@yourwedding.com
```

### Photobooth Settings

Access the admin panel at `http://localhost:8000/admin/` to configure:

1. **Camera Settings**
   - Resolution (default: 1920x1080)
   - Frame rate (default: 30fps)
   - Photo quality (default: 95%)

2. **Session Settings**
   - Welcome message
   - Instructions text
   - Countdown duration

3. **Gallery Settings**
   - Enable/disable preview
   - Photos per page
   - Auto-cleanup settings

## 🎯 Usage

### Setting Up for an Event

1. **Create a New Session**
   ```bash
   # Via Django admin or shell
   uv run manage.py shell -c "
   from photobooth.models import PhotoboothSession
   from django.utils import timezone
   
   session = PhotoboothSession.objects.create(
       name='John & Jane Wedding',
       date=timezone.now(),
       is_active=True,
       qr_base_url='http://your-domain.com'
   )
   print(f'Session created: {session.name}')
   "
   ```

2. **Configure Hardware**
   - Connect webcam to computer
   - Position monitor for guests
   - Test camera permissions in browser
   - Ensure good lighting

3. **Test the System**
   - Visit `/photobooth/` in your browser
   - Take test photos
   - Verify QR codes work
   - Check photo downloads

### Guest Experience

1. **Approach the Photobooth**
   - Guests see live camera preview
   - Welcome message displays event name

2. **Take Photos**
   - Click "Take Photo" button
   - 3-second countdown begins
   - Flash effect on capture
   - Instant photo preview

3. **Get Photos**
   - Download directly from interface
   - Scan QR code for mobile download
   - Access full gallery via QR code

### Gallery Access

- **Main Gallery**: `/photobooth/gallery/`
- **Session Gallery**: `/photobooth/gallery/{session-id}/`
- **QR Codes**: Automatically generated for each photo and session

## 👨‍💼 Administration

### Admin Dashboard

Access at `/admin/` to manage:

- **Sessions**: Create/edit events, set active session
- **Photos**: View all photos, guest information, metadata
- **Settings**: Configure camera, UI, and system settings

### Useful Admin Commands

```bash
# Create a new session
uv run manage.py shell -c "
from photobooth.models import PhotoboothSession
PhotoboothSession.objects.create(
    name='Event Name',
    is_active=True
)
"

# Export photos for an event
uv run manage.py shell -c "
import os, shutil
from photobooth.models import Photo

session_id = 'your-session-id'
photos = Photo.objects.filter(session_id=session_id)

export_dir = f'exported_photos_{session_id}'
os.makedirs(export_dir, exist_ok=True)

for i, photo in enumerate(photos, 1):
    if photo.image:
        src = photo.image.path
        dst = f'{export_dir}/photo_{i:04d}_{photo.taken_at.strftime(\"%Y%m%d_%H%M%S\")}.jpg'
        shutil.copy2(src, dst)

print(f'Exported {len(photos)} photos to {export_dir}/')
"

# Clean up old photos (optional)
uv run manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from photobooth.models import Photo

cutoff_date = timezone.now() - timedelta(days=30)
old_photos = Photo.objects.filter(taken_at__lt=cutoff_date)
count = old_photos.count()
old_photos.delete()
print(f'Deleted {count} photos older than 30 days')
"
```

## 🚀 Deployment

### Production Setup

1. **Set Production Environment Variables**

```bash
# .env file for production
DJANGO_SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://user:password@localhost/photobooth_db

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
```

2. **Configure Static Files for Production**

```bash
# Collect static files
uv run manage.py collectstatic --noinput
```

3. **Use Gunicorn for Production**

```bash
# Install gunicorn
uv add gunicorn

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Raspberry Pi Deployment

Perfect for dedicated photobooth setups:

```bash
# On Raspberry Pi OS
sudo apt update
sudo apt install python3-pip python3-venv

# Clone and setup
git clone https://github.com/your-username/photobooth.git
cd photobooth

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database and run
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Create systemd service for autostart
sudo nano /etc/systemd/system/photobooth.service
```

**Systemd Service File:**

```ini
[Unit]
Description=Wedding Photobooth
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/photobooth
Environment=PATH=/home/pi/photobooth/venv/bin
ExecStart=/home/pi/photobooth/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable photobooth.service
sudo systemctl start photobooth.service
```

## 🔧 Troubleshooting

### Common Issues

#### Camera Not Working

**Problem**: "Camera access denied" or black screen

**Solutions**:
- Ensure browser has camera permissions
- Try different browsers (Chrome recommended)
- Check if camera is used by another application
- For Linux: Check camera device permissions
- For Raspberry Pi: Enable camera in raspi-config

```bash
# Check camera devices on Linux
ls /dev/video*

# Test camera with v4l2
v4l2-ctl --list-devices
```

#### Photos Not Saving

**Problem**: Photos capture but don't appear in gallery

**Solutions**:
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Verify write permissions on media directory
- Check Django logs for errors
- Ensure session is active in admin

```bash
# Check media directory permissions
ls -la media/
sudo chown -R www-data:www-data media/  # For production
```

#### QR Codes Not Working

**Problem**: QR codes don't generate or scan properly

**Solutions**:
- Verify `qrcode` package is installed: `uv add qrcode`
- Check `qr_base_url` in session settings
- Ensure proper URL configuration
- Test QR code URLs manually

#### Performance Issues

**Problem**: Slow photo capture or processing

**Solutions**:
- Reduce camera resolution in admin settings
- Lower photo quality setting
- Check available disk space
- Monitor server resources

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Monitor in real-time
htop
```

### Browser Compatibility

**Recommended Browsers**:
- Chrome/Chromium (best camera support)
- Firefox (good compatibility)
- Safari (iOS/macOS)
- Edge (Windows)

**Mobile Considerations**:
- Touch-friendly interface included
- Responsive design for tablets
- Consider screen orientation for setup

### Network Setup

For guest access to galleries:
- Ensure firewall allows connections on port 8000
- Set up local WiFi network for guests
- Consider mobile hotspot for remote events
- Print QR codes as backup for gallery access

### Backup and Recovery

```bash
# Backup photos
cp -r media/photos /backup/photos_$(date +%Y%m%d)

# Backup database
uv run manage.py dumpdata > backup_$(date +%Y%m%d).json

# Restore from backup
uv run manage.py loaddata backup_20240101.json
```

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Features**: Request features via GitHub Discussions
- **Community**: Join our Discord for real-time help
- **Documentation**: Full docs at [docs.photoboothproject.com](https://docs.photoboothproject.com)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Made with ❤️ for weddings and special events**

I cover all of these steps in tutorials and premium courses over at [LearnDjango.com](https://learndjango.com).

## 🤝 Contributing

Contributions, issues and feature requests are welcome! See [CONTRIBUTING.md](https://github.com/wsvincent/lithium/blob/master/CONTRIBUTING.md).

## ⭐️ Support

Give a ⭐️  if this project helped you!

## License

[The MIT License](LICENSE)
