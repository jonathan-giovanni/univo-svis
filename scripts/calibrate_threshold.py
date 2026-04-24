from ultralytics import YOLO
import cv2
import os
from pathlib import Path

def calibrate():
    model_path = "models/yolo/yolo11n.pt"
    dataset_val = "/Users/admin/Documents/datasets/safety-vest-data-yolo-v1/valid/images"
    model = YOLO(model_path)
    
    thresholds = [0.25]
    
    # Take first 5 images from val set
    images = sorted([f for f in os.listdir(dataset_val) if f.endswith(('.png', '.jpg', '.jpeg'))])[:5]
    
    print(f"--- Calibrating Model: {model_path} ---")
    for thresh in thresholds:
        total_detections = 0
        print(f"\nTesting Threshold: {thresh}")
        for img_name in images:
            img_path = os.path.join(dataset_val, img_name)
            results = model.predict(source=img_path, conf=thresh, verbose=False)
            count = len(results[0].boxes)
            total_detections += count
            print(f"  {img_name}: {count} vests")
        print(f"TOTAL detections at {thresh}: {total_detections}")

if __name__ == "__main__":
    calibrate()
