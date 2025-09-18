// Event Photobooth JavaScript

class PhotoboothCamera {
    constructor() {
        this.video = document.getElementById('camera-video');
        this.captureBtn = document.getElementById('capture-btn');
        this.retakeBtn = document.getElementById('retake-btn');
        this.countdownOverlay = document.getElementById('countdown-overlay');
        this.flashEffect = document.getElementById('flash-effect');
        this.guestNameInput = document.getElementById('guest-name');
        this.guestEmailInput = document.getElementById('guest-email');
        this.photoCountElement = document.getElementById('photo-count');
        
        this.stream = null;
        this.isCapturing = false;
        this.currentEvent = null;
        this.cameraSettings = null;
        this.lastPhotoId = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Load event data from global variable
            if (window.eventData) {
                this.currentEvent = window.eventData;
                console.log('Loaded event:', this.currentEvent);
            }
            
            // Load camera settings
            await this.loadCameraSettings();
            
            // Start camera
            await this.startCamera();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load recent photos
            this.loadRecentPhotos();
            
        } catch (error) {
            console.error('Failed to initialize photobooth:', error);
            this.showError('Failed to initialize camera. Please refresh the page.');
        }
    }
    
    async loadCameraSettings() {
        try {
            // Check if PhotoboothAPI is available, otherwise use legacy
            if (typeof PhotoboothAPI !== 'undefined') {
                const api = new PhotoboothAPI();
                this.cameraSettings = await api.getCameraSettings();
            } else {
                // Legacy API call
                const response = await fetch('/photobooth/api/camera-settings/');
                this.cameraSettings = await response.json();
            }
        } catch (error) {
            console.error('Failed to load camera settings:', error);
            // Use default settings
            this.cameraSettings = {
                resolution: { width: 1920, height: 1080 },
                fps: 30,
                countdown: 3,
                quality: 95
            };
        }
    }
    
    async startCamera() {
        try {
            const constraints = {
                video: {
                    width: { ideal: this.cameraSettings.resolution.width },
                    height: { ideal: this.cameraSettings.resolution.height },
                    frameRate: { ideal: this.cameraSettings.fps },
                    facingMode: 'user' // Front camera preferred for photobooth
                }
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            
            // Wait for video to be ready
            return new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });
            
        } catch (error) {
            console.error('Camera access denied or not available:', error);
            throw new Error('Camera access is required for the photobooth');
        }
    }
    
    setupEventListeners() {
        this.captureBtn.addEventListener('click', () => this.capturePhoto());
        this.retakeBtn.addEventListener('click', () => this.retakePhoto());
        
        // Handle modal events
        const photoTakenModal = document.getElementById('photoTakenModal');
        if (photoTakenModal) {
            photoTakenModal.addEventListener('hidden.bs.modal', () => {
                // Clear photo preview when modal is closed
                document.getElementById('photo-preview-container').innerHTML = '';
                document.getElementById('qr-code-container').classList.add('d-none');
            });
        }
        
        // Handle QR code button
        const showQRBtn = document.getElementById('show-qr-btn');
        if (showQRBtn) {
            showQRBtn.addEventListener('click', () => this.showQRCode());
        }
        
        // Handle take another photo button
        const takeAnotherBtn = document.getElementById('take-another-btn');
        if (takeAnotherBtn) {
            takeAnotherBtn.addEventListener('click', () => {
                bootstrap.Modal.getInstance(photoTakenModal).hide();
            });
        }
        
        // Handle download button
        const downloadPhotoBtn = document.getElementById('download-photo-btn');
        if (downloadPhotoBtn) {
            downloadPhotoBtn.addEventListener('click', () => this.downloadPhoto());
        }
    }
    
    async capturePhoto() {
        if (this.isCapturing) return;
        
        if (!this.currentEvent) {
            this.showError('No event data available. Please refresh the page.');
            return;
        }
        
        this.isCapturing = true;
        this.captureBtn.disabled = true;
        
        try {
            // Start countdown
            await this.startCountdown();
            
            // Capture the photo
            const imageData = this.captureFrame();
            
            // Flash effect
            this.showFlash();
            
            // Send photo to server
            await this.sendPhoto(imageData);
            
        } catch (error) {
            console.error('Failed to capture photo:', error);
            this.showError('Failed to capture photo. Please try again.');
        } finally {
            this.isCapturing = false;
            this.captureBtn.disabled = false;
        }
    }
    
    async startCountdown() {
        return new Promise((resolve) => {
            const countdownNumber = this.countdownOverlay.querySelector('.countdown-number');
            this.countdownOverlay.classList.remove('d-none');
            
            let count = this.cameraSettings.countdown;
            countdownNumber.textContent = count;
            
            const countdownInterval = setInterval(() => {
                count--;
                if (count > 0) {
                    countdownNumber.textContent = count;
                } else {
                    clearInterval(countdownInterval);
                    this.countdownOverlay.classList.add('d-none');
                    resolve();
                }
            }, 1000);
        });
    }
    
    captureFrame() {
        // Create canvas to capture video frame
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(this.video, 0, 0);
        
        // Convert to base64
        return canvas.toDataURL('image/jpeg', this.cameraSettings.quality / 100);
    }
    
    showFlash() {
        this.flashEffect.classList.remove('d-none');
        setTimeout(() => {
            this.flashEffect.classList.add('d-none');
        }, 200);
    }
    
    async sendPhoto(imageData) {
        try {
            // Check if PhotoboothAPI is available
            if (typeof PhotoboothAPI === 'undefined') {
                console.error('PhotoboothAPI not loaded, falling back to legacy method');
                return this.sendPhotoLegacy(imageData);
            }
            
            // Use new REST API
            const api = new PhotoboothAPI();
            const result = await api.capturePhoto(
                this.currentEvent.id,
                imageData,
                this.guestNameInput.value.trim(),
                this.guestEmailInput.value.trim()
            );
            
            if (result.success) {
                this.lastPhotoId = result.photo_id;
                this.showPhotoTakenModal(imageData);
                this.updatePhotoCount();
            } else {
                throw new Error(result.message || 'Failed to capture photo');
            }
        } catch (error) {
            console.error('Photo capture failed:', error);
            // Try legacy method as fallback
            console.log('Attempting legacy photo capture...');
            try {
                await this.sendPhotoLegacy(imageData);
            } catch (legacyError) {
                console.error('Legacy photo capture also failed:', legacyError);
                this.showError('Failed to capture photo. Please try again.');
            }
        }
    }
    
    // Legacy method for compatibility (will be removed)
    async sendPhotoLegacy(imageData) {
        const photoData = {
            image: imageData,
            event_id: this.currentEvent.id,
            guest_name: this.guestNameInput.value.trim(),
            guest_email: this.guestEmailInput.value.trim()
        };
        
        const response = await fetch('/photobooth/api/capture/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(photoData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save photo');
        }
        
        const result = await response.json();
        this.lastPhotoId = result.photo_id;
        
        // Update photo count
        this.updatePhotoCount();
        
        // Show photo preview
        this.showPhotoTakenModal(imageData);
        
        // Clear guest info (optional)
        // this.guestNameInput.value = '';
        // this.guestEmailInput.value = '';
        
        // Refresh recent photos
        this.loadRecentPhotos();
    }
    
    showPhotoTakenModal(imageData) {
        // Show photo preview
        const previewContainer = document.getElementById('photo-preview-container');
        previewContainer.innerHTML = `<img src="${imageData}" class="img-fluid" alt="Captured Photo">`;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('photoTakenModal'));
        modal.show();
    }
    
    async updatePhotoCount() {
        if (!this.currentEvent) return;
        
        try {
            const response = await fetch(`/photobooth/api/event/${this.currentEvent.id}/info/`);
            if (response.ok) {
                const eventInfo = await response.json();
                if (this.photoCountElement) {
                    this.photoCountElement.textContent = eventInfo.photo_count;
                }
            }
        } catch (error) {
            console.error('Failed to update photo count:', error);
        }
    }
    
    async loadRecentPhotos() {
        // This would load recent photos for the event
        // Implementation depends on if you want to show recent photos
        console.log('Loading recent photos for event:', this.currentEvent?.name);
    }
    
    showQRCode() {
        if (!this.lastPhotoId) return;
        
        const qrContainer = document.getElementById('qr-code-container');
        const qrCodeDiv = document.getElementById('qr-code');
        
        // Load QR code image
        qrCodeDiv.innerHTML = `<img src="/photobooth/qr/photo/${this.lastPhotoId}/" class="img-fluid" alt="QR Code">`;
        qrContainer.classList.remove('d-none');
    }
    
    downloadPhoto() {
        if (!this.lastPhotoId) return;
        
        // Open download URL in new window
        window.open(`/photobooth/download/${this.lastPhotoId}/`, '_blank');
    }
    
    retakePhoto() {
        // Hide retake button, show capture button
        this.retakeBtn.classList.add('d-none');
        this.captureBtn.classList.remove('d-none');
        
        // Could add additional retake logic here
    }
    
    showError(message) {
        // Create or show error alert
        const alertContainer = document.createElement('div');
        alertContainer.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertContainer);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on a page with camera elements
    if (document.getElementById('camera-video')) {
        // Small delay to ensure all scripts are loaded
        setTimeout(() => {
            console.log('PhotoboothAPI available:', typeof PhotoboothAPI !== 'undefined');
            new PhotoboothCamera();
        }, 100);
    }
});

// Global functions for gallery
function downloadPhoto(photoId) {
    window.open(`/photobooth/download/${photoId}/`, '_blank');
}

function showQRCode(photoId) {
    // This function is used in gallery template
    const qrUrl = `/photobooth/qr/photo/${photoId}/`;
    document.getElementById('qr-code-display').innerHTML = `<img src="${qrUrl}" class="img-fluid" alt="QR Code">`;
    new bootstrap.Modal(document.getElementById('qrModal')).show();
}
