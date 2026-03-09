import cv2
import base64
import os
import json
import time
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Challan
from backend.detector import HelmetDetector

# Initialize detector
detector = HelmetDetector()

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        # Simple auth to match original Flask logic
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "MANOJ" and password == "manoj@64":
            # For simplicity, we'll use a session flag like Flask
            request.session['logged_in'] = True
            return redirect('dashboard_home')
        else:
            return render(request, 'login.html', {'error': "Access Denied: Invalid Credentials"})
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('index')

def session_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('logged_in'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@session_login_required
def dashboard_home(request):
    return render(request, 'dash-home.html')

@session_login_required
def violations_history(request):
    return render(request, 'dashboard.html')

@session_login_required
def statistics(request):
    return render(request, 'graph.html')

@session_login_required
def location(request):
    return render(request, 'location.html')

@session_login_required
def messages(request):
    return render(request, 'messages.html')

@session_login_required
def about(request):
    return render(request, 'about.html')

@session_login_required
def files_view(request):
    return render(request, 'files.html')

@session_login_required
def notifications(request):
    return render(request, 'notification.html')

@session_login_required
def get_stats(request):
    today = Challan.objects.filter(timestamp__date=timezone.now().date()).count()
    total = Challan.objects.count()
    
    ai_status = "ACTIVE" if detector.model else "Mock Mode (Model Error)"
    model_name = os.path.basename(detector.model_path) if detector.model_path else "Not Loaded"
    
    return JsonResponse({
        "today_violations": today, 
        "total_challans": total, 
        "revenue": total * 500,
        "ai_status": ai_status,
        "model_name": model_name
    })

@session_login_required
def get_challans(request):
    challans = Challan.objects.all().order_by('-timestamp')
    data = []
    for c in challans:
        data.append({
            "id": c.id,
            "vehicle_no": c.vehicle_no,
            "timestamp": c.timestamp.isoformat(),
            "image_path": c.image_path,
            "status": c.status
        })
    return JsonResponse(data, safe=False)

@session_login_required
def camera_status(request):
    camera_available = False
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            camera_available = True
        else:
            cap = cv2.VideoCapture(0)
            camera_available = cap.isOpened()
        if cap:
            cap.release()
    except:
        pass
    
    return JsonResponse({
        "camera_available": camera_available,
        "opencv_available": cv2 is not None,
        "server_status": "online",
        "message": "Camera is ready for use" if camera_available else "Camera not detected."
    })

@csrf_exempt
@session_login_required
def process_frame_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            img_data = data['image'].split(',')[1]
            import numpy as np
            img_bytes = base64.b64decode(img_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            processed_frame, person_count = detector.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            processed_img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return JsonResponse({
                "image": f"data:image/jpeg;base64,{processed_img_base64}",
                "person_count": person_count,
                "success": True
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST required"}, status=405)

@csrf_exempt
@session_login_required
def delete_violation(request, challan_id):
    if request.method == 'DELETE':
        try:
            Challan.objects.filter(id=challan_id).delete()
            return JsonResponse({"success": True})
        except:
            return JsonResponse({"success": False}, status=500)
    return JsonResponse({"error": "DELETE required"}, status=405)

import threading

class VideoCaptureThread:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

def gen_frames():
    # PERFORMANCE: Threaded Capture
    camera = VideoCaptureThread().start()
    frame_count = 0
    
    while True:
        success, frame = camera.read()
        if not success or frame is None:
            time.sleep(0.01)
            continue
            
        frame_count += 1
        # PERFORMANCE: Frame Skipping (Process every 3rd frame)
        if frame_count % 3 == 0:
            processed_frame, _ = detector.process_frame(frame)
        else:
            # For skipped frames, just add "Optimizing..." text or show raw
            processed_frame = frame
            
        ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
               
    camera.stop()

@session_login_required
def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
