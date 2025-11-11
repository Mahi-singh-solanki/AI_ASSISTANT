from threading import Thread,Lock,Event
from queue import Queue

wake_event=Event()
stop_event=Event()
mic_lock=Lock()
input_queue=Queue()
output_queue=Queue()
audio_queue=Queue()