import cv2
import numpy as np

def analyze(img, label):
    frame = cv2.imread(img)
    if frame is None: return
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    t = cv2.Laplacian(gray, cv2.CV_64F).var()
    edges = cv2.Canny(gray, 30, 100)
    e = (np.sum(edges > 0) / edges.size) * 100
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    h = (np.sum(thresh > 0) / thresh.size) * 100
    print(f"{label} -> T={t:.1f} E={e:.1f}% H={h:.1f}%")

analyze("hel.jpg", "HELMET_NEW_1")
analyze("hel1.jpg", "HELMET_NEW_2")
analyze("helmet_ref.jpg", "HELMET_OLD")
analyze("no helmate.webp", "NO_HELMET_NEW")
analyze("no_helmet_ref.jpg", "NO_HELMET_OLD")
analyze("hel not used.jpg", "HEL_NOT_USED")
