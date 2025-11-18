import os,pyautogui,time,re,json
from playwright.sync_api import sync_playwright
from rag.globals import output_queue
from backend.repository.text_extraction import clean_text
import psutil as p
from datetime import datetime,timedelta
from winotify import Notification

def play_music(name):
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(3)
    if name==" .":
        pyautogui.press('space')
        time.sleep(2)
        pyautogui.hotkey('alt','tab')
        pyautogui.keyDown('alt')
        pyautogui.keyUp('alt')
        
    elif name:
        pyautogui.click(788,38)
        pyautogui.write(name)
        time.sleep(3)
        pyautogui.click(665,291)
    else:
        pyautogui.press('space')
        time.sleep(2)
        pyautogui.hotkey('alt','tab')
        pyautogui.keyDown('alt')
        pyautogui.keyUp('alt')
    return "playing music..."

def stop_music(c):
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(2)
    pyautogui.press('space')
    time.sleep(2)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    return "stopping music..."

def open_vscode(c):
    os.system("start code")
    time.sleep(1)
    os.system("taskkill /f /im cmd.exe")
    return "Opened vs code"

def open_yt(c):
    os.startfile(rf"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe")
    time.sleep(1)
    pyautogui.write("yt")
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)
    return "opened youtube"

def play_last_video(c):
    pyautogui.click(119,497)
    time.sleep(3)
    pyautogui.click(516,530)
    return "Playing last video from history"

def open_note(note):
    os.system("notepad")
    time.sleep(1)
    pyautogui.write(note)
    time.sleep(3)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')
    return "noted.."

def get_all_files(c):
    list=os.listdir(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\ASSISTANT_FILES")
    print(list)
    return "listed.."

def create_file(name):
    path=os.path.join(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\ASSISTANT_FILES",name)
    if os.path.exists(path):
        return f"file {name} already exits"
    with open(path,"w") as f:
        f.write('')
        f.close()
    return f"file {name} created..."

def del_file(name):
    path=os.path.join(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\ASSISTANT_FILES",name)
    if not os.path.exists(path):
        return "NO file available"
    else:
        os.remove(path=path,dir_fd=None)
        return f"deleted {name} succesfully"
    
def web_search(topic):
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
        print(text)
        output_queue.put(text)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","r") as f:
            loaded=json.load(f)
        chunk={"id":len(loaded)+1,"source":"web","text":text}
        if not any(d["text"] == chunk["text"] for d in loaded):
            loaded.append(chunk)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","w") as f:
            json.dump(loaded,f,indent=4)
        return "task done.."

def my_data(c):
    cpu=p.cpu_percent(interval=0.1)
    print(f"CPU PERCENTAGE:{cpu}%")
    print(f"RAM USED:{p.virtual_memory().percent}%")
    print(f"BATTERY PERCENTAGE:{p.sensors_battery().percent}%")
    print(f"TIME:{time.localtime().tm_hour}:{time.localtime().tm_min}.{time.localtime().tm_sec}")
    return f"CPU PERCENTAGE:{cpu}%,RAM USED:{p.virtual_memory().percent}%,BATTERY PERCENTAGE:{p.sensors_battery().percent}%,TIME:{time.localtime().tm_hour}:{time.localtime().tm_min}.{time.localtime().tm_sec}"
    
def reminder():
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

def get_my_all_reminders(c):
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
        reminders=json.load(f)
    result=""
    for reminder in reminders:
        if reminder["status"]=="pending":
            result+=f"Reminder to {reminder["text"]} at {reminder["time"]},"
    print(result)
    return result

def cancel_all_reminders(c):
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
        reminders=json.load(f)
    reminders=[]
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","w") as f:
        json.dump(reminders,f,indent=4)
    return "ok sir deleted reminders"