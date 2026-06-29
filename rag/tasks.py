import os,pyautogui,time,re,json,requests
from playwright.sync_api import sync_playwright
from rag.globals import output_queue,gesture_event
import psutil as p
from datetime import datetime,timedelta
from winotify import Notification
from rag.voice import manual_audio
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

url = "https://ai-scheduler-xzk0.onrender.com/planner"

@tool
def play_music(name):
    """Play on Spotify of which the song name is provided, search and play it."""
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(3)
    pyautogui.click(788,38)
    pyautogui.write(name)
    time.sleep(3)
    pyautogui.click(665,291)
    return "playing music..."

@tool
def play_music_without_name():
    """Play or resume music on Spotify. If a song name is provided, search and play it."""
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(3)
    pyautogui.press('space')
    time.sleep(2)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    return "playing music..."

@tool
def reminder_create(message):
    """create a reminder for user using message as input """
    template = """
You are a reminder parser.

Convert the user's reminder request into a JSON object.

You will receive:
- user_input
- current_time (YYYY-MM-DD HH:MM:SS)

Return ONLY valid JSON in this format:

{{
    "text": "...",
    "time": "YYYY-MM-DD HH:MM:SS",
    "repeat": "none | daily | weekly",
    "status": "pending"
}}

Rules:

1. Convert every relative or natural language time into an absolute timestamp using current_time.

Examples:
- in 10 minutes
- in 2 hours
- tomorrow at 8 PM
- next Monday at 10 AM
- tonight
- today at 5

The output time MUST always be:
YYYY-MM-DD HH:MM:SS

2. Repeat rules:
- daily, every day, each day → "daily"
- weekly, every week, each week, every Monday → "weekly"
- otherwise → "none"

3. Reminder text:
- Keep only the task.
- Remove all reminder phrases and time expressions.
- Examples:
    "Remind me to drink water at 6 PM"
        → "drink water"

    "Remind me in 30 minutes to call John"
        → "call John"

    "Remind me tomorrow to pay electricity bill"
        → "pay electricity bill"

4. Do not change the intended reminder time.
5. Return ONLY JSON.
6. Do not use markdown.
7. Do not explain anything.

Current Time:
{current_time}

User Input:
{input}
"""
    prompt=ChatPromptTemplate.from_template(template)
    model=ChatOllama(model="mistral:instruct",temperature=0)
    chain=prompt | model
    result=chain.invoke({"input":message,"current_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    data=json.loads(result.content)
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
        prev=json.load(f)
    prev.append(data)
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","w") as f:
        json.dump(prev,f,indent=4)


@tool
def resume_music():
    """Resume the currently stopped music in Spotify."""
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(2)
    pyautogui.press('space')
    time.sleep(2)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    return "stopping music..."
@tool
def stop_music():
    """Pause the currently playing music in Spotify."""
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(2)
    pyautogui.press('space')
    time.sleep(2)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    return "stopping music..."

@tool
def open_vscode():
    """Open Visual Studio Code."""
    os.system("start code")
    time.sleep(1)
    os.system("taskkill /f /im cmd.exe")
    return "Opened vs code"

@tool
def open_yt():
    """Open YouTube in the Brave browser."""
    os.startfile(rf"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe")
    time.sleep(1)
    pyautogui.write("yt")
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)
    return "opened youtube"

@tool
def play_last_video():
    """Play the most recently watched YouTube video from history."""
    pyautogui.click(146,919)
    time.sleep(3)
    pyautogui.click(516,530)
    return "Playing last video from history"

@tool
def open_note(note):
    """Open Notepad and write the provided text into it."""
    os.system("notepad")
    time.sleep(1)
    pyautogui.write(note)
    time.sleep(3)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    return "noted.."

@tool
def get_all_files():
    """List all files inside the assistant's managed files directory."""
    list=os.listdir(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\ASSISTANT_FILES")
    print(list)
    return "listed.."

@tool
def create_file(name):
    """Create a new empty file with the given name inside the assistant files directory."""
    path=os.path.join(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\ASSISTANT_FILES",name)
    if os.path.exists(path):
        return f"file {name} already exits"
    with open(path,"w") as f:
        f.write('')
        f.close()
    return f"file {name} created..."

@tool
def del_file(name):
    """Delete the specified file from the assistant files directory."""
    path=os.path.join(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\ASSISTANT_FILES",name)
    if not os.path.exists(path):
        return "NO file available"
    else:
        os.remove(path=path,dir_fd=None)
        return f"deleted {name} succesfully"

@tool
def web_search(topic):
    """Search the web for a topic, retrieve the summary, and store it in memory."""
    url="https://search.brave.com/search?q="
    text=re.sub(" ","+",topic)
    url=url+text+"&summary=1"
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=False)
        context=browser.new_context()
        page=context.new_page()
        page.goto(url)
        time.sleep(7)
        div=page.locator("div.llm-output")
        p=div.locator("p")
        spans=p.locator("span")
        count=spans.count()
        text=""
        if count>0:
            for i in range(count):
                para=spans.nth(i).inner_text()
                text=text+para
        # result=clean_text(text)
        output_queue.put(text)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","r") as f:
            loaded=json.load(f)
        chunk={"id":len(loaded)+1,"source":"web","text":text}
        if not any(d["text"] == chunk["text"] for d in loaded):
            loaded.append(chunk)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","w") as f:
            json.dump(loaded,f,indent=4)
        return "ok sir let me search.."

@tool
def my_data():
    """Return the current system information including CPU usage, RAM usage, battery level, and current time."""
    cpu=p.cpu_percent(interval=0.1)
    print(f"CPU PERCENTAGE:{cpu}%")
    print(f"RAM USED:{p.virtual_memory().percent}%")
    print(f"BATTERY PERCENTAGE:{p.sensors_battery().percent}%")
    print(f"TIME:{time.localtime().tm_hour}:{time.localtime().tm_min}.{time.localtime().tm_sec}")
    return f"CPU PERCENTAGE:{cpu}%,RAM USED:{p.virtual_memory().percent}%,BATTERY PERCENTAGE:{p.sensors_battery().percent}%,TIME:{time.localtime().tm_hour}:{time.localtime().tm_min}.{time.localtime().tm_sec}"

@tool    
def reminder():
    """Continuously monitor reminders and notify the user when they are due."""
    while True:
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
            reminders=json.load(f)
        for reminder in reminders:
            if reminder["status"]=="pending":
                now=datetime.now()
                old = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
                if now>=old:
                    print(reminder["text"])
                    message=f"sorry to interrupt you sir but wanted to remind you to {reminder["text"]}"
                    output_queue.put(message)
                    toast=Notification(app_id="Assistant",title="Reminder",msg=reminder["text"],duration="short")
                    toast.show()
                    if reminder["repeat"]=="daily":
                        new =old+timedelta(days=1)
                        reminder["time"] = new.strftime("%Y-%m-%d %H:%M:%S")
                    elif reminder["repeat"]=="weekly":
                        new=old+timedelta(weeks=1)
                        reminder["time"] = new.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        reminder["status"]="done"
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","w") as f:
            json.dump(reminders,f,indent=4)
        time.sleep(10)

@tool
def schedule():
    """Continuously monitor the daily schedule and notify the user about upcoming activities."""
    while True:
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\schedule.json","r") as f:
            schedules=json.load(f)
        if schedules:
            for reminder in schedules:
                if reminder["status"]=="pending":
                    now=datetime.now()
                    old = datetime.strptime(reminder["timestamp"], "%Y-%m-%d %H:%M:%S")
                    if now>=old:
                        print(reminder["activity"])
                        message=f"sorry to interrupt you sir but wanted to remind you to {reminder["activity"]}"
                        output_queue.put(message)
                        toast=Notification(app_id="Assistant",title="Reminder",msg=reminder["activity"],duration="short")
                        toast.show()
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\schedule.json","w") as f:
            json.dump(schedules,f,indent=4)
        time.sleep(10)

@tool
def get_my_all_reminders():
    """Return all currently pending reminders."""
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
        reminders=json.load(f)
    result=""
    for reminder in reminders:
        if reminder["status"]=="pending":
            result+=f"Reminder to {reminder["text"]} at {reminder["time"]},"
    print(result)
    return result

@tool
def set_schedule():
    """Interactively collect the user's daily activities and generate an optimized schedule."""
    questions=[]
    output_queue.put("Do you have any assignments?")
    time.sleep(3)
    q1=manual_audio()
    questions.append(q1)
    output_queue.put("Do you have any Projects?")
    time.sleep(3)
    q2=manual_audio()
    questions.append(q2)
    output_queue.put("Do you have any learning to do?")
    time.sleep(3)
    q3=manual_audio()
    questions.append(q3)
    output_queue.put("Do you have any exercise to do?")
    time.sleep(3)
    q4=manual_audio()
    questions.append(q4)
    output_queue.put("what is your college time?")
    time.sleep(3)
    q5=manual_audio()
    questions.append(q5)
    output_queue.put("what is your class time?")
    time.sleep(3)
    q6=manual_audio()
    questions.append(q6)
    print(questions)
    payload = {
    "q1":q1,
    "q2":q2,
    "q3":q3,
    "q4":q4,
    "q5":q5,
    "q6":q6,
    }
    headers={"Content-Type": "application/json"}
    response=requests.post(url,json=payload,headers=headers)
    response=response.json()
    step1 = re.sub(r'\\n\s*', '', response)
    step2 = re.sub(r'\\"', '"', step1)
    final = re.sub(r',\s*]', ']', step2)
    response=json.loads(final)
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\schedule.json","w") as f:
        json.dump(response,f,indent=4)
    return "ok sir schedule set"
    

@tool
def cancel_all_reminders():
    """Delete all pending reminders."""
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
        reminders=json.load(f)
    reminders=[]
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","w") as f:
        json.dump(reminders,f,indent=4)
    return "ok sir deleted reminders"


def setup_at_start():
    """Perform the assistant's startup routine by opening predefined applications and webpages."""
    os.startfile(rf"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe")
    time.sleep(1)
    pyautogui.write("web")
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)
    output_queue.put("Done with the startup sir")

@tool
def start_gesture():
    """Enable gesture control for the assistant."""
    gesture_event.set()

@tool
def close_gesture():
    """Disable gesture control for the assistant."""
    gesture_event.clear()