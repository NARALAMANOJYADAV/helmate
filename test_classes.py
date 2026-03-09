from ultralytics import YOLO
import sys
import pprint

try:
    model1 = YOLO('yolo12n.pt')
    print("yolo12n.pt classes:")
    print(list(model1.names.values())[:10]) 
except Exception as e:
    print(e)
    
try:
    model2 = YOLO('yolov12.pt')
    print("yolov12.pt classes:")
    print(list(model2.names.values())[:10])
except Exception as e:
    print(e)
