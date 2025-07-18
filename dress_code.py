import cv2
import os
import time
import numpy as np
import torch
from ultralytics import YOLO
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='dress_code_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
DATASET_PATH = "dataset"
IMAGE_PATH = os.path.join(DATASET_PATH, "images", "train")
LABEL_PATH = os.path.join(DATASET_PATH, "labels", "train")
MODEL_PATH = "./runs/detect/train/weights/best.pt"
DATA_YAML = "./data.yaml"
CLASSES = ["casual", "formal", "sportswear", "traditional"]  # Update based on your classes

# Create directories
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(LABEL_PATH, exist_ok=True)

# Load model
def load_model():
    if os.path.exists(MODEL_PATH):
        print(f"Loading trained model from {MODEL_PATH}")
        return YOLO(MODEL_PATH)
    else:
        print("No trained model found. Initializing YOLOv11n.")
        return YOLO("yolov11n.pt")  # Use nano model for speed; switch to 'yolov11m.pt' for better accuracy

model = load_model()

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    logging.error("Failed to open webcam")
    print("Error: Could not open webcam")
    exit()

# Image counter for saving
image_count = len(os.listdir(IMAGE_PATH))

def save_annotation(box, frame_shape, label_path, class_id):
    """Save YOLO-format annotation for a detected bounding box."""
    x1, y1, x2, y2 = box
    width, height = frame_shape[1], frame_shape[0]
    x_center = ((x1 + x2) / 2) / width
    y_center = ((y1 + y2) / 2) / height
    box_width = (x2 - x1) / width
    box_height = (y2 - y1) / height
    with open(label_path, "w") as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")

# Main loop for real-time detection
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture frame")
        break

    # Perform detection
    results = model(frame, conf=0.4, iou=0.5)  # Adjusted thresholds for better detection

    # Process results
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = f"{CLASSES[cls]}: {conf:.2f}"
            
            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Log detection
            logging.info(f"Detected {CLASSES[cls]} with confidence {conf:.2f} at ({x1}, {y1}, {x2}, {y2})")

    # Display frame
    cv2.imshow("Dress Code Analyzer", frame)

    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Quit
        break
    elif key == ord('s'):  # Save image and annotation
        try:
            label_name = input(f"Enter label ({', '.join(CLASSES)}): ").strip().lower()
            if label_name not in CLASSES:
                print(f"Invalid label. Choose from {CLASSES}")
                continue

            class_id = CLASSES.index(label_name)
            img_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_count}.jpg"
            img_path = os.path.join(IMAGE_PATH, img_name)
            label_path = os.path.join(LABEL_PATH, f"{img_name[:-4]}.txt")

            # Save image
            cv2.imwrite(img_path, frame)
            print(f"Saved image: {img_path}")

            # Save dummy annotation (full frame); adjust if specific box is needed
            save_annotation([0, 0, frame.shape[1], frame.shape[0]], frame.shape, label_path, class_id)
            print(f"Saved annotation: {label_path}")
            
            image_count += 1
            logging.info(f"Saved image {img_name} with label {label_name}")
        except Exception as e:
            logging.error(f"Error saving image/label: {str(e)}")
            print(f"Error: {str(e)}")

# Release resources
cap.release()
cv2.destroyAllWindows()

# Optional: Train model if dataset has new images
def train_model():
    print("Starting model training...")
    try:
        model.train(
            data=DATA_YAML,
            epochs=100,
            imgsz=640,
            batch=16,
            optimizer="AdamW",  # Modern optimizer for better convergence
            lr0=0.001,  # Initial learning rate
            patience=50,
            conf=0.4,
            iou=0.5,
            device=0 if torch.cuda.is_available() else "cpu",  # Use GPU if available
            augment=True  # Enable data augmentation
        )
        print("Training completed.")
        logging.info("Model training completed successfully")
    except Exception as e:
        logging.error(f"Training failed: {str(e)}")
        print(f"Training error: {str(e)}")

# Uncomment to train after collecting data
# train_model()