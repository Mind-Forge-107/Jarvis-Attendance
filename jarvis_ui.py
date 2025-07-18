from kivy.app import App
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.widget import Widget
from kivy.uix.image import Image
import numpy as np
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound, PlaysoundException
import os
import threading

# Set window size (optional, for testing)
Window.size = (800, 600)

# Custom Hover Behavior Implementation
class CustomHoverBehavior(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*pos):
            if not hasattr(self, '_hovered') or not self._hovered:
                self._hovered = True
                self.on_enter()
        else:
            if hasattr(self, '_hovered') and self._hovered:
                self._hovered = False
                self.on_leave()

    def on_enter(self):
        pass

    def on_leave(self):
        pass

class HoverButton(MDIconButton, CustomHoverBehavior):
    def on_enter(self):
        self.opacity = 1.0
        self.scale = 1.1

    def on_leave(self):
        self.opacity = 0.7
        self.scale = 1.0

class HoverTextField(MDTextField, CustomHoverBehavior):
    def on_enter(self):
        self.line_color_normal = [0, 0.5, 1, 1]
        self.line_color_focus = [0, 0.5, 1, 1]

    def on_leave(self):
        self.line_color_normal = [1, 1, 1, 0.7]
        self.line_color_focus = [1, 1, 1, 1]

