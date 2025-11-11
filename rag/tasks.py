import os,pyautogui,time


def play_music(name):
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(5)
    if name==".":
        pyautogui.press('space')
        time.sleep(2)
        pyautogui.hotkey('alt','tab')
        pyautogui.keyDown('alt')
    elif name:
        pyautogui.hotkey('ctrl','k')
        pyautogui.write(name)
        time.sleep(1)
        pyautogui.press('enter')
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.hotkey('alt','tab')
        pyautogui.keyDown('alt')
        pyautogui.keyUp('alt')
    else:
        pyautogui.press('space')
        time.sleep(2)
        pyautogui.hotkey('alt','tab')
        pyautogui.keyDown('alt')

def stop_music(c):
    os.startfile(rf"C:\Users\Admin\AppData\Roaming\Spotify\Spotify.exe")
    time.sleep(2)
    pyautogui.press('space')
    time.sleep(2)
    pyautogui.hotkey('alt','tab')
    pyautogui.keyDown('alt')
    pyautogui.keyUp('alt')

def open_vscode(c):
    os.system("start code")
    time.sleep(1)
    os.system("taskkill /f /im cmd.exe")

def open_yt(c):
    os.startfile(rf"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe")
    time.sleep(1)
    pyautogui.write("yt")
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)

def play_last_video(c):
    for _ in range(14):
        pyautogui.press("tab")
    pyautogui.press("enter")
    time.sleep(3)
    for _ in range(51):
        pyautogui.press("tab")
    pyautogui.press("enter")


    


