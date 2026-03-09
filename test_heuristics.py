import cv2
import numpy as np

with open("out_heuristic2.txt", "w") as f:
    def test_heuristic(img_path):
        frame = cv2.imread(img_path)
        if frame is None:
            f.write(f"FAILED {img_path}\n")
            return
        h, w = frame.shape[:2]
        x1, x2 = w//4, 3*w//4
        y1, y2 = 0, h//3
        head_roi = frame[y1:y2, x1:x2]
        head_roi = cv2.resize(head_roi, (100, 80))
        
        gray = cv2.cvtColor(head_roi, cv2.COLOR_BGR2GRAY)
        
        t_0 = cv2.Laplacian(gray, cv2.CV_64F).var()
        t_3 = cv2.Laplacian(cv2.GaussianBlur(gray, (3,3), 0), cv2.CV_64F).var()
        t_5 = cv2.Laplacian(cv2.GaussianBlur(gray, (5,5), 0), cv2.CV_64F).var()
        
        ycrcb = cv2.cvtColor(head_roi, cv2.COLOR_BGR2YCrCb)
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        skin_mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
        s = (np.sum(skin_mask > 0) / skin_mask.size) * 100
        
        frontal_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = frontal_cascade.detectMultiScale(gray, 1.1, 3)
        
        f.write(f"{img_path}: T0={t_0:.1f}, T3={t_3:.1f}, T5={t_5:.1f}, S={s:.1f}%, Faces={len(faces)}\n")

    for file in ["hel.jpg", "no_helmet_ref.jpg", "no helmate.webp"]:
        test_heuristic(file)
