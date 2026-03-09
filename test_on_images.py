import cv2
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from detector import HelmetDetector

def test_on_images():
    detector = HelmetDetector()
    images = [
        "hel.jpg",
        "hel1.jpg",
        "hel not used.jpg",
        "no helmate.webp",
        "no_helmet_ref.jpg"
    ]
    
    for img_path in images:
        if not os.path.exists(img_path):
            continue
        
        frame = cv2.imread(img_path)
        if frame is None:
            continue
            
        print(f"Testing {img_path}...")
        # Force a "person" detection at the center if YOLO fails or use YOLO
        processed, count = detector.process_frame(frame)
        
        # Save output
        out_name = f"result_{os.path.basename(img_path)}"
        cv2.imwrite(out_name, processed)
        print(f"  Saved to {out_name}")

if __name__ == "__main__":
    test_on_images()
