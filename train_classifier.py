from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import os
import numpy as np
import pickle
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(20)

    MDLabel:
        text: "TRAIN DATA SET"
        halign: "center"
        theme_text_color: "Custom"
        text_color: 1, 0, 0, 1  # Red color
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
                text: "Train Data"
                on_release: app.train_classifier()
                md_bg_color: [1, 1, 0, 1]  # Yellow color
                size_hint: None, None
                size: dp(200), dp(60)
                font_size: dp(30)
'''

class TrainApp(MDApp):
    def build(self):
        self.root = Builder.load_string(KV)
        return self.root

    def train_classifier(self):
        # Check if the embeddings directory exists
        embeddings_dir = "embeddings"
        if not os.path.exists(embeddings_dir):
            self.show_alert("Error", "Embeddings directory does not exist! Please generate embeddings using the student entry app.")
            return

        # Get embedding paths
        embedding_paths = [os.path.join(embeddings_dir, file) for file in os.listdir(embeddings_dir) if file.endswith('.npy')]

        if len(embedding_paths) == 0:
            self.show_alert("Error", "No embeddings found in the embeddings directory!")
            return

        embeddings = []
        ids = []

        for embedding_path in embedding_paths:
            try:
                # Load the embedding
                embedding = np.load(embedding_path)

                # Extract student ID from the filename (e.g., user.<student_id>.<img_id>.npy)
                student_id = os.path.split(embedding_path)[1].split('.')[1]  # e.g., 'VIT34CS021'

                embeddings.append(embedding.flatten())  # Flatten the embedding to 1D array
                ids.append(student_id)

            except Exception as e:
                print(f"Error processing file {embedding_path}: {e}")
                continue

        if len(embeddings) == 0 or len(ids) == 0:
            self.show_alert("Error", "No valid embeddings or IDs found to train the classifier!")
            return

        # Convert to numpy arrays
        embeddings = np.array(embeddings)
        ids = np.array(ids)

        # Check the number of unique classes (student IDs)
        unique_ids = np.unique(ids)
        if len(unique_ids) < 2:
            self.show_alert("Error", f"Need at least 2 different student IDs to train the classifier. Found {len(unique_ids)} student ID(s): {unique_ids}")
            return

        # Use LabelEncoder to convert string IDs to numeric labels
        label_encoder = LabelEncoder()
        numeric_ids = label_encoder.fit_transform(ids)

        # Train an SVM classifier
        clf = SVC(kernel='linear', probability=True)
        clf.fit(embeddings, numeric_ids)

        # Ensure the models directory exists
        models_dir = "models"
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        # Save the classifier
        classifier_path = os.path.join(models_dir, "classifier.pkl")
        with open(classifier_path, 'wb') as f:
            pickle.dump(clf, f)

        # Save the label encoder (to map numeric labels back to student IDs during recognition)
        label_encoder_path = os.path.join(models_dir, "label_encoder.pkl")
        with open(label_encoder_path, 'wb') as f:
            pickle.dump(label_encoder, f)

        self.show_alert("Result", "Training completed successfully! Classifier and label encoder saved in models/ folder.")

    def show_alert(self, title, message):
        from kivymd.uix.dialog import MDDialog
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == "__main__":
    TrainApp().run()