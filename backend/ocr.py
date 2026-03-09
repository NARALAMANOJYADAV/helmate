try:
    import cv2
except ImportError:
    cv2 = None
import random

class OCRProcessor:
    def __init__(self):
        # Initialize Tesseract or EasyOCR here
        pass

    def read_plate(self, image):
        # Mock OCR logic
        states = ['KA', 'MH', 'TN', 'DL', 'TS']
        num1 = random.randint(10, 99)
        char = random.choice(['AB', 'CD', 'EF', 'GH', 'JK'])
        num2 = random.randint(1000, 9999)
        
        return f"{random.choice(states)}-{num1}-{char}-{num2}"
