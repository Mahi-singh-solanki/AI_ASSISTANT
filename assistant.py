from threading import Thread,Event
from PIL import Image
from pystray import Icon as icon,Menu,MenuItem as item
import time,sys
from rag.pipeline import processor
from rag.voice import wake_up,get_audio,text_to_audio,audio_to_text
from rag.tasks import reminder
from log.log import get_logger

listening_enabled=True
wake_word_enabled=True
shutdown_event=Event()

def pause_listening(icon, item):
    global listening_enabled
    listening_enabled = False
    print("Listening paused")


def resume_listening(icon, item):
    global listening_enabled
    listening_enabled = True
    print("Listening resumed")


def restart_wake_word(icon, item):
    global wake_word_enabled
    wake_word_enabled = True
    print("Wake word detection restarted")


def show_status(icon, item):
    print(f"Listening: {listening_enabled} | Wake Word: {wake_word_enabled}")


def quit_assistant(icon, item):
    shutdown_event.set()
    print("Shutting down assistant…")
    icon.stop()

def load_icon():
    return Image.open("assets/virtual-assistant.png")

def build_menu():
    return (
        item("Pause Listening", pause_listening),
        item("Resume Listening", resume_listening),
        item("Restart Wake Word", restart_wake_word),
        item("Show Status", show_status),
        item("Quit Assistant", quit_assistant)
    )

def start_threads():
    threads=[
        Thread(target=wake_up,daemon=True),
        Thread(target=get_audio,daemon=True),
        Thread(target=audio_to_text,daemon=True),
        Thread(target=processor,daemon=True),
        Thread(target=reminder,daemon=True),
        Thread(target=text_to_audio,daemon=True)
    ]
    for t in threads:
        t.start()

def main():
    logger=get_logger()
    logger.info("==Assistant started==")
    logger.info("Python version: %s", sys.version)
    logger.info("Using Whisper: base | Wake word: max.ppn")

    start_threads()

    tray_icon=icon(
        "Personal Assistant",
        load_icon(),
        "Assistant Running",
        menu=Menu(*build_menu())
    )
    tray_icon.run()
    logger.info("Assistant shutting down gracefully.")


if __name__ == "__main__":
    main()
