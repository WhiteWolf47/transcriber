import gradio as gr
import openai
import os

openai.api_key = "API_KEY"

def speech_to_text(audio_data):

    response = openai.WhisperRecognize.complete(audio=audio_data)

    if response["error"]:
        raise ValueError("Failed to convert speech to text.")

    return response["transcriptions"][0]["text"]

def record_audio_and_convert(audio):
    if audio is None:
        raise ValueError("No audio provided.")

    if isinstance(audio, str):

        with open(audio, "rb") as f:
            audio_data = f.read()
    else:

        sample_rate = audio.samplerate
        audio_data = audio.record.astype("float32").tobytes()

    try:

        text = speech_to_text(audio_data)
        return text
    except Exception as e:
        raise ValueError(f"Error: {str(e)}")

# Gradio interface
audio_input = [
    gr.inputs.Audio(source="upload", label="Upload Audio"),
    gr.inputs.Audio(source="microphone", label="Record Audio"),
]
text_output = gr.outputs.Textbox(label="Text Output")

gr.Interface(
    fn=record_audio_and_convert,
    inputs=audio_input,
    outputs=text_output,
    title="Speech to Text",
    description="Convert speech to text using OpenAI's Whisper API. Choose to either upload an audio file or record audio.",
    server_port=os.environ.get("GRADIO_SERVER_PORT", 7860),
).launch()
