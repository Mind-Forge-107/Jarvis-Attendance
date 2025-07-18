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
import csv
import os

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    padding: [dp(20), 0, dp(20), dp(20)]  # Zero top padding to ensure title is at the top
    spacing: dp(10)
    md_bg_color: [0, 0, 0, 0]  # Transparent background

    # Title at the top-center
    MDBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(50)
        MDLabel:
            text: "ATTENDANCE MANAGEMENT SYSTEM"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0, 0, 0, 1  # Black color
            font_style: "H4"

    # Main content with two panels
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(20)
        size_hint_y: None
        height: self.minimum_height

        # Left Panel (Student Attendance Details)
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.5
            size_hint_y: None
            height: dp(400)  # Fixed height to match the right panel
            padding: dp(15)
            spacing: dp(10)
            md_bg_color: [0.9, 0.8, 0.95, 1]  # Pale violet
            canvas.before:
                Color:
                    rgba: self.md_bg_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20), dp(20), dp(20), dp(20)]  # Rounded corners

            MDLabel:
                text: "Student Attendance Details"
                halign: "center"
                font_style: "H6"
                size_hint_y: None
                height: dp(40)

            ScrollView:
                do_scroll_x: False
                MDBoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(5)
                    spacing: dp(5)

                    MDGridLayout:
                        cols: 2
                        size_hint_y: None
                        height: self.minimum_height
                        MDLabel:
                            text: "ID:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: atten_id
                            hint_text: "ID"
                            size_hint_y: None
                            height: dp(40)
                        MDLabel:
                            text: "Roll No:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: atten_roll
                            hint_text: "Roll No"
                            size_hint_y: None
                            height: dp(40)
                        MDLabel:
                            text: "Name:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: atten_name
                            hint_text: "Name"
                            size_hint_y: None
                            height: dp(40)
                        MDLabel:
                            text: "Department:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: atten_dep
                            hint_text: "Department"
                            size_hint_y: None
                            height: dp(40)
                        MDLabel:
                            text: "Time:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: atten_time
                            hint_text: "Time"
                            size_hint_y: None
                            height: dp(40)
                        MDLabel:
                            text: "Date:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDTextField:
                            id: atten_date
                            hint_text: "Date"
                            size_hint_y: None
                            height: dp(40)
                        MDLabel:
                            text: "Status:"
                            halign: "left"
                            size_hint_y: None
                            height: dp(40)
                        MDDropDownItem:
                            id: atten_status
                            text: "Idle"
                            size_hint_y: None
                            height: dp(40)

                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        padding: dp(10)
                        size_hint_y: None
                        height: dp(50)
                        MDRaisedButton:
                            text: "Import CSV"
                            on_release: app.importCsv()
                            md_bg_color: [0, 1, 0, 1]  # Green
                        MDRaisedButton:
                            text: "Export CSV"
                            on_release: app.exportCsv()
                            md_bg_color: [1, 0.65, 0, 1]  # Orange
                        MDRaisedButton:
                            text: "Update"
                            on_release: app.update_data()
                            md_bg_color: [1, 0, 0, 1]  # Red
                        MDRaisedButton:
                            text: "Reset"
                            on_release: app.confirm_reset()
                            md_bg_color: [0, 0, 1, 1]  # Blue

        # Right Panel (Attendance Details)
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.5
            size_hint_y: None
            height: dp(400)  # Fixed height to match the left panel
            padding: dp(15)
            spacing: dp(10)
            md_bg_color: [0.9, 0.8, 0.95, 1]  # Pale violet
            canvas.before:
                Color:
                    rgba: self.md_bg_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20), dp(20), dp(20), dp(20)]  # Rounded corners

            MDLabel:
                text: "Attendance Details"
                halign: "center"
                font_style: "H6"
                size_hint_y: None
                height: dp(40)

            ScrollView:
                id: table_scroll
                MDBoxLayout:
                    id: table_content
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
'''

class AttendanceApp(MDApp):
    def __init__(self):
        super().__init__()
        self.mydata = []
        self.selected_row_index = None
        self.status_menu = None  # Initialize status_menu as None

    def build(self):
        self.root = Builder.load_string(KV)
        self.initialize_dropdown()
        return self.root

    def initialize_dropdown(self):
        # Define the menu items
        menu_items = [
            {"text": "Idle", "viewclass": "OneLineListItem", "on_release": lambda x="Idle": self.set_status(x)},
            {"text": "Present", "viewclass": "OneLineListItem", "on_release": lambda x="Present": self.set_status(x)},
            {"text": "Absent", "viewclass": "OneLineListItem", "on_release": lambda x="Absent": self.set_status(x)},
        ]
        # Initialize the dropdown menu
        self.status_menu = MDDropdownMenu(
            caller=self.root.ids.atten_status,
            items=menu_items,
            width_mult=4,
            position="auto",
        )
        # Bind the on_release event directly to the MDDropDownItem
        self.root.ids.atten_status.bind(on_release=self.open_status_menu)

    def open_status_menu(self, instance):
        # Open the dropdown menu when the MDDropDownItem is clicked
        if self.status_menu:
            self.status_menu.open()

    def set_status(self, status):
        # Update the text of the MDDropDownItem with the selected item
        self.root.ids.atten_status.set_item(status)
        self.status_menu.dismiss()

    def fetchData(self, rows):
        self.root.ids.table_content.clear_widgets()
        for idx, row in enumerate(rows):
            if len(row) != 7:
                print(f"Skipping invalid row {row}: expected 7 columns, got {len(row)}")
                continue
            row_text = " | ".join(str(item) for item in row)
            label = MDLabel(
                text=row_text,
                size_hint_y=None,
                height=dp(30),
                theme_text_color="Custom",
                text_color=(0, 0, 1, 1) if idx % 2 == 0 else (0, 0, 0, 1)
            )
            label.bind(on_touch_down=lambda instance, touch, idx=idx: self.select_row(instance, touch, idx))
            self.root.ids.table_content.add_widget(label)

    def select_row(self, instance, touch, idx):
        if instance.collide_point(*touch.pos):
            self.selected_row_index = idx
            self.get_cursor(instance.text)

    def importCsv(self):
        try:
            fln = "attendance.csv"
            if not os.path.exists(fln):
                self.show_alert("Error", "CSV file not found!")
                return
            with open(fln) as myfile:
                csvread = csv.reader(myfile, delimiter=",")
                self.mydata.clear()
                for i in csvread:
                    self.mydata.append(i)
                if not self.mydata:
                    self.show_alert("Error", "CSV file is empty!")
                    return
                self.fetchData(self.mydata)
                self.show_alert("Success", "CSV imported successfully!")
        except Exception as e:
            self.show_alert("Error", f"Due to: {str(e)}")

    def exportCsv(self):
        try:
            if len(self.mydata) < 1:
                self.show_alert("Error", "No data records found to export")
                return
            fln = "exported_attendance.csv"
            with open(fln, mode="w", newline="") as myfile:
                exp_write = csv.writer(myfile, delimiter=",")
                for i in self.mydata:
                    exp_write.writerow(i)
                self.show_alert("Success", f"Your data exported to {os.path.basename(fln)} successfully")
        except Exception as e:
            self.show_alert("Error", f"Due to: {str(e)}")

    def get_cursor(self, row_text):
        row = row_text.split(" | ")
        if len(row) == 7:
            self.root.ids.atten_id.text = row[0]
            self.root.ids.atten_roll.text = row[1]
            self.root.ids.atten_name.text = row[2]
            self.root.ids.atten_dep.text = row[3]
            self.root.ids.atten_time.text = row[4]
            self.root.ids.atten_date.text = row[5]
            self.root.ids.atten_status.set_item(row[6])  # Use set_item for MDDropDownItem

    def update_data(self):
        if self.selected_row_index is None:
            self.show_alert("Error", "Please select a row to update!")
            return
        updated_row = [
            self.root.ids.atten_id.text,
            self.root.ids.atten_roll.text,
            self.root.ids.atten_name.text,
            self.root.ids.atten_dep.text,
            self.root.ids.atten_time.text,
            self.root.ids.atten_date.text,
            self.root.ids.atten_status.current_item  # Use current_item to get the selected status
        ]
        if not all(updated_row):
            self.show_alert("Error", "All fields must be filled!")
            return
        self.mydata[self.selected_row_index] = updated_row
        self.fetchData(self.mydata)
        self.show_alert("Success", "Attendance record updated successfully!")

    def confirm_reset(self):
        from kivymd.uix.dialog import MDDialog
        dialog = MDDialog(
            title="Confirm Reset",
            text="Are you sure you want to reset the fields? This action cannot be undone.",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Reset", on_release=lambda x: self.reset_data_and_dismiss(dialog))
            ]
        )
        dialog.open()

    def reset_data_and_dismiss(self, dialog):
        self.reset_data()
        dialog.dismiss()

    def reset_data(self):
        self.root.ids.atten_id.text = ""
        self.root.ids.atten_roll.text = ""
        self.root.ids.atten_name.text = ""
        self.root.ids.atten_dep.text = ""
        self.root.ids.atten_time.text = ""
        self.root.ids.atten_date.text = ""
        self.root.ids.atten_status.set_item("Idle")  # Reset to "Idle"
        self.selected_row_index = None

    def show_alert(self, title, message):
        from kivymd.uix.dialog import MDDialog
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

if __name__ == "__main__":
    AttendanceApp().run()