from student_entry import StudentManagementApp
from train_classifier import TrainApp
from face_recognition import FaceRecognitionApp
from threading import Thread

def launch_student_details():
    """Run the Student Details app in a separate thread."""
    Thread(target=StudentManagementApp().run).start()

def launch_train_data():
    """Run the Train Data app in a separate thread."""
    Thread(target=TrainApp().run).start()

def launch_student_identification():
    """Run the Student Identification app in a separate thread."""
    Thread(target=FaceRecognitionApp().run).start()