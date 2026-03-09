# Camera Access Setup Guide

## Overview
The Helmet AI system now has enhanced camera access support for both server-side and browser-based camera input.

## What Was Enabled

### 1. **Browser Camera Permissions** 
   - Added comprehensive permission handling for camera access
   - Support for both front and back cameras (mobile devices)
   - Improved error messages for specific permission issues
   - Automatic permission status checking

### 2. **Backend Security Headers**
   - Added `Permissions-Policy` header to allow camera/microphone access
   - Added `Feature-Policy` header for backward compatibility
   - CORS headers configured to support camera streaming

### 3. **Camera Status Endpoint**
   - New `/api/camera-status` endpoint to check camera availability
   - Helps diagnose camera connectivity issues
   - Provides server-side and browser-side status

## How to Use Camera Access

### Windows Desktop
1. Start the Flask server: `python backend/app.py`
2. Open browser to: `http://localhost:5001`
3. Login with credentials (MANOJ / manoj@64)
4. Click **"Start Camera"** button on the dashboard
5. **Browser will prompt for camera permission** - Click "Allow"

### Mobile Device
1. Access the server from your phone on the same network
2. Navigate to the IP address and port (e.g., `http://192.168.x.x:5001`)
3. Login to dashboard
4. Click **"Start Camera"** button
5. Grant camera permission when prompted
6. Switch between front/back cameras using **"Switch Camera"** button

## Browser Requirements

✅ **Supported Browsers:**
- Google Chrome/Chromium (recommended)
- Mozilla Firefox
- Microsoft Edge
- Safari (iOS 11+)

❌ **Not Supported:**
- Internet Explorer

## Security Notes

- Camera access is **only available through HTTPS or localhost**
- All API endpoints are protected with login authentication
- Camera permissions are managed at the browser level (not by server)
- Users retain full control over camera access

## Troubleshooting

### "Camera Access Denied" Error
1. **Check browser permissions:**
   - Go to browser settings → Privacy & Security → Camera
   - Ensure localhost:5001 is allowed

2. **For Windows:**
   - Check Windows camera permissions: Settings → Privacy → Camera
   - Ensure your app has camera access enabled

3. **Try different browser:** Use Chrome if having issues with other browsers

4. **Clear browser cache:** Sometimes cached permissions cause issues
   - Press Ctrl+Shift+Delete and clear cache

### "No Camera Device Found"
- Verify your camera is connected and working
- Try using the camera in other applications first
- Restart the browser and the Flask server

### Camera Stops Working
1. Click "Stop Camera" then "Start Camera" again
2. Refresh the page and try again
3. Restart the Flask server: `python backend/app.py`

## Server-Side Camera (Optional)

If you have a USB camera connected to the server:

1. The system will automatically detect and use it
2. The `/video_feed` endpoint will stream the server camera
3. Browser-based camera and server camera can work simultaneously

To verify server camera status:
- Check Flask console output during startup
- Look for: `[AI] Initializing Camera...`

## API Endpoints

- **GET `/video_feed`** - MJPEG video stream from server camera
- **POST `/api/process_frame`** - Process frames from browser camera
- **GET `/api/camera-status`** - Check camera status
- **GET `/api/stats`** - Get system statistics including camera status

## Advanced Configuration

To modify camera constraints in `frontend/app.js`, line ~145:

```javascript
const constraints = {
    video: {
        facingMode: { ideal: facingMode },
        width: { ideal: 1280, min: 640 },      // Adjust resolution
        height: { ideal: 720, min: 480 }
    },
    audio: false  // Keep false unless microphone needed
};
```

## Next Steps

1. ✅ Start the server: `python backend/app.py`
2. ✅ Open dashboard and click "Start Camera"
3. ✅ Grant browser camera permission
4. ✅ System should now process video frames for helmet detection

---

For issues or questions, check the browser console (F12) for detailed error messages.
