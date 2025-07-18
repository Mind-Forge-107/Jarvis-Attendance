from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import mysql.connector
from time import strftime
from datetime import datetime
import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch
import pickle
from sklearn.preprocessing import LabelEncoder
import os

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(20)

    MDLabel:
        text: "FACE RECOGNITION"
        halign: "center"
        theme_text_color: "Custom"
        text_color: 1, 0.5, 0, 1  # Orange color
        font_style: "H4"

    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        padding: dp(10)

        # Placeholder for left panel (if needed in future)
        MDBoxLayout:
            size_hint_x: 0.5
            md_bg_color: [1, 1, 1, 1]

        # Right panel with button
        MDBoxLayout:
            size_hint_x: 0.5
            md_bg_color: [1, 1, 1, 1]
            orientation: 'vertical'
            halign: "center"
            valign: "center"

            MDRaisedButton:
                text: "Face Recognition"
                on_release: app.face_recog()
                md_bg_color: [1, 0.75, 0.8, 1]  # Pink color
                size_hint: None, None
                size: dp(200), dp(40)
'''

class FaceRecognitionApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(keep_all=False, device='cpu')  # Set device='cuda' if you have a GPU
        # Initialize FaceNet for embedding generation
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval()
        self.facenet.to('cpu')  # Set device='cuda' if you have a GPU
        # Load the trained SVM classifier
        try:
            with open("models/classifier.pkl", 'rb') as f:
                self.clf = pickle.load(f)
        except Exception as e:
            print(f"Error loading classifier: {e}")
            self.clf = None
        # Load the label encoder
        try:
            with open("models/label_encoder.pkl", 'rb') as f:
                self.label_encoder = pickle.load(f)
        except Exception as e:
            print(f"Error loading label encoder: {e}")
            self.label_encoder = None

    def build(self):
        self.root = Builder.load_string(KV)
        return self.root

    def mark_attendance(self, i, r, n, d):
        # Define the CSV file path
        csv_file = "attendance.csv"
        
        # Check if the file exists; if not, create it with headers
        if not os.path.exists(csv_file):
            with open(csv_file, "w", newline="\n") as f:
                f.write("Student_id,Roll,Name,Department,Time,Date,Status\n")

        # Read existing entries to check for duplicates
        name_list = []
        try:
            with open(csv_file, "r", newline="\n") as f:
                myDataList = f.readlines()
                for line in myDataList[1:]:  # Skip the header row
                    if line.strip():  # Ignore empty lines
                        entry = line.split(",")
                        if len(entry) > 0:
                            name_list.append(entry[0])  # Student_id
        except Exception as e:
            print(f"Error reading attendance.csv: {e}")
            return

        # Check for duplicates and log attendance
        if (i not in name_list) and (r not in name_list) and (n not in name_list) and (d not in name_list):
            now = datetime.now()
            d1 = now.strftime("%d/%m/%Y")
            dtString = now.strftime("%H:%M:%S")
            if i == "Unknown" and d == "Unknown" and r == "Unknown" and n == "Unknown":
                return
            else:
                try:
                    with open(csv_file, "a", newline="\n") as f:
                        f.writelines(f"{i},{r},{n},{d},{dtString},{d1},Present\n")
                except Exception as e:
                    print(f"Error writing to attendance.csv: {e}")
                    self.show_alert("Error", f"Failed to log attendance: {str(e)}")

    def face_recog(self):
        if self.clf is None or self.label_encoder is None:
            self.show_alert("Error", "Failed to load classifier or label encoder. Please train the model first.")
            return

        video_cap = cv2.VideoCapture(0)

        if not video_cap.isOpened():
            self.show_alert("Error", "Cannot access the camera")
            return

        while True:
            ret, img = video_cap.read()
            if not ret:
                print("Failed to capture frame from the camera.")
                break

            # Convert frame to RGB for MTCNN
            frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)

            # Detect faces using MTCNN
            boxes, _ = self.mtcnn.detect(frame_pil)

            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box)
                    if x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
                        continue

                    # Extract the face region
                    face = img[y1:y2, x1:x2]
                    if face.size == 0:
                        continue

                    # Resize face to 160x160 (required by FaceNet)
                    face_resized = cv2.resize(face, (160, 160))
                    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                    face_pil = Image.fromarray(face_rgb)

                    # Generate embedding using FaceNet
                    face_tensor = self.mtcnn(face_pil)
                    if face_tensor is None:
                        continue
                    face_tensor = face_tensor.unsqueeze(0)  # Add batch dimension
                    with torch.no_grad():
                        embedding = self.facenet(face_tensor).cpu().numpy()

                    # Predict the student ID using the SVM classifier
                    predicted_label = self.clf.predict(embedding)[0]
                    confidence = self.clf.predict_proba(embedding)[0][predicted_label] * 100  # Confidence score
                    student_id = self.label_encoder.inverse_transform([predicted_label])[0]
                    print(f"Predicted Student_id: {student_id}, Confidence: {confidence:.2f}%")

                    # Fetch student details from the database
                    try:
                        conn = mysql.connector.connect(host="localhost", username="root", password="root", database="jarvis")
                        mycur = conn.cursor()
                        mycur.execute("SELECT Student_id, Name, Roll, Dep FROM student WHERE TRIM(UPPER(Student_id))=TRIM(UPPER(%s))", (student_id,))
                        row = mycur.fetchone()
                        print(f"Database query result: {row}")  # Debug: Check the full row

                        if row:
                            i, n, r, d = row
                            i = i if i is not None else "Unknown"
                            n = n if n is not None else "Unknown"
                            r = r if r is not None else "Unknown"
                            d = d if d is not None else "Unknown"
                        else:
                            print(f"No matching record found for Student_id: {student_id}")
                            i, n, r, d = student_id, "Unknown", "Unknown", "Unknown"

                        # Display the result if confidence is high
                        if confidence > 80:
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            cv2.putText(img, f"ID: {i}", (x1, y1 - 75), cv2.FONT_HERSHEY_COMPLEX, 0.8, (73, 61, 158), 2)
                            cv2.putText(img, f"Roll: {r}", (x1, y1 - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (73, 61, 158), 2)
                            cv2.putText(img, f"Name: {n}", (x1, y1 - 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (73, 61, 158), 2)
                            cv2.putText(img, f"Department: {d}", (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (73, 61, 158), 2)
                            self.mark_attendance(i, r, n, d)
                        else:
                            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
                            cv2.putText(img, "Unknown face", (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 3)

                        conn.close()

                    except mysql.connector.Error as e:
                        print(f"Database error: {e}")
                        self.show_alert("Database Error", f"Failed to fetch student details: {str(e)}")
                        i, n, r, d = student_id, "Unknown", "Unknown", "Unknown"

            cv2.imshow("Welcome to Face Recognition", img)

            if cv2.waitKey(1) == 13:  # Press Enter to exit
                break

        video_cap.release()
        cv2.destroyAllWindows()

    def show_alert(self, title, message):
        from kivymd.uix.dialog import MDDialog
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == "__main__":
    FaceRecognitionApp().run()