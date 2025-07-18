import torch
import torchvision.transforms as transforms
import cv2
import numpy as np
from pytorchvideo.models.hub.slowfast import slowfast_r50
from torchvision.transforms import Normalize
from collections import deque

# Define custom class labels for classroom activities
CLASS_LABELS = [
    "sleeping", "dancing", "using mobile phone", "talking", "not attending class",
    "drinking water", "listening to class", "writing", "reading"
]

# Load the SlowFast model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = slowfast_r50(pretrained=True).eval().to(device)

# If you have a fine-tuned model, load it here (uncomment and update path)
# model.load_state_dict(torch.load("path_to_finetuned_model.pth"))
# model.eval()

# Define transformations for input frames
transform = transforms.Compose([
    transforms.ToTensor(),
    Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225])
])

# OpenCV Video Capture (0 for default webcam)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Error: Could not open webcam.")

# Frame queues for SlowFast
frame_queue = deque(maxlen=32)  # Fast pathway
slow_frame_queue = deque(maxlen=8)  # Slow pathway

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Resize and transform frame
    frame_resized = cv2.resize(frame_rgb, (224, 224))
    frame_tensor = transform(frame_resized)

    # Add to queues
    frame_queue.append(frame_tensor)
    if len(frame_queue) % 4 == 0:
        slow_frame_queue.append(frame_tensor)

    # Process when enough frames are collected
    if len(frame_queue) == 32 and len(slow_frame_queue) == 8:
        # Prepare input tensors
        fast_tensor = torch.stack(list(frame_queue), dim=1).unsqueeze(0)  # Shape: (1, 3, 32, 224, 224)
        slow_tensor = torch.stack(list(slow_frame_queue), dim=1).unsqueeze(0)  # Shape: (1, 3, 8, 224, 224)

        # Move to device
        fast_tensor = fast_tensor.to(device)
        slow_tensor = slow_tensor.to(device)

        # Model inference
        with torch.no_grad():
            preds = model([slow_tensor, fast_tensor])  # SlowFast input format
            probs = torch.softmax(preds, dim=1)
            top_prob, top_label = torch.max(probs, dim=1)

        # Map prediction to label (assuming fine-tuned model has correct num_classes)
        # If using pre-trained Kinetics model, this will need adjustment
        predicted_label = CLASS_LABELS[top_label.item() % len(CLASS_LABELS)]
        confidence = top_prob.item() * 100

        # Display result on frame
        text = f"Activity: {predicted_label} ({confidence:.1f}%)"
        cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show video feed
    cv2.imshow("Student Activity Recognition", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()