// State to track last seen challan ID to detect new ones
let lastChallanId = 0;

// Show Toast Notification
function showToast(vehicleNo) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle" style="font-size: 1.5rem;"></i>
        <div>
            <p style="font-weight: 700;">NEW VIOLATION</p>
            <p style="font-size: 0.85rem;">Vehicle: ${vehicleNo} detected without helmet.</p>
        </div>
    `;
    container.appendChild(toast);

    // Add to activity log
    addLogEntry(`AUTO-DETECT: Violation by ${vehicleNo}`, true);

    // Remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Add Log Entry
function addLogEntry(message, isAlert = false) {
    const log = document.getElementById('activityLog');
    if (!log) return;

    const entry = document.createElement('div');
    entry.className = `log-entry ${isAlert ? 'alert' : ''}`;
    entry.innerText = `${new Date().toLocaleTimeString()} - ${message}`;

    log.insertBefore(entry, log.firstChild);

    // Keep only last 20 entries
    if (log.children.length > 20) {
        log.lastElementChild.remove();
    }
}

// Fetch Statistics
async function updateStats() {
    try {
        const response = await fetch(getApiUrl('/api/stats'));
        const data = await response.json();

        if (document.getElementById('todayViolations')) {
            document.getElementById('todayViolations').innerText = data.today_violations;
            if (document.getElementById('revenue')) {
                document.getElementById('revenue').innerText = '₹' + data.revenue.toLocaleString();
            }

            // Update AI Status in Activity Log if first run
            if (window.isFirstStatsUpdate !== false) {
                const log = document.getElementById('activityLog');
                if (log) {
                    log.innerHTML = ''; // Clear hardcoded demo logs
                    addLogEntry(`Detection Engine: ${data.ai_status}`);
                    addLogEntry(`Model: ${data.model_name}`);
                }
                window.isFirstStatsUpdate = false;
            }
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Fetch Recent Challans
async function updateChallans() {
    try {
        const response = await fetch(getApiUrl('/api/challans'));
        const data = await response.json();

        const tableBody = document.getElementById('recentViolationsTable');
        if (tableBody) {
            tableBody.innerHTML = '';
            data.slice(0, 10).forEach((challan, index) => {
                // Check if this is a new challan
                if (index === 0 && lastChallanId !== 0 && challan.id > lastChallanId) {
                    showToast(challan.vehicle_no);
                }

                const row = `
                    <tr id="row-${challan.id}">
                        <td>
                            <div style="position: relative; width: 80px; height: 50px; cursor: pointer;" onclick="window.open(getApiUrl('${challan.image_path}'), '_blank')">
                                <img src="${getApiUrl(challan.image_path)}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 6px; border: 1px solid #334155;">
                                <div style="position:absolute; bottom: 2px; right: 2px; background: rgba(0,0,0,0.6); font-size: 0.6rem; padding: 2px 4px; border-radius: 4px;">🔍</div>
                            </div>
                        </td>
                        <td style="font-family: monospace; font-size: 1rem; font-weight: 600; color: var(--accent-color);">${challan.vehicle_no}</td>
                        <td style="color: var(--text-muted);">${new Date(challan.timestamp).toLocaleString()}</td>
                        <td>
                            <button onclick="window.location.href='dashboard.html'" style="padding: 6px 12px; border-radius: 6px; background: #334155; color: white; border: none; cursor: pointer; font-size: 0.8rem;">View Details</button>
                        </td>
                    </tr>
                `;
                tableBody.insertAdjacentHTML('beforeend', row);
            });

            if (data.length > 0) {
                lastChallanId = data[0].id;
            }
        }
    } catch (error) {
        console.error('Error fetching challans:', error);
    }
}

// --- WEB CAMERA SUPPORT (MOBILE & DESKTOP) ---
let stream = null;
let currentFacingMode = 'environment'; // Default to back camera for mobile
let isProcessing = false;

// Check if getUserMedia is available
function isCameraSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

// Request camera permissions
async function checkCameraPermissions() {
    if (!isCameraSupported()) {
        console.error("Camera not supported in this browser");
        return false;
    }
    try {
        const result = await navigator.permissions.query({ name: 'camera' });
        return result.state !== 'denied';
    } catch (e) {
        console.log("Permissions API unavailable, trying direct access...");
        return true;
    }
}

// Support for Server-Side Camera Feed
function useServerFeed() {
    const video = document.getElementById('videoElement');
    const processedImg = document.getElementById('processedFrame');
    const aiStatus = document.getElementById('aiStatus');
    const startBtn = document.getElementById('startCamBtn');

    // Stop browser capture if any
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    isProcessing = false;

    // Switch to server video stream
    video.style.display = 'none';
    processedImg.src = getApiUrl('/video_feed');

    aiStatus.innerHTML = `<i class="fas fa-circle" style="color: #22c55e; font-size: 0.7rem; animation: pulse 2s infinite;"></i> AI ENGINE: ACTIVE (SERVER FEED)`;
    startBtn.innerText = "Stop Server Feed";
    startBtn.style.background = "#ef4444";

    addLogEntry("✓ Switched to Server-Side Camera Feed", false);
}

async function startCamera(facingMode = 'environment') {
    const video = document.getElementById('videoElement');
    const aiStatus = document.getElementById('aiStatus');
    const startBtn = document.getElementById('startCamBtn');
    const switchBtn = document.getElementById('switchCamBtn');

    try {
        // Check if camera is supported
        if (!isCameraSupported()) {
            throw new Error("Camera API not supported in this browser. Please use Chrome, Firefox, Safari, or Edge.");
        }

        // Stop existing stream
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }

        addLogEntry("Requesting camera access...", false);

        const constraints = {
            video: {
                facingMode: { ideal: facingMode },
                width: { ideal: 1280, min: 640 },
                height: { ideal: 720, min: 480 }
            },
            audio: false // Disable audio for camera
        };

        // Request camera access
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        video.onloadedmetadata = function () {
            video.play().catch(e => console.error("Play error:", e));
        };

        currentFacingMode = facingMode;

        aiStatus.innerHTML = `<i class="fas fa-circle" style="color: #22c55e; font-size: 0.7rem; animation: pulse 2s infinite;"></i> AI ENGINE: ACTIVE (STREAMING)`;
        startBtn.innerText = "Stop Camera";
        startBtn.style.background = "#ef4444";
        switchBtn.style.display = "block";

        if (!isProcessing) {
            isProcessing = true;
            processLoop();
        }

        addLogEntry(`✓ Camera Started (${facingMode === 'environment' ? 'Back' : 'Front'} Camera)`, false);
    } catch (err) {
        console.error("Camera Error Details:", err);
        let errorMsg = "Camera Access Denied";
        let suggestServer = false;

        // More specific error messages
        if (err.name === 'NotAllowedError') {
            errorMsg = "Camera access was denied by user";
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            errorMsg = "No camera device found";
        } else if (err.name === 'NotSupportedError' || !isCameraSupported()) {
            errorMsg = "Browser Camera logic not supported (Needs HTTPS)";
            suggestServer = true;
        } else if (err.message.includes("not supported")) {
            errorMsg = "Camera not supported";
            suggestServer = true;
        }

        let statusHtml = `<i class="fas fa-circle" style="color: #ef4444; font-size: 0.7rem;"></i> ERROR: ${errorMsg}`;
        if (suggestServer) {
            statusHtml += ` <button onclick="useServerFeed()" style="margin-left:10px; padding:2px 8px; font-size:0.7rem; background:#3b82f6; color:white; border:none; border-radius:4px; cursor:pointer;">Try Server Camera</button>`;
        }

        aiStatus.innerHTML = statusHtml;
        addLogEntry(`⚠ ERROR: ${errorMsg}`, true);
        console.error("Full error:", err);
    }
}

function stopCamera() {
    const video = document.getElementById('videoElement');
    const aiStatus = document.getElementById('aiStatus');
    const startBtn = document.getElementById('startCamBtn');
    const switchBtn = document.getElementById('switchCamBtn');

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    isProcessing = false;
    video.srcObject = null;
    aiStatus.innerHTML = `<i class="fas fa-circle" style="color: #ef4444; font-size: 0.7rem;"></i> AI ENGINE: WAITING FOR CAMERA`;
    startBtn.innerText = "Start Camera";
    startBtn.style.background = "#22c55e";
    switchBtn.style.display = "none";

    // Clear processed frame
    document.getElementById('processedFrame').src = "";
    addLogEntry("Camera Stopped", false);
}

async function processLoop() {
    if (!isProcessing) return;

    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('canvasElement');
    const processedImg = document.getElementById('processedFrame');

    // DEBUG: Log readyState
    if (video.readyState < 2) { // HAVE_CURRENT_DATA
        console.log("Waiting for video data... readyState:", video.readyState);
        setTimeout(processLoop, 500);
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const base64Image = canvas.toDataURL('image/jpeg', 0.5); // Lower quality (0.5) for speed

    try {
        const response = await fetch(getApiUrl('/api/process_frame'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
        });

        if (!response.ok) {
            console.error("Server API Error:", response.status);
            processedImg.src = base64Image;
        } else {
            const data = await response.json();
            if (data.image) {
                processedImg.src = data.image;

                // Real-Time Feedback in Log
                if (data.person_count > 0) {
                    addLogEntry(`AI Detected: ${data.person_count} PERSON(S)`, false);
                }
            } else {
                processedImg.src = base64Image;
            }
        }
    } catch (err) {
        console.error("Frame processing error:", err);
        processedImg.src = base64Image; // Fallback
    }

    // Capture every 150ms for better responsiveness
    if (isProcessing) {
        setTimeout(processLoop, 150);
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    updateStats();
    updateChallans();

    // Check camera availability
    checkCameraStatus();

    const startBtn = document.getElementById('startCamBtn');
    const switchBtn = document.getElementById('switchCamBtn');

    if (startBtn) {
        startBtn.addEventListener('click', () => {
            const isServerFeed = document.getElementById('processedFrame').src.includes('video_feed');
            if (stream || isServerFeed) stopCamera();
            else startCamera(currentFacingMode);
        });
    }

    if (switchBtn) {
        switchBtn.addEventListener('click', () => {
            currentFacingMode = (currentFacingMode === 'user') ? 'environment' : 'user';
            startCamera(currentFacingMode);
        });
    }

    // Refresh data every 5 seconds for "Real-Time" feel
    setInterval(() => {
        updateStats();
        updateChallans();
    }, 5000);
});

// Check camera status on server
async function checkCameraStatus() {
    try {
        const response = await fetch(getApiUrl('/api/camera-status'));
        if (!response.ok) throw new Error('Failed to check camera status');

        const data = await response.json();
        console.log('[Camera Status]', data);

        if (data.camera_available) {
            addLogEntry('✓ Server Camera: Available', false);
        } else {
            addLogEntry('⚠ Server Camera: Not Detected (Using Browser Access)', false);
        }
    } catch (err) {
        console.log('Camera status check unavailable:', err);
    }
}
