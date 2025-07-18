from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
import numpy as np

# Set window size for testing
Window.size = (800, 600)

# ---------------------- JarvisUI (Main Screen) ----------------------

class JarvisUI(Screen):
    subtitle_text = StringProperty("say hello jarvis !")
    mic_active = BooleanProperty(False)
    typing_active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        self.title_label = MDLabel(
            text="JARVIS AI", halign="center", font_style="H2",
            theme_text_color="Custom", text_color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.title_label)

        self.subtitle_label = MDLabel(
            text=self.subtitle_text, halign="center", font_style="H5",
            theme_text_color="Custom", text_color=(1, 1, 1, 1)
        )
        self.layout.add_widget(self.subtitle_label)

        # Bottom bar (Text input + Microphone + Chat button)
        self.bottom_bar = MDBoxLayout(size_hint=(1, 0.15), padding=dp(10), spacing=dp(10))

        self.text_input = MDTextField(
            hint_text="Type here", mode="rectangle",
            size_hint=(0.6, None), height=dp(40), multiline=False
        )

        self.mic_button = MDIconButton(
            icon="microphone", theme_text_color="Custom", text_color=(1, 1, 1, 1),
            on_release=self.on_mic_press
        )

        self.chat_button = MDIconButton(
            icon="message-text", theme_text_color="Custom", text_color=(0, 0.5, 1, 1),
            on_release=self.switch_to_chat
        )

        self.bottom_bar.add_widget(self.text_input)
        self.bottom_bar.add_widget(self.mic_button)
        self.bottom_bar.add_widget(self.chat_button)

        self.layout.add_widget(self.bottom_bar)
        self.add_widget(self.layout)

    def switch_to_chat(self, *args):
        """Switch to the chat screen."""
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "chat"

    def on_mic_press(self, *args):
        """Simulate voice input response."""
        self.subtitle_label.text = "Listening..."
        self.text_input.text = ""

# ---------------------- ChatScreen (Chat Interface) ----------------------

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical')

        # Back Button
        self.back_button = MDIconButton(
            icon="arrow-left", theme_text_color="Custom",
            text_color=(1, 1, 1, 1), on_release=self.switch_to_jarvis
        )
        self.layout.add_widget(self.back_button)

        # Scrollable Chat Area
        self.chat_scroll = MDScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.chat_area = MDBoxLayout(
            orientation='vertical', size_hint_y=None,
            height=0, padding=dp(20), spacing=dp(10)
        )
        self.chat_scroll.add_widget(self.chat_area)
        self.layout.add_widget(self.chat_scroll)

        self.add_widget(self.layout)
        self.load_sample_messages()

    def switch_to_jarvis(self, *args):
        """Switch back to the main screen."""
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "jarvis"

    def load_sample_messages(self):
        """Load some default chat messages."""
        self.add_message("Jarvis", "Hello! How can I assist you?")
        self.add_message("You", "Can you help me with something?")
        self.add_message("Jarvis", "Sure! What do you need help with?")

    def add_message(self, sender, message):
        """Add a message to the chat UI."""
        message_container = MDBoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(60),
            padding=[dp(10), 0, dp(10), 0]
        )

        bubble_color = (0.2, 0.3, 0.4, 0.8) if sender == "Jarvis" else (0.3, 0.5, 0.8, 0.8)

        bubble = MDBoxLayout(
            size_hint=(None, None), size=(dp(200), dp(40)),
            md_bg_color=bubble_color, radius=[dp(15), dp(15), dp(15), dp(15)],
            pos_hint={"right": 1} if sender == "You" else {"left": 1}
        )

        message_label = MDLabel(
            text=message, halign="center", valign="middle",
            theme_text_color="Custom", text_color=(1, 1, 1, 1), font_size=dp(14)
        )
        bubble.add_widget(message_label)

        sender_label = MDLabel(
            text=sender, halign="left" if sender == "Jarvis" else "right",
            theme_text_color="Custom", text_color=(1, 1, 1, 0.7),
            font_size=dp(12), size_hint_y=None, height=dp(20)
        )

        message_container.add_widget(bubble)
        message_container.add_widget(sender_label)
        self.chat_area.add_widget(message_container)

        self.chat_area.height += message_container.height + self.chat_area.spacing
        self.chat_scroll.scroll_y = 0  # Scroll to the bottom

# ---------------------- App Class (Screen Manager) ----------------------

class JarvisApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(JarvisUI(name="jarvis"))
        sm.add_widget(ChatScreen(name="chat"))
        return sm

if __name__ == "__main__":
    JarvisApp().run()
