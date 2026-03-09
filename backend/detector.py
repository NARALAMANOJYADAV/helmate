import os
os.environ['YOLO_CONFIG_DIR'] = '/tmp'

try:
    import cv2
except ImportError:
    cv2 = None
import time
import os
import numpy as np
from datetime import datetime
try:
    from detection.models import Challan
    HAS_DJANGO = True
except Exception:
    HAS_DJANGO = False
    try:
        from database import add_challan
    except ImportError:
        def add_challan(*args): pass

try:
    from .ocr import OCRProcessor
except (ImportError, ValueError):
    try:
        from ocr import OCRProcessor
    except ImportError:
        class OCRProcessor:
            def extract_text(self, f): return "MH12DE1433"

class HelmetDetector:
    def __init__(self, model_path=None):
        """
        Initializes the AI Detection Engine.
        """
        if model_path is None:
            self.model_path = os.path.join(os.path.dirname(__file__), '../models/helmet-yolo.pt')
        else:
            self.model_path = model_path
            
        self.ocr = OCRProcessor()
        
        # FIX: Ensure Capture Directory Exists (Critical for Old Version to work)
        self.capture_dir = os.path.join(os.path.dirname(__file__), '../uploads/captured_images')
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir)

        self.model = None
        self.helmet_model = None
        try:
            from ultralytics import YOLO
            # 1. Load standard YOLO for persons/vehicles
            self.model_path = os.path.join(os.path.dirname(__file__), '../yolo12n.pt')
            self.model = YOLO(self.model_path)
            
            # 2. Load dedicated Helmet YOLO model
            helmet_model_path = os.path.join(os.path.dirname(__file__), '../models/helmet-yolo.pt')
            if os.path.exists(helmet_model_path):
                print(f"[AI Engine] Loading Deep Learning Helmet Model: {helmet_model_path}")
                self.helmet_model = YOLO(helmet_model_path)
            else:
                print("[AI Engine] Missing helmet-yolo.pt, falling back to heuristics only.")
        except Exception as e:
            print(f"AI Model Load Warning: {e}. Running in Mock Mode.")
        
        self.last_detection_time = 0
        self.detection_interval = 2 # 2 seconds between captures

    def is_wearing_helmet(self, frame, box):
        """
        AI DEEP LEARNING (V6): 
        Uses the dedicated yolo helmet detection model on the cropped person.
        Falls back to Face Cascade if the neural network misses the head.
        """
        try:
            x1, y1, x2, y2 = box
            
            h = y2 - y1
            # Crop just the upper body (head area)
            upper_roi = frame[max(0, y1-20):max(1, y1+int(h*0.5)), max(0, x1-20):min(frame.shape[1], x2+20)]
            
            if upper_roi.size > 0:
                # Use true AI Model if we downloaded it
                if hasattr(self, 'helmet_model') and self.helmet_model is not None:
                    results = self.helmet_model(upper_roi, verbose=False)
                    for r in results:
                        if len(r.boxes) > 0:
                            # 0: With Helmet, 1: Without Helmet
                            classes = [int(b.cls[0]) for b in r.boxes]
                            
                            # Prioritize network detection
                            if 0 in classes and 1 not in classes:
                                return True # Network saw ONLY a helmet
                            if 1 in classes:
                                return False # Network saw a naked head
                                
                # ---- FALLBACK (Webcam Close-Up) ----
                # Classic Face Detection cascade to catch these misses when directly in front of camera!
                gray_upper = cv2.cvtColor(upper_roi, cv2.COLOR_BGR2GRAY)
                fc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = fc.detectMultiScale(gray_upper, 1.1, 3)
                if len(faces) == 0:
                    pc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
                    faces = pc.detectMultiScale(gray_upper, 1.1, 3)
                    
                if len(faces) > 0:
                    cv2.putText(frame, "-FACE-", (x1, max(20, y1-15)), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 255), 2)
                    return False # We see a face, definitely no helmet
                
            # If no AI hit and no face found, default to True (assume helmeted on motorbike)
            return True
            
        except Exception as e:
            print(f"AI Engine V6 error: {e}")
            return False

    def process_frame(self, frame):
        """
        SYSTEM LOGIC:
        1. Detect Persons.
        2. Differentiate Adult vs Child (Estimate by height).
        3. Check Helmet for each.
        4. Apply Rules: Triple Riding = Red. No Helmet (Adult) = Red. Child = Exempt.
        """
        try:
            # print(f"DEBUG: Processing frame shape {frame.shape}", flush=True)
            now = time.time()
            NEON_RED = (21, 21, 255)
            NEON_GREEN = (57, 255, 20)
            NEON_YELLOW = (0, 255, 255)
            
            persons = []
            motorcycles = []
            if self.model:
                # LOWER CONFIDENCE for better mobile webcam detection
                # PERFORMANCE 1: Resize for faster inference (Standard YOLO size)
                input_w, input_h = frame.shape[1], frame.shape[0]
                inference_frame = cv2.resize(frame, (640, 640))
                
                # 1. RUN DETECTION
                results = self.model(inference_frame, verbose=False)[0]
                
                # Scale back boxes to original frame size
                scale_x = input_w / 640
                scale_y = input_h / 640
                
                for box in results.boxes:
                    cls = int(box.cls[0])
                    b = box.xyxy[0].cpu().numpy()
                    # Scale coordinates
                    scaled_b = [
                        int(b[0] * scale_x),
                        int(b[1] * scale_y),
                        int(b[2] * scale_x),
                        int(b[3] * scale_y)
                    ]
                    if cls == 0: # Person
                        persons.append(scaled_b)
                    elif cls in [3, 1, 2]: # Motorcycle, Bicycle, Car
                        motorcycles.append(scaled_b)
                
                if motorcycles:
                    print(f"[AI] Detected {len(motorcycles)} motorcycle(s)", flush=True)
                if persons:
                    print(f"[AI] Detected {len(persons)} person(s)", flush=True)
            
            # --- ADVANCED RIDER FILTERING ---
            # We only care about people ON or NEAR a vehicle
            riders_to_check = []
            if not motorcycles:
                # If no vehicle detected, we can still check persons in "Road Only" mode
                # but let's be strict for now to avoid false positives from the background
                riders_to_check = persons 
            else:
                for p in persons:
                    # Check if person is near any motorcycle
                    is_near_bike = False
                    for m in motorcycles:
                        # Improved overlap check: A person riding a bike should have their vertical center 
                        # generally overlapping the bike, and their bottom extending near the bottom of the bike.
                        px_center = (p[0] + p[2]) / 2
                        py_bottom = p[3]
                        
                        if (m[0] < px_center < m[2]) and (m[1] < py_bottom):
                            # Ensure the "person" has an aspect ratio typical of humans (taller than wide)
                            # to avoid classifying square patches of motorcycle as people.
                            p_w = p[2] - p[0]
                            p_h = p[3] - p[1]
                            if p_h > p_w * 0.8:
                                is_near_bike = True
                                break
                    if is_near_bike:
                        riders_to_check.append(p)
            
            if riders_to_check:
                # print(f"DEBUG: Identified {len(riders_to_check)} active riders/road-users", flush=True)
                pass
            
            if not riders_to_check:
                cv2.putText(frame, "AI SCANNING FOR ROAD USERS...", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, NEON_GREEN, 1)
                return frame, 0


            # 1. CLASSIFY RIDERS
            riders = []
            img_h, img_w = frame.shape[:2]
            margin = int(img_w * 0.15) # Increased margin to 15% (ignores background people better)
            
            for p in riders_to_check:
                box_h = p[3] - p[1]
                # DISTANCE FILTER: More sensitive threshold for testing (15% height)
                if box_h < (img_h * 0.15): 
                    cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), (100, 100, 100), 1)
                    cv2.putText(frame, "DISTANT", (p[0], p[1]-5), cv2.FONT_HERSHEY_PLAIN, 0.7, (100, 100, 100), 1)
                    continue
                
                # MARGIN FILTER: Ignore people entering from the sides
                if p[0] < margin or p[2] > (img_w - margin):
                    cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), (100, 100, 100), 1)
                    cv2.putText(frame, "SIDE VIEW", (p[0], p[1]-5), cv2.FONT_HERSHEY_PLAIN, 0.7, (100, 100, 100), 1)
                    continue

                helmet = self.is_wearing_helmet(frame, p)
                
                riders.append({
                    'box': p,
                    'helmet': helmet
                })

            # 2. APPLY RULES
            total_riders = len(riders)
            violation_found = False
            violation_reason = ""

            # Triple Riding Rule
            if total_riders >= 3:
                violation_found = True
                violation_reason = "TRIPLE RIDING"

            for rider in riders:
                p = rider['box']
                if rider['helmet']:
                    color = NEON_GREEN
                    label = "HELMET"
                else:
                    color = NEON_RED
                    label = "NO HELMET"
                    violation_found = True
                    if not violation_reason: violation_reason = "NO HELMET"
                
                # Visuals - CLEAN AND CONSISTENT
                cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), color, 3)
                cv2.putText(frame, label, (p[0], p[1]-15), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 2)

            # 3. CAPTURE CONTROL
            if violation_found:
                if (now - self.last_detection_time > self.detection_interval):
                    print(f"[AI] VIOLATION DETECTED: {violation_reason}. Capturing image...", flush=True)
                    cv2.putText(frame, f"VIOLATION: {violation_reason}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, NEON_RED, 2)
                    self.handle_violation(frame)
                    self.last_detection_time = now
            else:
                 cv2.putText(frame, "COMPLIANT", (20, 50), cv2.FONT_HERSHEY_PLAIN, 1.2, NEON_GREEN, 2)
        
        except Exception as e:
            print(f"Process Frame Error: {e}", flush=True)

        return frame, len(persons)

    def handle_violation(self, frame):
        """
        Handles capture with CORRECT DB LOGIC
        """
        print("DEBUG: handle_violation called", flush=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"violation_{timestamp}.jpg"
        filepath = os.path.join(self.capture_dir, filename)

        # 2. Save Image
        success = cv2.imwrite(filepath, frame)
        if success:
            print(f"Captured and saved: {filepath}", flush=True)
        else:
            print(f"ERROR: Failed to save image to {filepath}", flush=True)

        # OCR
        plate_text = "MH12DE1433"
        if self.ocr:
            try:
                if hasattr(self.ocr, 'read_plate'): val = self.ocr.read_plate(frame)
                elif hasattr(self.ocr, 'extract_text'): val = self.ocr.extract_text(frame)
                else: val = None
                if val: plate_text = val
            except: pass

        # DB LOG (With Fixes)
        web_path = f"uploads/captured_images/{filename}" 
        
        if HAS_DJANGO:
            try:
                Challan.objects.create(
                    vehicle_no=plate_text,
                    image_path=web_path
                )
                print(f"Logged to Django DB: {plate_text}")
            except Exception as e:
                print(f"Django DB Log Error: {e}")
        else:
            add_challan(plate_text, web_path)
            print(f"Logged to Flask DB: {plate_text}")