class JarvisUI(MDBoxLayout):
    subtitle_text = StringProperty("")
    mic_active = BooleanProperty(False)
    typing_active = BooleanProperty(False)
    top_right_color = ListProperty([0, 0.5, 1, 0.45])
    bottom_left_color = ListProperty([0.5, 0, 1, 0.45])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        self.recognizer = sr.Recognizer()
        self.cancel_speech = False

        Window.clearcolor = (0, 0, 0, 0)
        self.gradient_texture = self.create_gradient_texture(self.top_right_color, self.bottom_left_color)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size, texture=self.gradient_texture)
        Window.bind(on_resize=self.update_background)

        self.color_pairs = [
            ([0, 0.5, 1, 0.45], [0.5, 0, 1, 0.45]),
            ([0.5, 0, 1, 0.45], [0, 1, 0.8, 0.45]),
            ([0, 1, 0.8, 0.45], [0.678, 0.847, 0.902, 0.45]),
            ([0.678, 0.847, 0.902, 0.45], [0, 0.5, 1, 0.45])
        ]
        self.current_color_index = 0

        # Top bar for title and menu button
        self.top_bar = MDBoxLayout(
            size_hint=(1, None),
            height=dp(50),
            padding=(dp(10), 0)
        )

        # Title
        self.title_label = MDLabel(
            text="JARVIS AI",
            halign="center",
            font_style="H2",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1)
        )
        self.top_bar.add_widget(self.title_label)

        # Menu button (three dots)
        self.menu_button = HoverButton(
            icon="dots-vertical",
            pos_hint={"right": 1, "top": 1},
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            opacity=0.7,
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=self.toggle_options_panel
        )
        self.top_bar.add_widget(self.menu_button)

        self.add_widget(self.top_bar)

        # Options panel (wrapped in MDCard for rounded edges)
        self.options_card = MDCard(
            size_hint=(None, None),
            size=(dp(180), dp(180)),
            pos_hint={"right": 0.95, "top": 0.95},
            radius=[dp(15)] * 4,
            md_bg_color=(0.9, 0.9, 0.9, 1)
        )

        self.options_panel = MDBoxLayout(
            orientation='vertical',
            spacing=dp(5),
            padding=dp(10)
        )

        # Help option
        help_layout = MDBoxLayout(size_hint_y=None, height=dp(30))
        help_icon = MDIconButton(
            icon="help-circle",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        help_label = MDLabel(
            text="Help",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        help_layout.add_widget(help_icon)
        help_layout.add_widget(help_label)
        self.options_panel.add_widget(help_layout)

        # Separator
        separator1 = Widget(size_hint_y=None, height=dp(1))
        with separator1.canvas:
            Color(0.7, 0.7, 0.7, 1)
            Rectangle(size=(dp(150), dp(1)))
        self.options_panel.add_widget(separator1)

        # History option
        history_layout = MDBoxLayout(size_hint_y=None, height=dp(30))
        history_icon = MDIconButton(
            icon="history",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        history_label = MDLabel(
            text="History",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        history_layout.add_widget(history_icon)
        history_layout.add_widget(history_label)
        self.options_panel.add_widget(history_layout)

        # Separator
        separator2 = Widget(size_hint_y=None, height=dp(1))
        with separator2.canvas:
            Color(0.7, 0.7, 0.7, 1)
            Rectangle(size=(dp(150), dp(1)))
        self.options_panel.add_widget(separator2)

        # Settings option
        settings_layout = MDBoxLayout(size_hint_y=None, height=dp(30))
        settings_icon = MDIconButton(
            icon="cog",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        settings_label = MDLabel(
            text="Settings",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        settings_layout.add_widget(settings_icon)
        settings_layout.add_widget(settings_label)
        self.options_panel.add_widget(settings_layout)

        # Separator
        separator3 = Widget(size_hint_y=None, height=dp(1))
        with separator3.canvas:
            Color(0.7, 0.7, 0.7, 1)
            Rectangle(size=(dp(150), dp(1)))
        self.options_panel.add_widget(separator3)

        # About option
        about_layout = MDBoxLayout(size_hint_y=None, height=dp(30))
        about_icon = MDIconButton(
            icon="information",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        about_label = MDLabel(
            text="About",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_y": 0.5}
        )
        about_layout.add_widget(about_icon)
        about_layout.add_widget(about_label)
        self.options_panel.add_widget(about_layout)

        # Add the options panel to the card
        self.options_card.add_widget(self.options_panel)

        # Initially hide the panel
        self.options_card.opacity = 0
        self.options_card.disabled = True
        self.add_widget(self.options_card)

        # GIF Animation below title (reduced size)
        self.gif_image = Image(
            source='flying-bird.gif',
            anim_delay=0.1,
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            pos_hint={"center_x": 0.5}
        )
        self.add_widget(self.gif_image)

        # Description text below GIF
        self.description_label = MDLabel(
            text='"Jarvis is a powerful yet intelligent smart monitoring assistant with live attendance monitoring with continuous updates"',
            halign="center",
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(0, 0.5, 1, 1),
            size_hint=(None, None),
            width=dp(600),
            height=dp(60),
            pos_hint={"center_x": 0.5},
            font_name="Roboto-Italic.ttf"
        )
        self.add_widget(self.description_label)

        # Subtitle with typing animation
        self.subtitle_label = MDLabel(
            text="",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        self.add_widget(self.subtitle_label)

        # Chat display (scrollable, extended height)
        self.chat_scroll = MDScrollView()
        self.chat_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(400)
        )
        self.chat_container.bind(minimum_height=self.chat_container.setter('height'))
        self.chat_scroll.add_widget(self.chat_container)
        self.add_widget(self.chat_scroll)

        # Bottom bar
        self.bottom_bar = MDBoxLayout(
            size_hint=(1, 0.15),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=(0, 0, 0, 0),
        )

        # Text input with hover effect, Enter key as send
        self.text_input = HoverTextField(
            hint_text="Type here or say 'Hello Jarvis'",
            mode="rectangle",
            size_hint=(0.6, None),
            height=dp(40),
            multiline=False,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            on_text=self.on_text_input,
            on_focus=self.on_text_focus,
        )
        self.text_input.text_color = [1, 1, 1, 1]

        Window.bind(on_key_down=self.on_key_down)

        # Microphone button (hover)
        self.mic_button = HoverButton(
            icon="microphone",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(0, 0.4, 0, 1),
            opacity=0.7,
            on_release=self.on_mic_press
        )

        # Cancel button (hover)
        self.cancel_button = HoverButton(
            icon="close",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(1, 0, 0, 1),
            opacity=0.7,
            on_release=self.cancel_speech_input
        )

        # Clear button (hover)
        self.clear_button = HoverButton(
            icon="delete",
            pos_hint={"center_y": 0.5},
            theme_text_color="Custom",
            text_color=(0, 0, 1, 1),
            opacity=0.7,
            on_release=self.clear_chat
        )

        self.bottom_bar.add_widget(self.text_input)
        self.bottom_bar.add_widget(self.mic_button)
        self.bottom_bar.add_widget(self.clear_button)
        self.add_widget(self.bottom_bar)

        Clock.schedule_once(self.start_background_animation, 1)
        Clock.schedule_once(self.animate_subtitle, 1)

    def toggle_options_panel(self, *args):
        if self.options_card.opacity == 0:
            # Show the panel
            self.options_card.opacity = 1
            self.options_card.disabled = False
        else:
            # Hide the panel
            self.options_card.opacity = 0
            self.options_card.disabled = True


    def create_gradient_texture(self, top_right, bottom_left):
        size = 256
        buf = np.zeros((size, size, 4), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                u, v = x / (size - 1), y / (size - 1)
                r = bottom_left[0] * (1 - u) * (1 - v) + top_right[0] * u * v
                g = bottom_left[1] * (1 - u) * (1 - v) + top_right[1] * u * v
                b = bottom_left[2] * (1 - u) * (1 - v) + top_right[2] * u * v
                a = bottom_left[3] * (1 - u) * (1 - v) + top_right[3] * u * v
                buf[y, x] = [int(r * 255), int(g * 255), int(b * 255), int(a * 255)]
        texture = Texture.create(size=(size, size), colorfmt='rgba')
        texture.blit_buffer(buf.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        return texture

    def update_background(self, instance, width, height):
        self.bg_rect.size = (width, height)

    def start_background_animation(self, dt):
        self.animate_background_color()

    def animate_background_color(self):
        next_color_index = (self.current_color_index + 1) % len(self.color_pairs)
        next_top_right, next_bottom_left = self.color_pairs[next_color_index]
        anim = Animation(top_right_color=next_top_right, bottom_left_color=next_bottom_left, duration=2.0)
        anim.bind(on_progress=self.update_gradient)
        anim.bind(on_complete=self.on_color_animation_complete)
        anim.start(self)
        self.current_color_index = next_color_index

    def update_gradient(self, animation, widget, progression):
        self.gradient_texture = self.create_gradient_texture(self.top_right_color, self.bottom_left_color)
        self.bg_rect.texture = self.gradient_texture

    def on_color_animation_complete(self, animation, widget):
        self.animate_background_color()

    def on_text_focus(self, instance, value):
        if value:
            self.typing_active = True
            self.switch_to_typing_state()
        elif not self.text_input.text:
            self.typing_active = False
            self.switch_to_default_state()

    def on_text_input(self, instance, value):
        if value:
            self.typing_active = True
            self.switch_to_typing_state()
        else:
            self.typing_active = False
            self.switch_to_default_state()

    def switch_to_typing_state(self):
        if self.mic_button in self.bottom_bar.children:
            self.bottom_bar.remove_widget(self.mic_button)
        if self.cancel_button not in self.bottom_bar.children:
            self.bottom_bar.add_widget(self.cancel_button)

    def switch_to_default_state(self):
        if self.cancel_button in self.bottom_bar.children:
            self.bottom_bar.remove_widget(self.cancel_button)
        if self.mic_button not in self.bottom_bar.children:
            self.bottom_bar.add_widget(self.mic_button)
        self.text_input.hint_text = "Type here or say 'Hello Jarvis'"

    def switch_to_mic_state(self):
        self.text_input.text = ""
        self.text_input.hint_text = "Speak now ..."
        if self.mic_button in self.bottom_bar.children:
            self.bottom_bar.remove_widget(self.mic_button)
        if self.cancel_button not in self.bottom_bar.children:
            self.bottom_bar.add_widget(self.cancel_button)
        self.animate_dots()

    def on_mic_press(self, *args):
        self.mic_active = True
        self.typing_active = False
        self.cancel_speech = False
        self.switch_to_mic_state()
        self.animate_mic_button()
        threading.Thread(target=self.transcribe_and_respond).start()

    def on_send_press(self, *args):
        text = self.text_input.text
        if text:
            response = self.chatbot_response(text)
            self.update_chat(text, response)
            self.speak(response)
            self.text_input.text = ""
            self.typing_active = False
            self.switch_to_default_state()

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if key == 13 and self.text_input.focus:  # 13 is the keycode for Enter
            self.on_send_press()
            return True  # Consume the key event
        return False  # Let other handlers process if not Enter

    def clear_chat(self, *args):
        self.chat_container.clear_widgets()
        self.chat_container.add_widget(MDLabel(text="Chat cleared!", halign="center", size_hint_y=None, height=dp(30)))

    def cancel_speech_input(self, *args):
        self.cancel_speech = True
        self.mic_active = False
        self.switch_to_default_state()
        self.update_chat("", "Speech input cancelled.")
        if hasattr(self, 'mic_anim'):
            self.mic_anim.cancel(self.mic_button)

    def animate_subtitle(self, dt):
        subtitle_full_text = "Say hello to Jarvis"
        self.subtitle_text = ""
        self.current_char = 0

        def update_text(dt):
            if self.current_char < len(subtitle_full_text):
                self.subtitle_text += subtitle_full_text[self.current_char]
                self.current_char += 1
                Clock.schedule_once(update_text, 0.1)
        Clock.schedule_once(update_text, 0.1)
        self.subtitle_label.text = self.subtitle_text

    def animate_dots(self):
        base_text = "Speak now "
        dots = ["", ".", "..", "..."]
        self.dot_index = 0

        def update_dots(dt):
            if self.mic_active:
                self.text_input.hint_text = base_text + dots[self.dot_index]
                self.dot_index = (self.dot_index + 1) % len(dots)
                Clock.schedule_once(update_dots, 0.5)
            else:
                self.switch_to_default_state()
        Clock.schedule_once(update_dots, 0.5)

    def animate_mic_button(self):
        anim = Animation(text_color=[0, 1, 0, 1], duration=0.5) + Animation(text_color=[0, 0.4, 0, 1], duration=0.5)
        anim.repeat = True
        anim.start(self.mic_button)
        self.mic_anim = anim

    def update_chat(self, user_text, bot_response):
        if user_text:
            user_card = MDCard(
                size_hint=(None, None),
                size=(dp(300), dp(40)),
                md_bg_color=(0.9, 0.9, 0.9, 1),
                radius=[dp(10)] * 4,
                pos_hint={"left": 1}
            )
            user_label = MDLabel(
                text=f"You: {user_text}",
                halign="left",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                padding=(dp(10), dp(10))
            )
            user_card.add_widget(user_label)
            self.chat_container.add_widget(user_card)

        if bot_response:
            bot_card = MDCard(
                size_hint=(None, None),
                size=(dp(300), dp(40)),
                md_bg_color=(0, 0.5, 1, 0.8),
                radius=[dp(10)] * 4,
                pos_hint={"right": 1}
            )
            bot_label = MDLabel(
                text=f"JARVIS: {bot_response}",
                halign="right",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                padding=(dp(10), dp(10))
            )
            bot_card.add_widget(bot_label)
            self.chat_container.add_widget(bot_card)

        # Scroll to the last chat message
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(self.chat_container.children[0]), 0.1)

    def speak(self, text):
        tts = gTTS(text=text, lang='en', slow=False)
        audio_file = "response.mp3"
        try:
            tts.save(audio_file)
            playsound(audio_file)
        except PlaysoundException as e:
            print(f"Playsound error: {e}")
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)

    def chatbot_response(self, text):
        text = text.lower()
        if "hello" in text or "hi" in text:
            return "Hello! How can I assist you today?"
        elif "time" in text:
            return "I’m not a clock, but I can chat with you!"
        elif "weather" in text:
            return "I can’t check the weather yet, but I’d love to learn how!"
        elif "joke" in text:
            return "Why don’t skeletons fight each other? Because they don’t have the guts!"
        else:
            return "Interesting! Tell me more or ask something specific."

    def transcribe_and_respond(self):
        Clock.schedule_once(lambda dt: self.update_chat("", "Listening..."), 0)

        def transcription_thread():
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 300
                
                try:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    if self.cancel_speech:
                        return
                    Clock.schedule_once(lambda dt: self.update_chat("", "Recognizing..."), 0)
                    text = self.recognizer.recognize_google(audio)
                    response = self.chatbot_response(text)
                    Clock.schedule_once(lambda dt: self.update_chat(text, response), 0)
                    Clock.schedule_once(lambda dt: self.speak(response), 0)
                except sr.WaitTimeoutError:
                    if not self.cancel_speech:
                        response = "Timed out waiting for you to speak."
                        Clock.schedule_once(lambda dt: self.update_chat("", response), 0)
                        Clock.schedule_once(lambda dt: self.speak(response), 0)
                except sr.UnknownValueError:
                    if not self.cancel_speech:
                        response = "Sorry, I couldn’t understand."
                        Clock.schedule_once(lambda dt: self.update_chat("", response), 0)
                        Clock.schedule_once(lambda dt: self.speak(response), 0)
                except sr.RequestError as e:
                    if not self.cancel_speech:
                        response = f"Service error: {e}"
                        Clock.schedule_once(lambda dt: self.update_chat("", response), 0)
                        Clock.schedule_once(lambda dt: self.speak(response), 0)

        threading.Thread(target=transcription_thread).start()

class JarvisApp(MDApp):
    def build(self):
        return JarvisUI()

if __name__ == "__main__":
    JarvisApp().run()