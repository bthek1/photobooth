// Wedding Photobooth JavaScript

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
        this.activeSession = null;
        this.cameraSettings = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Load camera settings
            await this.loadCameraSettings();
            
            // Load active session
            await this.loadActiveSession();
            
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
            const response = await fetch('/photobooth/api/camera-settings/');
            this.cameraSettings = await response.json();
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
    
    async loadActiveSession() {
        try {
            const response = await fetch('/photobooth/api/active-session/');
            if (response.ok) {
                this.activeSession = await response.json();
                this.updatePhotoCount(this.activeSession.photo_count);
            } else {
                console.warn('No active session found');
            }
        } catch (error) {
            console.error('Failed to load active session:', error);
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
        
        if (!this.activeSession) {
            this.showError('No active session. Please contact the event organizer.');
            return;
        }
        
        this.isCapturing = true;
        this.captureBtn.disabled = true;
        
        try {
            // Start countdown
            await this.startCountdown();
            
            // Capture the photo
            const photoData = this.captureFrame();
            
            // Show flash effect
            this.showFlash();
            
            // Upload photo
            const result = await this.uploadPhoto(photoData);
            
            if (result.success) {
                this.currentPhotoId = result.photo_id;
                this.showPhotoTaken(photoData);
                this.updatePhotoCount();
                this.loadRecentPhotos();
            } else {
                throw new Error(result.error || 'Failed to save photo');
            }
            
        } catch (error) {
            console.error('Failed to capture photo:', error);
            this.showError('Failed to capture photo. Please try again.');
        } finally {
            this.isCapturing = false;
            this.captureBtn.disabled = false;
        }
    }
    
    async startCountdown() {
        const countdownNumber = this.countdownOverlay.querySelector('.countdown-number');
        this.countdownOverlay.classList.remove('d-none');
        
        for (let i = this.cameraSettings.countdown; i > 0; i--) {
            countdownNumber.textContent = i;
            countdownNumber.style.animation = 'none';
            // Force reflow
            countdownNumber.offsetHeight;
            countdownNumber.style.animation = 'pulse 1s ease-in-out';
            
            await this.sleep(1000);
        }
        
        this.countdownOverlay.classList.add('d-none');
    }
    
    captureFrame() {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(this.video, 0, 0);
        
        // Convert to base64 JPEG
        return canvas.toDataURL('image/jpeg', this.cameraSettings.quality / 100);
    }
    
    showFlash() {
        this.flashEffect.classList.remove('d-none');
        setTimeout(() => {
            this.flashEffect.classList.add('d-none');
        }, 300);
    }
    
    async uploadPhoto(photoData) {
        const payload = {
            image: photoData,
            session_id: this.activeSession.id,
            guest_name: this.guestNameInput.value.trim(),
            guest_email: this.guestEmailInput.value.trim()
        };
        
        const response = await fetch('/photobooth/api/capture/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    }
    
    showPhotoTaken(photoData) {
        const previewContainer = document.getElementById('photo-preview-container');
        previewContainer.innerHTML = `
            <img src="${photoData}" class="img-fluid rounded" alt="Captured photo" style="max-height: 400px;">
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('photoTakenModal'));
        modal.show();
    }
    
    showQRCode() {
        if (!this.currentPhotoId) return;
        
        const qrContainer = document.getElementById('qr-code-container');
        const qrCode = document.getElementById('qr-code');
        
        qrCode.innerHTML = `<img src="/photobooth/qr/${this.currentPhotoId}/" class="img-fluid" alt="QR Code">`;
        qrContainer.classList.remove('d-none');
    }
    
    downloadPhoto() {
        if (!this.currentPhotoId) return;
        
        window.open(`/photobooth/download/${this.currentPhotoId}/`, '_blank');
    }
    
    retakePhoto() {
        // This would be used if we had a photo preview mode
        // For now, just ensure camera is running
        if (!this.stream) {
            this.startCamera();
        }
    }
    
    updatePhotoCount(count = null) {
        if (this.photoCountElement) {
            if (count !== null) {
                this.photoCountElement.textContent = count;
            } else {
                // Increment current count
                const currentCount = parseInt(this.photoCountElement.textContent) || 0;
                this.photoCountElement.textContent = currentCount + 1;
            }
        }
    }
    
    async loadRecentPhotos() {
        try {
            const response = await fetch('/photobooth/gallery/');
            if (response.ok) {
                // This would load recent photos for the preview
                // For now, we'll leave this as a placeholder
                console.log('Recent photos loaded');
            }
        } catch (error) {
            console.error('Failed to load recent photos:', error);
        }
    }
    
    showError(message) {
        // Show error message to user
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show';
        errorAlert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(errorAlert, document.body.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (errorAlert.parentNode) {
                errorAlert.remove();
            }
        }, 5000);
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    destroy() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Initialize photobooth when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.photobooth = new PhotoboothCamera();
});

// Cleanup when page is unloaded
window.addEventListener('beforeunload', () => {
    if (window.photobooth) {
        window.photobooth.destroy();
    }
});
