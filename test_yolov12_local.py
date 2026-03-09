from ultralytics import YOLO
model = YOLO('yolov12.pt')
results = model('hel.jpg')
for r in results:
    print(r.boxes.cls)
    print(r.names)
