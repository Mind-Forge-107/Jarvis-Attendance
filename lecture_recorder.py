import cv2
import pyaudio
import wave
import numpy as np
from moviepy import VideoFileClip, AudioFileClip
import threading
import time
import os
import shutil
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.clock import Clock
import kivy

class LectureRecorder(App):
    def __init__(self):
        super().__init__()
        print(f"Kivy version: {kivy.__version__}")
        self.is_recording = False
        self.is_paused = False
        self.video_writer = None
        self.audio_stream = None
        self.audio_frames = []
        self.frame_count = 0
        self.recording_start_time = 0
        self.writer_lock = threading.Lock()  # Lock for video_writer access

        # Create recordings folder if it doesn't exist
        self.recordings_dir = "recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)

        # Store temporary files in recordings folder
        self.temp_video_path = os.path.join(self.recordings_dir, "temp_video.avi")
        self.temp_audio_path = os.path.join(self.recordings_dir, "temp_audio.wav")
        self.debug_audio_path = os.path.join(self.recordings_dir, "debug_audio.wav")  # For debugging

        self.output_format = '.mp4'
        self.record_mode = 'Video + Audio'

        # Initialize video capture
        self.cap = None
        if self.record_mode == 'Video + Audio':
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                print("Error: Cannot access camera at index 0. Trying index 1.")
                self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    print("Error: Cannot access camera. Disabling video.")
                    self.cap = None
                    self.record_mode = 'Audio Only'

        # Video properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if self.cap and self.cap.isOpened() else 640
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if self.cap and self.cap.isOpened() else 480
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) if self.cap and self.cap.isOpened() and self.cap.get(cv2.CAP_PROP_FPS) > 0 else 30
        print(f"Camera FPS: {self.fps}")

        # Audio properties
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.pyaudio_instance = pyaudio.PyAudio()

        # Start video preview after GUI initialization
        if self.record_mode == 'Video + Audio' and self.cap:
            Clock.schedule_once(lambda dt: self.start_preview(), 1)

    def start_preview(self):
        print("Starting preview thread")
        self.preview_thread = threading.Thread(target=self.update_preview, daemon=True)
        self.preview_thread.start()

    def build(self):
        print("Building GUI")
        Window.size = (400, 300)
        Window.top = 100
        Window.left = 100

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        title_label = Label(text="Lecture Recorder", font_size=24, size_hint_y=0.2)
        layout.add_widget(title_label)

        format_row = BoxLayout(size_hint_y=0.2, spacing=10)
        format_label = Label(text="Output Format:", size_hint_x=0.4)
        format_spinner = Spinner(text='.mp4', values=['.mp4', '.mkv', '.m4a'], size_hint_x=0.6)
        format_spinner.bind(text=self.set_output_format)
        format_row.add_widget(format_label)
        format_row.add_widget(format_spinner)
        layout.add_widget(format_row)

        mode_row = BoxLayout(size_hint_y=0.2, spacing=10)
        mode_label = Label(text="Record Mode:", size_hint_x=0.4)
        mode_spinner = Spinner(text='Video + Audio', values=['Video + Audio', 'Audio Only'], size_hint_x=0.6)
        mode_spinner.bind(text=self.set_record_mode)
        mode_row.add_widget(mode_label)
        mode_row.add_widget(mode_spinner)
        layout.add_widget(mode_row)

        button_row = BoxLayout(size_hint_y=0.4, spacing=10)
        start_button = Button(text="Start Recording")
        start_button.bind(on_press=self.start_recording)
        pause_button = Button(text="Pause", disabled=True)
        pause_button.bind(on_press=self.toggle_pause)
        stop_button = Button(text="Stop Recording", disabled=True)
        stop_button.bind(on_press=self.stop_recording)
        button_row.add_widget(start_button)
        button_row.add_widget(pause_button)
        button_row.add_widget(stop_button)
        layout.add_widget(button_row)

        layout.ids = {
            'format_spinner': format_spinner,
            'mode_spinner': mode_spinner,
            'start_button': start_button,
            'pause_button': pause_button,
            'stop_button': stop_button
        }

        print("GUI built, layout children:", layout.children)
        return layout

    def set_output_format(self, spinner, text):
        self.output_format = text
        print(f"Output format set to: {self.output_format}")

    def set_record_mode(self, spinner, text):
        self.record_mode = text
        print(f"Record mode set to: {self.record_mode}")
        if self.is_recording:
            print("Cannot change mode during recording.")
            return
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
        if self.record_mode == 'Video + Audio':
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    print("Error: Cannot access camera.")
                    self.cap = None
                    self.record_mode = 'Audio Only'
                    return
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if self.cap.isOpened() else 640
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if self.cap.isOpened() else 480
            self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) if self.cap and self.cap.isOpened() and self.cap.get(cv2.CAP_PROP_FPS) > 0 else 30
            print(f"Camera FPS: {self.fps}")
            Clock.schedule_once(lambda dt: self.start_preview(), 1)
        else:
            self.cap = None

    def update_preview(self):
        print("Starting video preview")
        if not self.cap or not self.cap.isOpened():
            print("No valid camera for preview")
            return
        while self.record_mode == 'Video + Audio' and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame")
                break
            cv2.imshow("Live Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Preview closed by user")
                break
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Video preview stopped")

    def start_recording(self, instance):
        if self.is_recording:
            return
        self.is_recording = True
        self.is_paused = False
        self.frame_count = 0
        self.recording_start_time = time.time()
        try:
            self.root.ids.start_button.disabled = True
            self.root.ids.pause_button.disabled = False
            self.root.ids.stop_button.disabled = False
            self.root.ids.pause_button.text = "Pause"
        except AttributeError as e:
            print(f"Error accessing button IDs: {e}")

        # Initialize video writer
        if self.record_mode == 'Video + Audio' and self.cap and self.cap.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            with self.writer_lock:
                self.video_writer = cv2.VideoWriter(self.temp_video_path, fourcc, self.fps,
                                                    (self.frame_width, self.frame_height))
                if not self.video_writer.isOpened():
                    print("Error: Failed to initialize VideoWriter")
                    self.video_writer = None
                    self.record_mode = 'Audio Only'
                else:
                    print("VideoWriter initialized successfully")

        # Initialize audio stream
        self.audio_frames = []
        self.audio_stream = self.pyaudio_instance.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        # Start video and audio threads together
        if self.record_mode == 'Video + Audio' and self.cap and self.cap.isOpened() and self.video_writer:
            self.video_thread = threading.Thread(target=self.record_video, daemon=True)
            self.video_thread.start()
        self.audio_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.audio_thread.start()

        print("Recording started.")

    def toggle_pause(self, instance):
        if not self.is_recording:
            return
        self.is_paused = not self.is_paused
        try:
            self.root.ids.pause_button.text = "Resume" if self.is_paused else "Pause"
        except AttributeError as e:
            print(f"Error accessing pause_button: {e}")
        print("Recording paused." if self.is_paused else "Recording resumed.")

    def record_video(self):
        if not self.cap or not self.cap.isOpened():
            print("No valid camera for recording")
            return
        frame_interval = 1 / self.fps
        while self.is_recording and self.record_mode == 'Video + Audio':
            if not self.is_paused:
                start_time = time.time()
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame")
                    break
                with self.writer_lock:
                    if self.video_writer is None:
                        print("VideoWriter is None, stopping video recording")
                        break
                    self.video_writer.write(frame)
                self.frame_count += 1
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                time.sleep(sleep_time)
        print(f"Recorded {self.frame_count} frames")

    def record_audio(self):
        while self.is_recording:
            if not self.is_paused:
                data = self.audio_stream.read(self.chunk, exception_on_overflow=False)
                self.audio_frames.append(data)

    def stop_recording(self, instance):
        if not self.is_recording:
            return
        self.is_recording = False
        self.is_paused = False
        recording_end_time = time.time()
        recording_duration = recording_end_time - self.recording_start_time
        print(f"Recording duration: {recording_duration:.2f} seconds")

        # Calculate actual FPS
        if self.frame_count > 0 and recording_duration > 0:
            actual_fps = self.frame_count / recording_duration
            print(f"Actual FPS: {actual_fps:.2f}")
        else:
            actual_fps = self.fps
            print("Warning: No frames recorded or invalid duration")

        try:
            self.root.ids.start_button.disabled = False
            self.root.ids.pause_button.disabled = True
            self.root.ids.stop_button.disabled = True
            self.root.ids.pause_button.text = "Pause"
        except AttributeError as e:
            print(f"Error accessing button IDs: {e}")

        # Release video writer
        with self.writer_lock:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

        # Stop and close audio stream
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None

        # Save audio to temp file
        wf = wave.open(self.temp_audio_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.audio_format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()

        # Debug audio file
        if os.path.exists(self.temp_audio_path):
            audio_size = os.path.getsize(self.temp_audio_path)
            print(f"Audio file size: {audio_size} bytes")
            if audio_size < 1000:
                print("Warning: Audio file appears to be empty or very small")
            # Keep a copy for debugging
            shutil.copy(self.temp_audio_path, self.debug_audio_path)
            print(f"Copied audio to {self.debug_audio_path} for debugging")
        else:
            print("Error: Audio file was not created")

        # Save final file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.recordings_dir, f"lecture_{timestamp}{self.output_format}")
        try:
            if self.record_mode == 'Video + Audio' and os.path.exists(self.temp_video_path):
                video_clip = VideoFileClip(self.temp_video_path)
                audio_clip = AudioFileClip(self.temp_audio_path)
                print(f"Video duration: {video_clip.duration:.2f} seconds")
                print(f"Audio duration: {audio_clip.duration:.2f} seconds")

                # Trim video to match audio duration
                if video_clip.duration > audio_clip.duration:
                    video_clip = video_clip.subclip(0, audio_clip.duration)
                    print(f"Trimmed video to match audio duration: {video_clip.duration:.2f} seconds")

                # Write final video with audio
                if self.output_format in ['.mp4', '.mkv']:
                    video_clip.write_videofile(
                        output_path,
                        codec='libx264',
                        audio=audio_clip,
                        audio_codec='mp3',  # Changed to mp3
                        fps=actual_fps
                    )
                elif self.output_format == '.m4a':
                    audio_clip.write_audiofile(output_path, codec='mp3')
                video_clip.close()
                audio_clip.close()
            else:
                audio_clip = AudioFileClip(self.temp_audio_path)
                audio_clip.write_audiofile(output_path, codec='mp3')
                audio_clip.close()
            print(f"Recording saved as {output_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

        # Clean up temporary files
        for temp_file in [self.temp_video_path, self.temp_audio_path]:
            if os.path.exists(temp_file):
                for attempt in range(3):
                    try:
                        os.remove(temp_file)
                        print(f"Deleted temporary file: {temp_file}")
                        break
                    except PermissionError as e:
                        print(f"Attempt {attempt + 1}: Failed to delete {temp_file}: {e}")
                        time.sleep(1)
                else:
                    print(f"Warning: Could not delete {temp_file}. It may still be in use.")

    def on_stop(self):
        if self.is_recording:
            print("Please stop recording before closing.")
            return
        if self.cap:
            self.cap.release()
        self.pyaudio_instance.terminate()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    print("Starting Kivy app")
    try:
        LectureRecorder().run()
    except Exception as e:
        print(f"Application failed: {e}")