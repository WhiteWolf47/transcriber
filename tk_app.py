import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import sounddevice as sd
import numpy as np
import whisper
import os


class AudioTranscriber(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create the Azure theme
        self.setup_azure_theme()

        # Create control variables
        self.audio_data = None
        self.sample_rate = None
        self.is_recording = False
        self.recording_stream = None
        self.playback_stream = None
        self.playback_callback = None
        self.realtime_audio_data = None
        self.realtime_stream = None
        self.selected_model = "base"  # Default model selection

        # Create widgets
        self.setup_widgets()

    def setup_azure_theme(self):
        self.master.tk.call("source", "azure.tcl")
        self.master.tk.call("set_theme", "dark")

    def setup_widgets(self):
        # Create a Frame for the model selection options
        self.model_frame = ttk.LabelFrame(self, text="Model Options", padding=(20, 10))
        self.model_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Model Selection Dropdown
        self.model_selection_label = ttk.Label(self.model_frame, text="Select Model:")
        self.model_selection_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")  # Align to the left

        self.models = ["tiny", "base", "small"]
        self.model_var = tk.StringVar(value="base")  # Default model selection
        self.model_selection_dropdown = ttk.Combobox(self.model_frame, textvariable=self.model_var, values=self.models, state="readonly")
        self.model_selection_dropdown.grid(row=0, column=1, padx=5, pady=10, sticky="ew")  # Expand horizontally

        # Create a Frame for the audio options
        self.audio_frame = ttk.LabelFrame(self, text="Audio Options", padding=(20, 10))
        self.audio_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Upload Audio Button
        self.upload_btn = ttk.Button(self.audio_frame, text="Upload Audio", command=self.upload_audio)
        self.upload_btn.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        # Record Audio Button
        self.record_btn = ttk.Button(self.audio_frame, text="Record Audio", command=self.toggle_record)
        self.record_btn.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

        # Progress Bar for Recording
        self.progress_bar = ttk.Progressbar(self.audio_frame, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")

        # Play Audio Button
        self.play_btn = ttk.Button(self.audio_frame, text="Play Audio", command=self.toggle_play)
        self.play_btn.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Pause Audio Button
        self.pause_btn = ttk.Button(self.audio_frame, text="Pause Audio", command=self.toggle_play)
        self.pause_btn.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")
        self.pause_btn.grid_remove()

        # Progress Bar for Playback
        self.playback_progress_bar = ttk.Progressbar(self.audio_frame, orient="horizontal", length=200, mode="determinate")
        self.playback_progress_bar.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")
        self.playback_progress_bar.grid_remove()

        # Transcribe Button
        self.transcribe_btn = ttk.Button(self.audio_frame, text="Transcribe", command=self.transcribe_audio, state=tk.DISABLED)
        self.transcribe_btn.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")

        # Save Transcription Button
        self.save_btn = ttk.Button(self.audio_frame, text="Save Transcription", command=self.save_transcription, state=tk.DISABLED)
        self.save_btn.grid(row=7, column=0, padx=5, pady=10, sticky="nsew")

        # Create a button for real-time transcription
        self.realtime_btn = ttk.Button(self.audio_frame, text="Real-time Transcription", style='Accent.TButton', command=self.toggle_realtime)
        self.realtime_btn.grid(row=8, column=0, padx=5, pady=10, sticky="nsew")

        # Real-time transcription variables
        self.realtime_audio_data = None
        self.realtime_stream = None

        # Create a Frame for the transcribed text
        self.transcription_frame = ttk.LabelFrame(self, text="Transcribed Text", padding=(20, 10))
        self.transcription_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        self.transcription_frame.columnconfigure(0, weight=1)
        self.transcription_frame.rowconfigure(0, weight=1)

        # Transcribed Text Widget
        self.transcribed_text = tk.Text(self.transcription_frame, wrap="word")
        self.transcribed_text.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

    def toggle_realtime(self):
        if self.realtime_stream is None:
            self.realtime_btn.config(text="Stop Real-time Transcription")
            self.start_realtime_transcription()
        else:
            self.realtime_btn.config(text="Real-time Transcription")
            self.stop_realtime_transcription()

    def start_realtime_transcription(self):
        self.realtime_audio_data = np.array([])
        self.sample_rate = 44100  # Default sample rate (can be adjusted as needed)

        def audio_callback(indata, frames, time, status):
            if self.realtime_stream is not None:
                self.realtime_audio_data = np.append(self.realtime_audio_data, indata.flatten())
                # Perform real-time transcription here
                transcribed_text = self.perform_realtime_transcription()
                self.transcribed_text.config(state=tk.NORMAL)
                self.transcribed_text.delete("1.0", tk.END)
                self.transcribed_text.insert(tk.END, transcribed_text)
                self.transcribed_text.config(state=tk.DISABLED)

        self.realtime_stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=self.sample_rate)
        self.realtime_stream.start()

    def stop_realtime_transcription(self):
        if self.realtime_stream:
            self.realtime_stream.stop()
            self.realtime_stream.close()
            self.realtime_stream = None

    def perform_realtime_transcription(self):
        # Call your real-time transcription logic using Whisper here
        if self.realtime_audio_data is not None:
            model = whisper.load_model(self.selected_model)
            result = model.transcribe(self.realtime_audio_data)
            return result

        return "No real-time audio data available."


    def generate_random_string(self, length=8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def save_audio(self, audio_data, sample_rate):
        folder_path = "audios"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if self.audio_file_path is None:
            filename = f"audio_{self.generate_random_string()}.wav"
        else:
            filename = os.path.basename(self.audio_file_path)

        file_path = os.path.join(folder_path, filename)
        whisper.write(file_path, audio_data, sample_rate)
        return file_path

    def upload_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        if file_path:
            self.audio_data, self.sample_rate = whisper.read(file_path)
            self.audio_file_path = file_path
            self.transcribe_btn.config(state=tk.NORMAL)
            self.play_btn.config(state=tk.NORMAL)
    def toggle_record(self):
        if not self.is_recording:
            self.is_recording = True
            self.progress_bar.start(500)  # Start the progress bar animation
            self.record_btn.config(text="Stop Recording")
            self.transcribe_btn.config(state=tk.DISABLED)
            self.play_btn.config(state=tk.DISABLED)
            self.pause_btn.grid_remove()
            self.start_recording()
        else:
            self.is_recording = False
            self.progress_bar.stop()  # Stop the progress bar animation
            self.record_btn.config(text="Record Audio")
            self.transcribe_btn.config(state=tk.NORMAL)
            self.play_btn.config(state=tk.NORMAL)
            self.pause_btn.grid_remove()
            self.stop_recording()

    def start_recording(self):
        self.audio_data = None
        self.sample_rate = 44100  # Default sample rate (can be adjusted as needed)

        def audio_callback(indata, frames, time, status):
            if self.is_recording:
                if self.audio_data is None:
                    self.audio_data = np.array([])
                self.audio_data = np.append(self.audio_data, indata.flatten())

        self.recording_stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=self.sample_rate)
        self.recording_stream.start()

    def stop_recording(self):
        if self.recording_stream:
            self.recording_stream.stop()
            self.recording_stream.close()
            self.recording_stream = None

    def toggle_play(self):
        if self.audio_data is not None:
            if self.playback_stream is None:
                self.play_btn.grid_remove()
                self.pause_btn.grid()
                self.playback_progress_bar.grid()
                self.play_audio()
            else:
                self.play_btn.grid()
                self.pause_btn.grid_remove()
                self.playback_progress_bar.grid_remove()
                self.pause_audio()

    def play_audio(self):
        if self.audio_data is not None:
            self.playback_stream = sd.OutputStream(callback=self.playback_callback, channels=1, samplerate=self.sample_rate)
            self.playback_stream.start()

    def pause_audio(self):
        if self.playback_stream:
            self.playback_stream.stop()
            self.playback_stream.close()
            self.playback_stream = None

    def playback_callback(self, outdata, frames, time, status):
        if len(self.audio_data) == 0:
            return
        playback_ratio = outdata.shape[0] / self.audio_data.shape[0]
        current_index = int(self.playback_progress_bar["value"] * playback_ratio)
        current_index = min(current_index, self.audio_data.shape[0])
        outdata[:, 0] = self.audio_data[:current_index].reshape(-1, 1)
        self.playback_progress_bar["value"] = current_index / playback_ratio

    def perform_transcription(self, audio_file_path):
        model = whisper.load_model("base")
        result = model.transcribe(audio_file_path)
        return result

    def transcribe_audio(self):
        if self.audio_data is not None:
            self.transcribed_text.config(state=tk.NORMAL)  # Enable the widget to insert text
            self.transcribed_text.delete("1.0", tk.END)  # Clear the text widget

            # Call your transcribe function here
            model = whisper.load_model(self.selected_model)
            transcribed_text = model.transcribe(self.audio_data)  # Replace this with your transcription logic

            self.transcribed_text.insert(tk.END, transcribed_text)
            self.transcribed_text.config(state=tk.DISABLED)  # Disable the widget to prevent editing
            self.save_btn.config(state=tk.NORMAL)

    def save_transcription(self):
        if self.audio_data is not None:
            # Ask the user for the desired filename
            filename = simpledialog.askstring("Save Transcription", "Enter the filename (without extension):")
            if not filename:
                return

            # Create a folder if it doesn't exist
            if not os.path.exists("transcribedtxt"):
                os.makedirs("transcribedtxt")

            # Save the transcription as a .txt file
            file_path = os.path.join("transcribedtxt", f"{filename}.txt")
            with open(file_path, "w") as file:
                file.write(self.transcribed_text.get("1.0", tk.END))
            messagebox.showinfo("Transcription Saved", f"Transcription saved as {filename}.txt in the 'transcribedtxt' folder.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Audio Transcriber")

    app = AudioTranscriber(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

    root.mainloop()