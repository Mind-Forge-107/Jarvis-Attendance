from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import mysql.connector
import cv2
import os
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import torch

# KV string with the current layout
KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: dp(10)
    spacing: 0

    # Top Section: Title and Buttons
    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(50)
        spacing: dp(10)

        MDLabel:
            text: "Student Attendance System"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0, 0.5, 0, 1
            font_style: "H4"

        MDBoxLayout:
            orientation: 'horizontal'
            size_hint_x: None
            width: dp(500)
            spacing: dp(5)
            padding: dp(5)

            MDRaisedButton:
                text: "Save"
                on_release: app.add_data()
            MDRaisedButton:
                text: "Update"
                on_release: app.update_data()
            MDRaisedButton:
                text: "Delete"
                on_release: app.delete_data()
            MDRaisedButton:
                text: "Reset"
                on_release: app.reset_data()
            MDRaisedButton:
                text: "Take Photo Sample"
                on_release: app.generate_dataset()

    # Main Content
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        padding: dp(10)

        # Left Panel: Student Details
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.5
            md_bg_color: [1, 1, 1, 1]
            padding: dp(10)
            spacing: dp(10)

            MDBoxLayout:
                orientation: 'vertical'
                md_bg_color: [0.9, 0.95, 0.9, 1]  # Pale green color
                radius: [20, 20, 20, 20]  # Rounded corners
                padding: dp(15)
                spacing: dp(15)

                MDLabel:
                    text: "Student Details"
                    halign: "center"
                    font_style: "H6"

                ScrollView:
                    do_scroll_x: False
                    do_scroll_y: True

                    MDGridLayout:
                        cols: 2
                        padding: dp(10)
                        spacing: dp(10)
                        size_hint_y: None
                        height: self.minimum_height

                        MDLabel:
                            text: "Department:"
                            size_hint_y: None
                            height: dp(40)
                        MDDropDownItem:
                            id: dep_dropdown
                            text: "Select Department"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Course:"
                            size_hint_y: None
                            height: dp(40)
                        MDDropDownItem:
                            id: course_dropdown
                            text: "Select Course"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Year:"
                            size_hint_y: None
                            height: dp(40)
                        MDDropDownItem:
                            id: year_dropdown
                            text: "Select Year"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Semester:"
                            size_hint_y: None
                            height: dp(40)
                        MDDropDownItem:
                            id: semester_dropdown
                            text: "Select Semester"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Student ID:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: std_id
                            hint_text: "e.g., VIT21CS030"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Student Name:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: std_name
                            hint_text: "Student Name"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Roll No:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: roll
                            hint_text: "Roll No"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Gender:"
                            size_hint_y: None
                            height: dp(40)
                        MDDropDownItem:
                            id: gender_dropdown
                            text: "Select Gender"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "DOB (YYYY-MM-DD):"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: dob
                            hint_text: "DOB (YYYY-MM-DD)"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Email:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: email
                            hint_text: "Email"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Phone No:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: phone
                            hint_text: "Phone No"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Address:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: address
                            hint_text: "Address"
                            size_hint_y: None
                            height: dp(40)

                        MDLabel:
                            text: "Teacher Name:"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: teacher
                            hint_text: "Teacher Name"
                            size_hint_y: None
                            height: dp(40)

        # Right Panel: Student Records
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.5
            md_bg_color: [1, 1, 1, 1]
            padding: dp(10)
            spacing: dp(10)

            MDBoxLayout:
                orientation: 'vertical'
                md_bg_color: [0.9, 0.95, 0.9, 1]  # Pale green color
                radius: [20, 20, 20, 20]  # Rounded corners
                padding: dp(15)
                spacing: dp(10)

                MDLabel:
                    text: "Student Records"
                    halign: "center"
                    font_style: "H6"

                MDLabel:
                    text: "Search By:"
                    halign: "left"

                MDGridLayout:
                    cols: 4
                    padding: dp(5)
                    spacing: dp(5)

                    MDDropDownItem:
                        id: search_dropdown
                        text: "Select"
                    MDTextField:
                        id: search_entry
                        hint_text: "Search..."
                    MDRaisedButton:
                        text: "Search"
                        on_release: app.search_data()
                    MDRaisedButton:
                        text: "Show All"
                        on_release: app.fetch_data()

            ScrollView:
                id: table_scroll
                MDBoxLayout:
                    id: table_content
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
'''

class StudentManagementApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(keep_all=False, device='cpu')  # Set device='cuda' if you have a GPU
        # Initialize FaceNet (InceptionResnetV1) for face embeddings
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval()  # Use VGGFace2 pre-trained model
        self.facenet.to('cpu')  # Set device='cuda' if you have a GPU

    def build(self):
        self.root = Builder.load_string(KV)
        self.initialize_dropdowns()
        self.fetch_data()
        return self.root

    def initialize_dropdowns(self):
        # Department
        dep_items = ["Select Department", "Computer Science", "Electrical", "Electronics", "Civil", "Mechanical"]
        self.dep_menu = MDDropdownMenu(
            caller=self.root.ids.dep_dropdown,
            items=[{"text": x, "viewclass": "OneLineListItem", "on_release": lambda x=x: self.set_dropdown_item(self.root.ids.dep_dropdown, x)} for x in dep_items],
            width_mult=4,
        )
        self.root.ids.dep_dropdown.on_release = lambda: self.dep_menu.open()

        # Course
        course_items = ["Select Course", "B.Tech", "BCA", "B.com"]
        self.course_menu = MDDropdownMenu(
            caller=self.root.ids.course_dropdown,
            items=[{"text": x, "viewclass": "OneLineListItem", "on_release": lambda x=x: self.set_dropdown_item(self.root.ids.course_dropdown, x)} for x in course_items],
            width_mult=4,
        )
        self.root.ids.course_dropdown.on_release = lambda: self.course_menu.open()

        # Year
        year_items = ["Select Year", "2021-2025", "2022-2026", "2023-2027", "2024-2028", "2025-2029"]
        self.year_menu = MDDropdownMenu(
            caller=self.root.ids.year_dropdown,
            items=[{"text": x, "viewclass": "OneLineListItem", "on_release": lambda x=x: self.set_dropdown_item(self.root.ids.year_dropdown, x)} for x in year_items],
            width_mult=4,
        )
        self.root.ids.year_dropdown.on_release = lambda: self.year_menu.open()

        # Semester
        semester_items = ["Select Semester", "Semester-1", "Semester-2", "Semester-3", "Semester-4", 
                         "Semester-5", "Semester-6", "Semester-7", "Semester-8"]
        self.semester_menu = MDDropdownMenu(
            caller=self.root.ids.semester_dropdown,
            items=[{"text": x, "viewclass": "OneLineListItem", "on_release": lambda x=x: self.set_dropdown_item(self.root.ids.semester_dropdown, x)} for x in semester_items],
            width_mult=4,
        )
        self.root.ids.semester_dropdown.on_release = lambda: self.semester_menu.open()

        # Gender
        gender_items = ["Select Gender", "Male", "Female", "Other"]
        self.gender_menu = MDDropdownMenu(
            caller=self.root.ids.gender_dropdown,
            items=[{"text": x, "viewclass": "OneLineListItem", "on_release": lambda x=x: self.set_dropdown_item(self.root.ids.gender_dropdown, x)} for x in gender_items],
            width_mult=4,
        )
        self.root.ids.gender_dropdown.on_release = lambda: self.gender_menu.open()

        # Search
        search_items = ["Select", "Roll No", "Phone No"]
        self.search_menu = MDDropdownMenu(
            caller=self.root.ids.search_dropdown,
            items=[{"text": x, "viewclass": "OneLineListItem", "on_release": lambda x=x: self.set_dropdown_item(self.root.ids.search_dropdown, x)} for x in search_items],
            width_mult=4,
        )
        self.root.ids.search_dropdown.on_release = lambda: self.search_menu.open()

    def set_dropdown_item(self, dropdown, text):
        """Update the dropdown text when an item is selected."""
        print(f"Selected item for {dropdown.id}: {text}")  # Debugging
        dropdown.text = text
        # Dismiss the corresponding menu
        if dropdown == self.root.ids.dep_dropdown:
            self.dep_menu.dismiss()
        elif dropdown == self.root.ids.course_dropdown:
            self.course_menu.dismiss()
        elif dropdown == self.root.ids.year_dropdown:
            self.year_menu.dismiss()
        elif dropdown == self.root.ids.semester_dropdown:
            self.semester_menu.dismiss()
        elif dropdown == self.root.ids.gender_dropdown:
            self.gender_menu.dismiss()
        elif dropdown == self.root.ids.search_dropdown:
            self.search_menu.dismiss()

    def get_field_values(self):
        return {
            "dep": self.root.ids.dep_dropdown.text,
            "course": self.root.ids.course_dropdown.text,
            "year": self.root.ids.year_dropdown.text,
            "semester": self.root.ids.semester_dropdown.text,
            "std_id": self.root.ids.std_id.text,
            "std_name": self.root.ids.std_name.text,
            "roll": self.root.ids.roll.text,
            "gender": self.root.ids.gender_dropdown.text,
            "dob": self.root.ids.dob.text,
            "email": self.root.ids.email.text,
            "phone": self.root.ids.phone.text,
            "address": self.root.ids.address.text,
            "teacher": self.root.ids.teacher.text,
            "photo": "No"
        }

    def add_data(self):
        values = self.get_field_values()
        if values["dep"] == "Select Department" or values["std_name"] == "" or values["std_id"] == "":
            self.show_alert("Error!", "Department, Student ID, and Name are required")
            return

        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="jarvis")
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO student (Dep, Course, Year, Semester, Student_id, Name, Roll, Gender, Dob, Email, 
                Phone, Address, Teacher, PhotoSample) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (values["dep"], values["course"], values["year"], values["semester"], values["std_id"], values["std_name"],
                 values["roll"], values["gender"], values["dob"], values["email"], values["phone"], values["address"],
                 values["teacher"], values["photo"])
            )
            conn.commit()
            self.fetch_data()
            conn.close()
            self.show_alert("Success", "Student details added successfully")
        except Exception as e:
            self.show_alert("Error!", f"Due to: {str(e)}")

    def fetch_data(self):
        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="jarvis")
            cursor = conn.cursor()
            cursor.execute("SELECT Dep, Course, Year, Semester, Student_id, Name, Roll, Gender, Dob, Email, Phone, Address, Teacher, PhotoSample FROM student")
            data = cursor.fetchall()
            
            self.root.ids.table_content.clear_widgets()
            for row in data:
                row_text = " | ".join(str(item) for item in row)
                self.root.ids.table_content.add_widget(MDLabel(text=row_text, size_hint_y=None, height=dp(30)))
            
            conn.close()
        except Exception as e:
            self.show_alert("Error!", f"Due to: {str(e)}")

    def update_data(self):
        values = self.get_field_values()
        if values["dep"] == "Select Department" or values["std_name"] == "" or values["std_id"] == "":
            self.show_alert("Error!", "Department, Student ID, and Name are required")
            return

        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="jarvis")
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE student SET Dep=%s, Course=%s, Year=%s, Semester=%s, Name=%s, Roll=%s, 
                Gender=%s, Dob=%s, Email=%s, Phone=%s, Address=%s, Teacher=%s, PhotoSample=%s 
                WHERE Student_id=%s""",
                (values["dep"], values["course"], values["year"], values["semester"], values["std_name"],
                 values["roll"], values["gender"], values["dob"], values["email"], values["phone"], values["address"],
                 values["teacher"], values["photo"], values["std_id"])
            )
            conn.commit()
            self.fetch_data()
            conn.close()
            self.show_alert("Success", "Student details updated successfully")
        except Exception as e:
            self.show_alert("Error!", f"Due to: {str(e)}")

    def delete_data(self):
        std_id = self.root.ids.std_id.text
        if not std_id:
            self.show_alert("Error!", "Student ID is required")
            return

        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="jarvis")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE Student_id=%s", (std_id,))
            conn.commit()
            self.fetch_data()
            conn.close()
            self.show_alert("Success", "Student deleted successfully")
        except Exception as e:
            self.show_alert("Error!", f"Due to: {str(e)}")

    def reset_data(self):
        self.root.ids.dep_dropdown.text = "Select Department"
        self.root.ids.course_dropdown.text = "Select Course"
        self.root.ids.year_dropdown.text = "Select Year"
        self.root.ids.semester_dropdown.text = "Select Semester"
        self.root.ids.std_id.text = ""
        self.root.ids.std_name.text = ""
        self.root.ids.roll.text = ""
        self.root.ids.gender_dropdown.text = "Select Gender"
        self.root.ids.dob.text = ""
        self.root.ids.email.text = ""
        self.root.ids.phone.text = ""
        self.root.ids.address.text = ""
        self.root.ids.teacher.text = ""

    def search_data(self):
        search_by = self.root.ids.search_dropdown.text
        search_value = self.root.ids.search_entry.text
        if search_by == "Select" or not search_value:
            self.show_alert("Error!", "Select a search criterion and enter a value")
            return

        try:
            conn = mysql.connector.connect(host="localhost", username="root", password="root", database="jarvis")
            cursor = conn.cursor()
            if search_by == "Roll No":
                query = "SELECT Dep, Course, Year, Semester, Student_id, Name, Roll, Gender, Dob, Email, Phone, Address, Teacher, PhotoSample FROM student WHERE Roll = %s"
            elif search_by == "Phone No":
                query = "SELECT Dep, Course, Year, Semester, Student_id, Name, Roll, Gender, Dob, Email, Phone, Address, Teacher, PhotoSample FROM student WHERE Phone = %s"
            cursor.execute(query, (search_value,))
            data = cursor.fetchall()

            self.root.ids.table_content.clear_widgets()
            for row in data:
                row_text = " | ".join(str(item) for item in row)
                self.root.ids.table_content.add_widget(MDLabel(text=row_text, size_hint_y=None, height=dp(30)))

            conn.close()
        except Exception as e:
            self.show_alert("Error!", f"Due to: {str(e)}")

    def generate_dataset(self):
        values = self.get_field_values()
        if values["dep"] == "Select Department" or values["std_name"] == "" or values["std_id"] == "":
            self.show_alert("Error!", "Department, Student ID, and Name are required")
            return

        try:
            # Update database
            self.update_data()
            values["photo"] = "Yes"

            # Ensure data directory exists
            if not os.path.exists("data"):
                os.makedirs("data")

            # Ensure embeddings directory exists
            if not os.path.exists("embeddings"):
                os.makedirs("embeddings")

            # Open webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("Failed to open webcam. Ensure a camera is connected and accessible.")

            img_id = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert frame to RGB (MTCNN expects RGB images)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)

                # Detect faces using MTCNN
                boxes, _ = self.mtcnn.detect(frame_pil)
                if boxes is not None and len(boxes) > 0:
                    # Take the first detected face (you can modify to handle multiple faces if needed)
                    box = boxes[0]
                    x1, y1, x2, y2 = map(int, box)

                    # Extract the face region
                    face = frame[y1:y2, x1:x2]
                    if face.size == 0:
                        continue

                    # Resize face to 160x160 (required by FaceNet)
                    face_resized = cv2.resize(face, (160, 160))
                    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
                    face_pil = Image.fromarray(face_rgb)

                    # Convert face to tensor for FaceNet
                    face_tensor = self.mtcnn(face_pil)
                    if face_tensor is None:
                        continue
                    face_tensor = face_tensor.unsqueeze(0)  # Add batch dimension

                    # Generate embedding using FaceNet
                    with torch.no_grad():
                        embedding = self.facenet(face_tensor).cpu().numpy()

                    # Save the face image
                    img_id += 1
                    face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
                    file_name_path = f"data/user.{values['std_id']}.{img_id}.jpg"
                    cv2.imwrite(file_name_path, face_gray)

                    # Save the embedding
                    embedding_path = f"embeddings/user.{values['std_id']}.{img_id}.npy"
                    np.save(embedding_path, embedding)

                    # Display the face with sample number
                    cv2.putText(face_resized, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
                    cv2.imshow("Cropped Face", face_resized)

                if cv2.waitKey(1) == 13 or img_id == 100:  # Enter key or 100 samples
                    break

            cap.release()
            cv2.destroyAllWindows()
            self.show_alert("Result", "Generating Datasets Completed!")
        except Exception as e:
            self.show_alert("Error!", f"Due to: {str(e)}")

    def show_alert(self, title, message):
        from kivymd.uix.dialog import MDDialog
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == "__main__":
    StudentManagementApp().run()