import whisper
import wave
import sys
import pyaudio,struct
import pyttsx3,pvporcupine

ACCESS_KEY = "GGxt4UpkNVAhL2lOi2Sh0u8J3h/HNmUICwFqxQTtwjf6jvQ1SSIKSQ=="
KEYWORD_PATH = rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\hey-max_en_windows_v3_0_0.ppn"
SENSITIVITY = 0.6

def wake_up():
    porcupine=pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[KEYWORD_PATH],
        sensitivities=[SENSITIVITY]
    )
    p=pyaudio.PyAudio()
    audio_stream=p.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    print("Wake me...")
    while True:
        pcm=audio_stream.read(porcupine.frame_length,exception_on_overflow=False)
        pcm_unpacked=struct.unpack_from("h"*porcupine.frame_length,pcm)
        result=porcupine.process(pcm_unpacked)
        if result>=0:
            return True
        


def get_audio():
    CHUNK=1024
    FORMAT=pyaudio.paInt16
    CHANNELS=1 if sys.platform=='darwin' else 2
    RATE=44100
    RECORD_SECONDS=10

    with wave.open('output.wav','wb') as wf:
        p=pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream=p.open(format=
                  FORMAT,channels=CHANNELS,rate=RATE,input=True)
        print("Recording..")
        for _ in range(0,RATE//CHUNK*RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
        print('Done')

        stream.close()

        p.terminate()


def audio_to_text():
    model=whisper.load_model("base")
    audio=whisper.load_audio("output.wav")
    audio=whisper.pad_or_trim(audio)
    result = model.transcribe(audio,language="en")
    print(result["text"])
    return result["text"]


def text_to_audio(text):
    pyttsx3.speak(text)