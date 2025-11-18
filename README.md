Personal AI Desktop Assistant (Offline RAG + Wake Word + Automation + Reminders)

A fully offline, wake-word activated, personal AI assistant built in Python using:

Ollama (Mistral) for LLM

Whisper for speech-to-text

pyttsx3 for text-to-speech

pvporcupine for wake-word detection

Chromadb + LangChain for RAG

Threading + Queues for parallel processing

Pystray for system tray integration

Windows automations for running tasks

Reminder Scheduler for notifications

Runs 100% locally, works in background, starts automatically at boot, and responds via wake-word.

🚀 Project Features
✔ Wake-word activation (Porcupine)
✔ Voice command recording
✔ Whisper speech-to-text
✔ RAG pipeline (context-aware answers)
✔ Personal memory
✔ Task automation (open apps, music, YouTube, browser, VS Code, notepad write, etc.)
✔ Reminders with notification system
✔ System tray menu (pause/resume/quit)
✔ Auto-start on system boot
✔ Multi-threaded architecture
📂 Project Structure
AI_ASSISTANT/
│── assistant.py              # Main entry point (starts wake-word, pipeline, tray)
│── rag/
│     ├── pipeline.py         # Retrieval, memory, LLM pipeline
│     ├── voice.py            # Audio recording, STT, TTS
│     ├── tasks.py            # Task automations + reminders
│     ├── embeddings/
│     │      ├── vector.py    # Main RAG database
│     │      ├── memory_vector.py
│── data/
│     ├── chunks.json         # Your RAG knowledge base
│── wakeword/
│     ├── custom.ppn          # Wake-word file
│── history.json              # Conversation history
│── memory.json               # Stored user facts
│── reminders.json            # Reminder storage
│── requirements.txt
│── start_assistant.bat
│── run_assistant.vbs


Your folders may differ slightly — but these are the required components.

🔧 Installation
1. Install Python 3.10–3.11

Recommended: Python 3.10 or 3.11 (Whisper & Porcupine are most stable here).

2. Install Ollama

Download: https://ollama.com

Then pull your main model:

ollama pull mistral


Or whichever you use: mistral-nemo, llama3.2, etc.

3. Create a Virtual Environment
python -m venv venv
venv\Scripts\activate

4. Install Requirements
pip install -r requirements.txt


Make sure these libraries are present:

whisper

pvporcupine

langchain

langchain_ollama

langchain_chroma

chromadb

pystray

pyaudio

pyttsx3 / piper-tts

numpy

winotify

psutil

playwright

📁 Required JSON Files

Create these three files manually in the project root:

history.json
[]

memory.json
[]

reminders.json
[]


These are used for:

recent conversation context

permanent memory (facts about user)

pending reminders

🎧 Wake Word Setup (Porcupine)

You must supply your own wake-word .ppn file.

Steps:

1. Go to Picovoice Console

https://console.picovoice.ai/

2. Sign up → Create Wake Word

Choose:

Language: English

Wake word: anything (“Athena”, “Hey Neo”, etc.)

Download the .ppn file and place it in:

wakeword/yourword.ppn

3. Add your Porcupine Access Key

Create an environment variable:

setx PV_ACCESS_KEY "your-access-key-here"


Or hardcode it (not recommended).

🔊 Whisper Speech-to-Text Setup

Whisper must download its model files the first time.

Use:

import whisper
model = whisper.load_model("base")


This auto-downloads weights to:

%USERPROFILE%\.cache\whisper

🔥 Running the Assistant (Development Mode)
venv\Scripts\activate
python assistant.py


You should see:

wake-word detection

recording

whisper decoding

RAG answering

text-to-speech

reminders

tray icon

🌙 Auto-Start on Windows Boot (RECOMMENDED)


✔ Step: Add run_assistant.vbs to Startup

Press:

Win + R → shell:startup


Paste the .vbs file here.

Now it auto-starts silently in background.
🔄 Updating the Project

When updating your assistant:

1. Update requirements.txt
pip freeze > requirements.txt

2. Reinstall dependencies
pip install -r requirements.txt

3. If you modify wake-word

Replace only the .ppn file inside wakeword/.

4. If you modify embeddings

Run the embedding sync logic (your code already handles this).

5. If you update main logic

No need to rebuild EXE — autostart will still work with .bat + .vbs system.

🎉 You're Now Ready

Your assistant is now:

✔ Offline
✔ Wake-word activated
✔ Full RAG
✔ Task automation
✔ Scheduled reminders
✔ Auto-starting
✔ Tray controlled
✔ Multi-threaded
✔ Local & private
