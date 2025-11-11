from threading import Thread
import time,sys
from rag.pipeline import processor
from rag.voice import wake_up,get_audio,text_to_audio,audio_to_text
from log.log import get_logger

logger=get_logger()
logger.info("==Assistant started==")
logger.info("Python version: %s", sys.version)
logger.info("Using Whisper: base | Wake word: max.ppn")
threads=[
    Thread(target=wake_up,daemon=True),
    Thread(target=get_audio,daemon=True),
    Thread(target=audio_to_text,daemon=True),
    Thread(target=processor,daemon=True),
    Thread(target=text_to_audio,daemon=True)
]


for t in threads:
    t.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Assistant shutting down gracefully.")
except Exception as e:
    logger.info(f"Something Happened program crashed error - {e}")