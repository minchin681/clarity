import openai
import wave
import pyaudio
import time
import os
import tempfile
from openai import OpenAI

client = OpenAI()

CHUNK_DURATION = 15  #seconds
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16

def record_audio(duration, filename):
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)

  
    frames = []
    for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
        data = stream.read(CHUNK_SIZE)
        frames.append(data)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))

    stream.stop_stream()
    stream.close()
    audio.terminate()

def transcribe(filename):
    with open(filename, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio_file, 
            language="ko", 
        )
        return response.text

def run_continuous_transcription():
    print("🔄 Starting continuous transcription. Press Ctrl+C to stop.")
    try:
        while True:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                record_audio(CHUNK_DURATION, tmp.name)
                transcript = transcribe(tmp.name)
                translate_text(transcript)
                #print(f"📝 Transcription: {transcript}\n{'-'*40}")
                #os.unlink(tmp.name)
    except KeyboardInterrupt:
        print("\n🛑 Transcription stopped by user.")


def translate_text(text):
    target_language = "english"
    prompt = f"Translate the following text to {target_language}:\n\n{text}. Please dont reply with Here is a translation of your text to English."
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
        {"role": "developer", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    print(response.choices[0].message.content)
    
if __name__ == "__main__":
    run_continuous_transcription()
    