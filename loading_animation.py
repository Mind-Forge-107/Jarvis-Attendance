from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.label import MDLabel

# Set window size (optional, adjust as needed)
Window.size = (800, 450)

# Make the window borderless (removes title bar and borders)
Window.borderless = True

class LoadingScreenApp(MDApp):
    def build(self):
        self.screen = Builder.load_file("loading_animation.kv")
        return self.screen

    def on_start(self):
        # Start the animations when the app starts
        Clock.schedule_once(self.start_animations, 0)
        # Start the background color animation
        Clock.schedule_once(self.start_background_animation, 0)

    def start_animations(self, dt):
        # Animate the progress bar and percentage
        progress_bar = self.screen.ids.progress_bar
        percentage_label = self.screen.ids.percentage_label
        loading_label = self.screen.ids.loading_label  # Reference to the loading label

        # Animate progress bar from 0 to 100 over 5 seconds
        anim = Animation(value=100, duration=5)
        anim.start(progress_bar)

        # Update percentage text as the progress bar animates
        def update_percentage(instance, value):
            percentage_label.text = f"{int(value)} %"
            # Check if progress bar has reached 100%
            if int(value) >= 100:
                # Stop the "loading..." dots animation
                Clock.unschedule(update_dots)
                # Make the "loading..." text disappear
                loading_label.opacity = 0  # Set opacity to 0 to hide the label

        # Bind the progress update
        anim.bind(on_progress=lambda instance, widget, progress: update_percentage(progress_bar, progress_bar.value))

        # Animate the "loading..." dots
        dots = ["", ".", "..", "..."]
        dot_index = 0

        def update_dots(dt):
            nonlocal dot_index
            loading_label.text = f"loading{dots[dot_index]}"
            dot_index = (dot_index + 1) % len(dots)

        # Schedule the dots animation to update every 0.5 seconds
        Clock.schedule_interval(update_dots, 0.5)

    def start_background_animation(self, dt):
        # Define a list of colors to cycle through for the top-left and bottom-right
        top_left_colors = [
            (1, 0.8, 0, 1),    # Yellow
            (0.2, 0.8, 0.4, 1), # Light Green
            (0, 0.6, 0.8, 1),   # Cyan
            (0.8, 0.2, 0.6, 1), # Purple
        ]
        bottom_right_colors = [
            (0, 0.7, 0.6, 1),   # Teal
            (0, 0.4, 0.8, 1),   # Blue
            (0.6, 0.2, 0.8, 1), # Magenta
            (0.8, 0.6, 0.2, 1), # Orange
        ]

        # Get references to the canvas instructions for color updates
        canvas = self.screen.canvas.before
        top_left_color_instruction = canvas.get_group('top_left_color')[0]  # First Color instruction
        bottom_right_color_instruction = canvas.get_group('bottom_right_color')[0]  # Second Color instruction

        # Get reference to the progress bar
        progress_bar = self.screen.ids.progress_bar

        # Animation function to cycle through colors
        def animate_colors(index=0):
            # Check if the progress bar has reached 100%
            if progress_bar.value >= 100:
                return  # Stop the animation loop by not scheduling the next change

            # Get the next colors
            top_left_next = top_left_colors[index % len(top_left_colors)]
            bottom_right_next = bottom_right_colors[index % len(bottom_right_colors)]

            # Create animations for both colors
            anim_top = Animation(rgba=top_left_next, duration=1.5)
            anim_bottom = Animation(rgba=bottom_right_next, duration=1.5)

            # Start the animations
            anim_top.start(top_left_color_instruction)
            anim_bottom.start(bottom_right_color_instruction)

            # Schedule the next color change, but only if progress is less than 100%
            Clock.schedule_once(lambda dt: animate_colors(index + 1), 1.5)

        # Start the color animation loop
        animate_colors()

if __name__ == "__main__":
    LoadingScreenApp().run()