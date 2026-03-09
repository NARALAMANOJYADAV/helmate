from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
import os
import sqlite3
import sys
import functools
import time
import base64
from io import BytesIO
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None
    print("WARNING: OpenCV not found. Camera features will be disabled.")

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

TEMPLATE_DIR = os.path.normpath(os.path.join(BASE_DIR, '../frontend'))
STATIC_DIR = os.path.normpath(os.path.join(BASE_DIR, '../frontend'))

app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR,
            static_url_path='')

# Manual CORS and Session fix for cross-port support
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    # Enable camera/microphone permissions via Permissions-Policy
    response.headers['Permissions-Policy'] = 'camera=(self), microphone=(self), geolocation=(self)'
    # For older browsers, add Feature-Policy
    response.headers['Feature-Policy'] = 'camera \'self\'; microphone \'self\'; geolocation \'self\''
    return response

# For session security
app.secret_key = 'smart_helmet_secret_key_123'
app.config['SESSION_COOKIE_NAME'] = 'helmate_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 # 1 hour

@app.before_request
def make_session_permanent():
    session.permanent = True

# Specified Credentials
ADMIN_USER = "MANOJ"
ADMIN_PASS = "manoj@64"

UPLOAD_FOLDER = os.path.normpath(os.path.join(BASE_DIR, '../uploads/captured_images'))
DB_PATH = os.path.normpath(os.path.join(BASE_DIR, '../database/challans.db'))

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DB_FOLDER = os.path.dirname(DB_PATH)
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# Import local modules
try:
    from detector import HelmetDetector
    from database import init_db, get_all_challans, delete_challan
    detector = HelmetDetector()
except ImportError as e:
    print(f"Error loading backend modules: {e}")
    # Minimal fallback
    def init_db(): pass
    def get_all_challans(): return []
    class HelmetDetector:
        def process_frame(self, f): return f
    detector = HelmetDetector()

# Auth Decorator
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login.html')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            print(f"DEBUG: Login attempt for: {username}", flush=True)
            
            if username == ADMIN_USER and password == ADMIN_PASS:
                print("DEBUG: Login SUCCESS", flush=True)
                session['logged_in'] = True
                session.modified = True
                return redirect('/dash-home.html')
            else:
                print("DEBUG: Login FAILED", flush=True)
                return render_template('login.html', error="Access Denied: Invalid Credentials")
    except Exception as e:
        print(f"LOGIN ERROR: {e}", flush=True)
        return render_template('login.html', error="System Error: Please restart server")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/index.html')

@app.route('/index.html')
def index_alias():
    return render_template('index.html')

@app.route('/dashboard')
@app.route('/dash-home.html')
@login_required
def dashboard_home():
    return render_template('dash-home.html')

@app.route('/violations')
@app.route('/dashboard.html')
@login_required
def violations_history():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"Error loading violations page: {e}"

@app.route('/analytics')
@app.route('/graph.html')
@login_required
def statistics():
    return render_template('graph.html')

@app.route('/location')
@app.route('/location.html')
@login_required
def location():
    return render_template('location.html')

@app.route('/messages')
@app.route('/messages.html')
@login_required
def messages():
    return render_template('messages.html')

@app.route('/uploads/captured_images/<filename>')
def serve_image(filename):
    try:
        from flask import send_from_directory
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return f"Error opening image: {e}", 404


