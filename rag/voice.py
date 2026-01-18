import whisper
import wave
import sys,os
import pyaudio,struct
import pvporcupine
from rag.globals import wake_event,mic_lock,input_queue,output_queue,audio_queue,stop_event
from log.log import get_logger
import numpy as np
import pyttsx3

logger=get_logger()

access_key = "GGxt4UpkNVAhL2lOi2Sh0u8J3h/HNmUICwFqxQTtwjf6jvQ1SSIKSQ=="
KEYWORD_PATH = rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\hey-max_en_windows_v3_0_0.ppn"
SENSITIVITY = 0.6



def wake_up():
    porcupine=pvporcupine.create(
        access_key=access_key,
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
  
    try:
        logger.info("Waking up...")
        while True:
            stop_event.wait()
            pcm=audio_stream.read(porcupine.frame_length,exception_on_overflow=False)
            pcm_unpacked=struct.unpack_from("h"*porcupine.frame_length,pcm)
            result=porcupine.process(pcm_unpacked)
            if result>=0:
                logger.info("assistant listening")
                wake_event.set()
    except Exception as e:
        logger.exception(e)


def get_audio():
    try:
        while True:
            wake_event.wait()
            CHUNK=1024
            FORMAT=pyaudio.paInt16
            CHANNELS=1 if sys.platform=='darwin' else 2
            RATE=44100
            RECORD_SECONDS=6
            logger.info("Recording started..")
            with wave.open('output.wav','wb') as wf:
                p=pyaudio.PyAudio()
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)

                stream=p.open(format=
                  FORMAT,channels=CHANNELS,rate=RATE,input=True)
                with mic_lock:
                    for _ in range(0,RATE//CHUNK*RECORD_SECONDS):
                        wf.writeframes(stream.read(CHUNK))
                stream.close()
                p.terminate()
            logger.info("Recorded")
            audio_queue.put('output.wav')
            wake_event.clear()
    except Exception as e:
        logger.exception(e)

def manual_audio():
    try:
            CHUNK=1024
            FORMAT=pyaudio.paInt16
            CHANNELS=1 if sys.platform=='darwin' else 2
            RATE=44100
            RECORD_SECONDS=6
            logger.info("Recording started..")
            with wave.open('output.wav','wb') as wf:
                p=pyaudio.PyAudio()
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)

                stream=p.open(format=
                  FORMAT,channels=CHANNELS,rate=RATE,input=True)
                with mic_lock:
                    for _ in range(0,RATE//CHUNK*RECORD_SECONDS):
                        wf.writeframes(stream.read(CHUNK))
                stream.close()
                p.terminate()
            logger.info("Recorded")
            text=manual_audio_to_text('output.wav')
            return text
    except Exception as e:
        logger.exception(e)

def manual_audio_to_text(audio):
    try:
            logger.info("Converting to text")
            model=whisper.load_model("small")
            audio=whisper.load_audio("output.wav")
            audio=whisper.pad_or_trim(audio)
            result = model.transcribe(audio,language="en")
            logger.info(f"Converted audio text - {result["text"]}")
            text=result["text"]
            return text
    except Exception as e:
        logger.exception(e)

def audio_to_text():
    try:
        while True:
            audio=audio_queue.get()
            logger.info("Converting to text")
            model=whisper.load_model("small")
            audio=whisper.load_audio("output.wav")
            audio=whisper.pad_or_trim(audio)
            result = model.transcribe(audio,language="en")
            logger.info(f"Converted audio text - {result["text"]}")
            text=result["text"]
            input_queue.put(text)
    except Exception as e:
        logger.exception(e)


def text_to_audio():
    try:
        while True:
            text=output_queue.get()
            # engine=pyttsx3.init()
            # voices=engine.getProperty("voices")
            # engine.setProperty("voice",voices[1].id)
            # engine.setProperty("rate", 190)
            logger.info("Text is converting to audio")
            pyttsx3.speak(text)
            # engine.say(text)
            # engine.runAndWait()
            logger.info("converted to audio")
    except Exception as e:
        logger.exception(e)