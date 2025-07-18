from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from kivy.uix.screenmanager import FadeTransition
from kivy.clock import Clock
from kivy.animation import Animation
import pyrebase
import subprocess
import sys

# Set initial window size for the loading screen (800x450)
Window.size = (800, 450)
Window.borderless = True
screen_width, screen_height = Window.system_size
Window.left = screen_width * 0.2
Window.top = screen_height * 0.1

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDMtu_9TakONHF9Glm_jMHnPUNO-_u_448",
    "authDomain": "jarvisauth-74f12.firebaseapp.com",
    "databaseURL": "",
    "projectId": "jarvisauth-74f12",
    "storageBucket": "jarvisauth-74f12.firebasestorage.app",
    "messagingSenderId": "597787476260",
    "appId": "1:597787476260:web:d56ee3d43306ff0564f3b1",
    "measurementId": "G-FEGC5RKB4J"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

class LoadingScreen(MDScreen):
    def on_enter(self):
        Window.size = (800, 450)
        screen_width, screen_height = Window.system_size
        Window.left = screen_width * 0.2
        Window.top = screen_height * 0.1
        Clock.schedule_once(self.start_animations, 0)
        Clock.schedule_once(self.start_background_animation, 0)

    def start_animations(self, dt):
        progress_bar = self.ids.progress_bar
        percentage_label = self.ids.percentage_label
        loading_label = self.ids.loading_label

        anim = Animation(value=100, duration=5)
        anim.start(progress_bar)

        def update_percentage(instance, value):
            percentage_label.text = f"{int(value)} %"
            if int(value) >= 100:
                Clock.unschedule(update_dots)
                loading_label.opacity = 0
                anim_window = Animation(size=(1280, 720), duration=0.5)
                def on_complete_window_resize(*args):
                    screen_width, screen_height = Window.system_size
                    Window.left = (screen_width - Window.size[0]) / 2
                    Window.top = (screen_height - Window.size[1]) / 2
                    self.manager.current = "login"
                anim_window.bind(on_complete=on_complete_window_resize)
                anim_window.start(Window)

        anim.bind(on_progress=lambda instance, widget, progress: update_percentage(progress_bar, progress_bar.value))

        dots = ["", ".", "..", "..."]
        dot_index = 0

        def update_dots(dt):
            nonlocal dot_index
            loading_label.text = f"loading{dots[dot_index]}"
            dot_index = (dot_index + 1) % len(dots)

        Clock.schedule_interval(update_dots, 0.5)

    def start_background_animation(self, dt):
        top_left_colors = [
            (1, 0.8, 0, 1),
            (0.2, 0.8, 0.4, 1),
            (0, 0.6, 0.8, 1),
            (0.8, 0.2, 0.6, 1),
        ]
        bottom_right_colors = [
            (0, 0.7, 0.6, 1),
            (0, 0.4, 0.8, 1),
            (0.6, 0.2, 0.8, 1),
            (0.8, 0.6, 0.2, 1),
        ]

        canvas = self.canvas.before
        top_left_color_instruction = canvas.get_group('top_left_color')[0]
        bottom_right_color_instruction = canvas.get_group('bottom_right_color')[0]
        progress_bar = self.ids.progress_bar

        def animate_colors(index=0):
            if progress_bar.value >= 100:
                return

            top_left_next = top_left_colors[index % len(top_left_colors)]
            bottom_right_next = bottom_right_colors[index % len(bottom_right_colors)]

            anim_top = Animation(rgba=top_left_next, duration=1.5)
            anim_bottom = Animation(rgba=bottom_right_next, duration=1.5)

            anim_top.start(top_left_color_instruction)
            anim_bottom.start(bottom_right_color_instruction)

            Clock.schedule_once(lambda dt: animate_colors(index + 1), 1.5)

        animate_colors()

class LoginScreen(MDScreen):
    def on_enter(self):
        Window.size = (1280, 720)
        screen_width, screen_height = Window.system_size
        Window.left = screen_width * 0.2
        Window.top = screen_height * 0.1

    def on_text_input(self, instance, value):
        print(f"Input in {instance.hint_text}: {value}")

    def login(self):
        email = self.ids.login_email.text
        password = self.ids.login_password.text
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            print("Successfully logged in:", user["email"])
            self.ids.login_message.text = "Login successful!"
            # Launch the main app and close the auth app
            subprocess.Popen([sys.executable, "main_app.py"])
            # Close the current app
            MDApp.get_running_app().stop()
        except Exception as e:
            print("Login failed:", e)
            self.ids.login_message.text = "Login failed: Invalid email or password"

    def forgot_password(self):
        email = self.ids.login_email.text
        if not email:
            self.ids.login_message.text = "Please enter your email"
            return
        try:
            auth.send_password_reset_email(email)
            self.ids.login_message.text = "Password reset email sent! Check your inbox."
        except Exception as e:
            print("Password reset failed:", e)
            self.ids.login_message.text = "Error: " + str(e)

class SignupScreen(MDScreen):
    def on_enter(self):
        Window.size = (1280, 720)
        screen_width, screen_height = Window.system_size
        Window.left = screen_width * 0.2
        Window.top = screen_height * 0.1

    def on_text_input(self, instance, value):
        print(f"Input in {instance.hint_text}: {value}")

    def signup(self):
        username = self.ids.signup_username.text
        email = self.ids.signup_email.text
        password = self.ids.signup_password.text
        try:
            user = auth.create_user_with_email_and_password(email, password)
            print("Successfully signed up:", user["email"])
            self.ids.signup_message.text = "Signup successful! Please log in."
            self.manager.current = "login"
        except Exception as e:
            print("Signup failed:", e)
            self.ids.signup_message.text = "Signup failed: Email already exists or weak password"

class AuthApp(MDApp):
    def build(self):
        Builder.load_file("loading_animation.kv")
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.sm = MDScreenManager(transition=FadeTransition(duration=0.5))
        self.sm.add_widget(LoadingScreen(name="loading"))
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignupScreen(name="signup"))
        self.sm.current = "loading"
        return self.sm

    def switch_to_signup(self):
        self.sm.current = "signup"

    def switch_to_login(self):
        self.sm.current = "login"

if __name__ == "__main__":
    AuthApp().run()