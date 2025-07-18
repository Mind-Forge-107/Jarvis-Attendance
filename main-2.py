from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField


class HomeScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class ToolsScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("main.kv")

    def set_theme(self, theme_style):
        """Switch between Light and Dark theme."""
        self.theme_cls.theme_style = theme_style

    def set_custom_theme(self, color):
        """Change the app theme color."""
        self.theme_cls.primary_palette = color

    def show_theme_picker(self):
        """Show the theme selection dialog."""
        dialog = MDDialog(
            title="Select Theme",
            buttons=[
                MDRaisedButton(
                    text="Light",
                    on_release=lambda x: self.set_theme("Light")
                ),
                MDRaisedButton(
                    text="Dark",
                    on_release=lambda x: self.set_theme("Dark")
                ),
            ],
        )
        dialog.open()

    def show_date_picker(self):
        """Show a date picker dialog."""
        date_dialog = MDDatePicker()
        date_dialog.open()

    def show_location_picker(self, instance):
        """Simulate opening a file picker for storage location selection."""
        print("Opening storage location picker...")

    def clear_cache(self):
        """Simulate clearing cache."""
        print("Cache Cleared!")

    def show_password_dialog(self):
        """Display a password change dialog."""
        dialog = MDDialog(
            title="Change Password",
            type="custom",
            content_cls=MDTextField(hint_text="Enter new password", password=True),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="CONFIRM",
                    on_release=lambda x: self.change_password(dialog),
                ),
            ],
        )
        dialog.open()

    def change_password(self, dialog):
        """Simulate password change process."""
        print("Password changed successfully!")
        dialog.dismiss()

    def show_email_dialog(self):
        """Display an email update dialog."""
        dialog = MDDialog(
            title="Update Email",
            type="custom",
            content_cls=MDTextField(hint_text="Enter new email"),
            buttons=[
                MDFlatButton(
                    text=" on_release=lambda x: dialog.dismiss()",
                ),
                MDRaisedButton(
                    text="UPDATE",
                    on_release=lambda x: self.update_email(dialog),
                ),
            ],
        )
        dialog.open()

    def update_email(self, dialog):
        """Simulate email update process."""
        print("Email updated successfully!")
        dialog.dismiss()

    def show_pin_dialog(self):
        """Display a PIN setup dialog."""
        dialog = MDDialog(
            title="Set New PIN",
            type="custom",
            content_cls=MDTextField(hint_text="Enter new PIN", password=True),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="SET PIN",
                    on_release=lambda x: self.set_new_pin(dialog),
                ),
            ],
        )
        dialog.open()

    def set_new_pin(self, dialog):
        """Simulate PIN setup process."""
        print("New PIN set successfully!")
        dialog.dismiss()


if __name__ == "__main__":
    MainApp().run()