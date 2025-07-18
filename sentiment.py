import cv2
import os
import argparse
import sys
import numpy as np
from deepface import DeepFace

def highlightFace(net, frame, conf_threshold=0.7):
    """
    Detect faces in the frame using OpenCV DNN-based face detector.
    Returns the frame with bounding boxes and a list of face coordinates.
    """
    frameOpencvDnn = frame.copy()
    frameHeight, frameWidth = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    faceBoxes = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            faceBoxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)

    return frameOpencvDnn, faceBoxes

def map_nuanced_emotions(emotion_probs):
    """
    Map DeepFace's basic emotions to nuanced emotions based on probability thresholds.
    This is a heuristic approach and can be customized further.
    """
    dominant_emotion = max(emotion_probs, key=emotion_probs.get)
    emotion_scores = emotion_probs.copy()

    # Example mappings (adjust thresholds as needed)
    if dominant_emotion == "sad" and emotion_scores.get("neutral", 0) > 0.2:
        return "lonely"
    elif dominant_emotion == "happy" and emotion_scores.get("surprise", 0) > 0.15:
        return "romantic"
    elif dominant_emotion == "fear" and emotion_scores.get("sad", 0) > 0.25:
        return "scary"
    elif dominant_emotion == "sad" and emotion_scores.get("angry", 0) > 0.2:
        return "gloomy"
    else:
        return dominant_emotion  # Fallback to basic emotion

def analyze_face(face_img):
    """
    Analyze the face for age, gender, and emotion using DeepFace.
    Returns a dictionary with predictions.
    """
    try:
        result = DeepFace.analyze(face_img, actions=['age', 'gender', 'emotion'], enforce_detection=False)
        result = result[0]  # DeepFace returns a list of results

        # Extract predictions
        age = result['age']
        gender = result['dominant_gender']
        emotion_probs = result['emotion']
        emotion = map_nuanced_emotions(emotion_probs)

        return {
            'age': age,
            'gender': gender,
            'emotion': emotion
        }
    except Exception as e:
        print(f"Error analyzing face: {e}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, help="Path to input image file")
    args = parser.parse_args()

    # Define model file paths for face detection
    base_path = "models/"  # Adjust to your model directory
    faceProto = os.path.join(base_path, "opencv_face_detector.pbtxt")
    faceModel = os.path.join(base_path, "opencv_face_detector_uint8.pb")

    # Load the face detection model
    faceNet = cv2.dnn.readNet(faceModel, faceProto)

    # Check if image is provided, otherwise use webcam
    if args.image is None:
        print("No image path provided. Using webcam...")
        video = cv2.VideoCapture(0)
    else:
        if not os.path.exists(args.image):
            print(f"Error: The file {args.image} does not exist.")
            sys.exit(1)
        video = cv2.VideoCapture(args.image)

    padding = 20

    while cv2.waitKey(1) < 0:
        hasFrame, frame = video.read()
        if not hasFrame:
            cv2.waitKey()
            break

        # Detect faces
        resultImg, faceBoxes = highlightFace(faceNet, frame)
        if not faceBoxes:
            print("No face detected")
            cv2.imshow("Age and Emotion Detection", resultImg)
            continue

        for faceBox in faceBoxes:
            # Extract face ROI
            x1, y1, x2, y2 = faceBox
            face = frame[max(0, y1 - padding):min(y2 + padding, frame.shape[0] - 1),
                         max(0, x1 - padding):min(x2 + padding, frame.shape[1] - 1)]

            # Analyze face for age, gender, and emotion
            analysis = analyze_face(face)
            if analysis is None:
                continue

            # Extract results
            age = analysis['age']
            gender = analysis['gender']
            emotion = analysis['emotion']

            # Display results
            label = f"{gender}, {age}, {emotion}"
            cv2.putText(resultImg, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Age and Emotion Detection", resultImg)

    # Cleanup
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()