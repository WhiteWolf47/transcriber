import tkinter as tk

from pygame import mixer

class AudioTranscriber(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.text = tk.Text(self, font=("Helvetica", 16))
        self.text.pack(fill="both", expand=True)
        self.playpause = False
        self.setup_widgets()

    def setup_widgets(self):
        tk.Button(root, command=self.play).pack()

    def play(self):
        if not self.playpause:
            mixer.init()
            sound = mixer.Sound("audio1.mp3")
            sound.play()
            self.playpause = True
        else:
            mixer.stop()
            self.playpause = False

if __name__ == "__main__":
    root = tk.Tk()

    root.title("Audio Transcriber")

    app = AudioTranscriber(root)
    app.pack(fill="both", expand=True)

    root.mainloop()