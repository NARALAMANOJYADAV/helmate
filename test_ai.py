import os
import sys

try:
    from ultralytics import YOLO
    print("SUCCESS: Ultralytics imported.")
except ImportError:
    print("ERROR: Ultralytics not installed.")
    sys.exit(1)

model_path = os.path.join(os.getcwd(), 'yolov12.pt')
if not os.path.exists(model_path):
    print(f"ERROR: Model file not found at {model_path}")
    sys.exit(1)

try:
    model = YOLO(model_path)
    print("SUCCESS: Model loaded.")
    
    # Test inference with dummy black image
    import numpy as np
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    results = model(dummy_frame, verbose=False)
    print("SUCCESS: Inference worked.")
except Exception as e:
    print(f"ERROR: Model processing failed: {e}")