def gen_frames():
    # SIMULATION MODE: Default to True on Cloud servers (no physical camera)
    USE_REAL_CAMERA = os.environ.get("RENDER") is None
    
    cap = None
    if USE_REAL_CAMERA:
        print("[AI] Cloud Check: Enabling Physical Camera search...", flush=True)
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
    else:
        print("[AI] Cloud Environment Detected: Physical Camera disabled. Please use Browser Camera.", flush=True)
    
    if not USE_REAL_CAMERA or (cap is None or not cap.isOpened()):
        print("[AI] Entering Simulation Mode (No Camera Found)", flush=True)
        import numpy as np
        while True:
            # Create a simple placeholder frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "SIMULATION MODE ACTIVE", (20, 30), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 255), 1)
            cv2.putText(frame, "System Stable - No Camera", (20, 50), cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 200, 200), 1)
            
            # Still process for autonomous logic simulation
            detector.process_frame(frame)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
               break
            else:
                try:
                    processed_frame = detector.process_frame(frame)
                    ret, buffer = cv2.imencode('.jpg', processed_frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                except Exception as e:
                    print(f"Error processing frame: {e}")
                    continue
    except Exception as e:
         print(f"Camera stream error: {e}")
    finally:
         cap.release()

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera-status')
@login_required
def camera_status():
    """Check if camera is available and properly initialized"""
    try:
        # Skip physical check if on Render to avoid log spam
        if os.environ.get("RENDER"):
            return jsonify({
                "camera_available": False,
                "opencv_available": cv2 is not None,
                "server_status": "online",
                "message": "Render Cloud: Use 'Start Camera' button for Browser Access"
            })

        camera_available = False
        cap = None
        if cv2 is not None:
            # Try to open camera with different backends
            try:
                cap = cv2.VideoCapture(0)
                camera_available = cap.isOpened()
            except Exception as e:
                camera_available = False
        
        if cap is not None:
            cap.release()
        
        return jsonify({
            "camera_available": camera_available,
            "opencv_available": cv2 is not None,
            "server_status": "online",
            "message": "Camera is ready for use" if camera_available else "Camera not detected. Browser may still access it."
        })
    except Exception as e:
        return jsonify({
            "camera_available": False,
            "error": str(e)
        }), 500

@app.route('/api/challans')
@login_required
def get_challans():
    return jsonify(get_all_challans())

@app.route('/api/process_frame', methods=['POST'])
@login_required
def process_frame_api():
    """
    Handles frames sent from the browser (mobile/webcam).
    """
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({"error": "No image data"}), 400
        
        # 1. Decode base64
        try:
            img_data = data['image'].split(',')[1] # Remove header
            img_bytes = base64.b64decode(img_data)
        except Exception as e:
            print(f"Base64 Decode Error: {e}")
            return jsonify({"error": "Base64 decode failure"}), 400
        
        # 2. Convert to OpenCV format
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            print("ERROR: cv2.imdecode returned None")
            return jsonify({"error": "Invalid image"}), 400
            
        # 3. Process with AI
        processed_frame, person_count = detector.process_frame(frame)
        
        # 4. Encode back to base64
        ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ret:
            print("ERROR: cv2.imencode failed")
            return jsonify({"error": "Encode failure"}), 500
            
        processed_img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "image": f"data:image/jpeg;base64,{processed_img_base64}",
            "person_count": person_count,
            "success": True
        })
    except Exception as e:
        print(f"API Process Frame Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/challans/delete/<int:challan_id>', methods=['DELETE'])
@login_required
def delete_violation(challan_id):
    if delete_challan(challan_id):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Database error"}), 500

@app.route('/api/stats')
@login_required
def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM challans WHERE date(timestamp) = date('now')")
        today = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM challans")
        total = cursor.fetchone()[0]
        conn.close()
    except:
        today, total = 0, 0
    
    # Add AI Engine Status
    ai_status = "ACTIVE" if detector.model else "Mock Mode (Model Error)"
    model_name = os.path.basename(detector.model_path) if detector.model_path else "Not Loaded"
    
    return jsonify({
        "today_violations": today, 
        "total_challans": total, 
        "revenue": total * 500,
        "ai_status": ai_status,
        "model_name": model_name
    })

if __name__ == '__main__':
    print("=========================================")
    print("   HELMEE AI ENGINE INITIALIZING")
    print("=========================================")
    try:
        init_db()
        print("[SUCCESS] Database initialized.")
    except Exception as e:
        print(f"[ERROR] Database init failed: {e}")

    print(f"Login ID: {ADMIN_USER}")
    print(f"Password: {ADMIN_PASS}")
    
    try:
        print("\n[AI SYSTEM] Starting Helmet AI Server...")
        print(f" - Host: 0.0.0.0 (Global Access)")
        print(f" - Port: 10000")
        print(f" - Login ID: {ADMIN_USER}")
        print("-----------------------------------------")
        # RUN ON 0.0.0.0 to ensure both localhost and 127.0.0.1 work
        port = int(os.environ.get("PORT") or 10000)
        app.run(host='0.0.0.0', debug=False, port=port, threaded=True)
    except Exception as e:
        print(f"CRITICAL SERVER EXIT: {e}")
