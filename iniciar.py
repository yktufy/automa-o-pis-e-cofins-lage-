import subprocess
import time
import pyautogui


subprocess.Popen([r"C:\Contabil\contabil.exe", "/escrita"])


time.sleep(25)  


pyautogui.write("Brasil#1", interval=0.05)


pyautogui.press("enter")