import cv2
import numpy as np
import os

def analyze(img_path):
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return
    
    frame = cv2.imread(img_path)
    if frame is None:
        print(f"Could not read: {img_path}")
        return
    
    # Simulate the head crop logic
    h, w, _ = frame.shape
    # Usually we crop the top 20% of a person box. 
    # For these full images, let's just analyze the whole thing or a central crop.
    # But since these are often close-ups, we'll just use the whole image.
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    edges = cv2.Canny(gray, 50, 150)
    edge_density = (np.sum(edges > 0) / edges.size) * 100
    
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    highlight_pixels = (np.sum(thresh > 0) / thresh.size) * 100
    
    # Skin Detection (YCrCb method is robust)
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    lower_skin = np.array([0, 133, 77], dtype=np.uint8)
    upper_skin = np.array([255, 173, 127], dtype=np.uint8)
    skin_mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
    skin_pixels = (np.sum(skin_mask > 0) / skin_mask.size) * 100
    
    print(f"Image: {img_path}")
    print(f"  Laplacian Var: {lap_var:.2f}")
    print(f"  Edge Density: {edge_density:.2f}%")
    print(f"  Highlight %: {highlight_pixels:.2f}%")
    print(f"  Skin Pixels %: {skin_pixels:.2f}%")
    print("-" * 30)

images = [
    "hel.jpg",
    "hel1.jpg",
    "hel not used.jpg",
    "no helmate.webp",
    "no_helmet_ref.jpg"
]

for img in images:
    analyze(img)
