import tkinter as tk
from tkinter import filedialog
import sounddevice as sd
import numpy as np
import whisper

class AudioTranscriber(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Audio Transcriber")
        self.geometry("400x150")

        self.label = tk.Label(self, text="Choose an option:")
        self.label.pack(pady=10)

        self.upload_btn = tk.Button(self, text="Upload Audio", command=self.upload_audio)
        self.upload_btn.pack(pady=5)

        self.record_btn = tk.Button(self, text="Record Audio", command=self.record_audio)
        self.record_btn.pack(pady=5)

        self.transcribe_btn = tk.Button(self, text="Transcribe", command=self.transcribe_audio, state=tk.DISABLED)
        self.transcribe_btn.pack(pady=10)

    def upload_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        if file_path:
            self.audio_data, self.sample_rate = whisper.read(file_path)
            self.transcribe_btn.config(state=tk.NORMAL)

    def record_audio(self):
        self.audio_data = None
        self.sample_rate = 44100  # Default sample rate (can be adjusted as needed)
        duration = 5  # Recording duration in seconds

        self.audio_data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1)
        sd.wait()  # Wait until recording is finished
        self.transcribe_btn.config(state=tk.NORMAL)

    def transcribe_audio(self):
        if self.audio_data is not None:
            text = whisper.transcribe(self.audio_data, sample_rate=self.sample_rate)
            self.display_transcription(text)

    def display_transcription(self, text):
        transcription_window = tk.Toplevel(self)
        transcription_window.title("Transcription Result")

        text_box = tk.Text(transcription_window, wrap=tk.WORD)
        text_box.insert(tk.END, text)
        text_box.pack(padx=10, pady=10)

if __name__ == "__main__":
    app = AudioTranscriber()
    app.mainloop()
