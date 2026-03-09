import cv2
import numpy as np
import pprint

images = ["hel.jpg", "hel1.jpg", "no_helmet_ref.jpg", "no helmate.webp"]

results = {}

for img_path in images:
    frame = cv2.imread(img_path)
    if frame is None:
        continue
    
    h, w = frame.shape[:2]
    # Simulate a full person crop from YOLO
    # for these we just evaluate the top 50%
    roi = frame[0:int(h*0.5), :]
    
    # Let's compute statistics in different zones
    z_top = roi[0:int(roi.shape[0]*0.4), :]       # Top 40% (Forehead/Hair/Helmet Top)
    z_mid = roi[int(roi.shape[0]*0.4):int(roi.shape[0]*0.8), :] # Mid 40% (Face/Visor)
    
    def get_stats(img):
        if img.size == 0: return 0, 0, 0, 0
        img = cv2.resize(img, (100, 80))
        blur = cv2.GaussianBlur(img, (3,3), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        
        # Skin Mask
        ycrcb = cv2.cvtColor(blur, cv2.COLOR_BGR2YCrCb)
        m_y = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
        m_h = cv2.inRange(hsv, np.array([0, 15, 60]), np.array([20, 255, 255]))
        skin = cv2.bitwise_or(m_y, m_h)
        s_pct = (np.sum(skin>0)/skin.size)*100
        
        # Texture
        t = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness (Max and Mean)
        v_mean = np.mean(hsv[:,:,2])
        v_max = np.percentile(hsv[:,:,2], 95)
        
        return s_pct, t, v_mean, v_max

    s_t, t_t, vm_t, vmx_t = get_stats(z_top)
    s_m, t_m, vm_m, vmx_m = get_stats(z_mid)
    
    results[img_path] = {
        "TOP_S": round(s_t, 1),
        "TOP_T": round(t_t, 1),
        "TOP_VMEAN": round(vm_t, 1),
        "TOP_VMAX": round(vmx_t, 1),
        "MID_S": round(s_m, 1),
        "MID_T": round(t_m, 1),
        "MID_VMEAN": round(vm_m, 1),
        "MID_VMAX": round(vmx_m, 1)        
    }

with open('out_h4.txt', 'w', encoding='utf-8') as f:
    f.write(pprint.pformat(results))

