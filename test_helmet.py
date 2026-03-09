from ultralytics import YOLO
import sys

try:
    model = YOLO('../models/helmet-yolo.pt')
    results = model('hel.jpg')
    for r in results:
        print(r.boxes.xyxy)
        print(r.boxes.cls)
        print(r.boxes.conf)
except Exception as e:
    print(e)
