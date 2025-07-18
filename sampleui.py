from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget

KV = """
MDScreen:

    MDNavigationLayout:

        ScreenManager:
            id: screen_manager

            # Dashboard
            MDScreen:
                name: "dashboard"

                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Jarvis"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state('open')]]
                        right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

                    MDLabel:
                        text: "Hey Welcome to new Class Monitoring System"
                        halign: "center"
                        font_style: "H5"
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.primary_color

                    MDRaisedButton:
                        text: "View Attendance"
                        pos_hint: {"center_x": 0.5}
                        on_release: app.switch_screen("attendance")

            # Attendance Page
            MDScreen:
                name: "attendance"

                MDBoxLayout:
                    orientation: "vertical"

                    MDTopAppBar:
                        title: "Attendance"
                        left_action_items: [["arrow-left", lambda x: app.switch_screen("dashboard")]]

                    MDLabel:
                        text: "📋 Attendance Records"
                        halign: "center"
                        font_style: "H5"
                        theme_text_color: "Secondary"

                    ScrollView:
                        MDList:
                            id: attendance_list

        # Navigation Drawer
        MDNavigationDrawer:
            id: nav_drawer

            MDBoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                padding: "8dp"

                MDLabel:
                    text: "Menu"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]

                MDList:
                    OneLineIconListItem:
                        text: "Dashboard"
                        on_release:
                            app.switch_screen("dashboard")
                            nav_drawer.set_state("close")
                        IconLeftWidget:
                            icon: "home"

                    OneLineIconListItem:
                        text: "Attendance"
                        on_release:
                            app.switch_screen("attendance")
                            nav_drawer.set_state("close")
                        IconLeftWidget:
                            icon: "clipboard-list"
"""

class AttendanceApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Set primary theme color
        return Builder.load_string(KV)

    def toggle_theme(self):
        """Toggles between Dark and Light Mode"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"

    def switch_screen(self, screen_name):
        """Switches between different screens"""
        self.root.ids.screen_manager.current = screen_name

    def on_start(self):
        """Loads attendance data into the list"""
        students = [
            ("101", "Alice Johnson", "Present"),
            ("102", "Bob Smith", "Absent"),
            ("103", "Charlie Brown", "Present"),
            ("104", "David Wilson", "Late"),
            ("105", "Emma Watson", "Present"),
        ]
        for student in students:
            item = OneLineAvatarIconListItem(text=f"{student[1]} - {student[2]}")
            item.add_widget(IconLeftWidget(icon="account-check" if student[2] == "Present" else "account-remove"))
            self.root.ids.attendance_list.add_widget(item)


if __name__ == "__main__":
    AttendanceApp().run()
