import requests, schedule, time, os
from ast import If
from turtle import end_fill
from bs4 import BeautifulSoup
from plyer import notification
from py_imessage import imessage
import chime

URL = "http://www.simar-louresodivelas.pt/"
chime.theme('big-sur')

def check_web():
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="home")
    text = results.text.strip()
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = ' '.join(text.split())
    if not (text == "sem roturas"):
        # notification.notify(
        #     title = 'Rotura de água',
        #     message = results.text.strip(),
        #     app_icon = None,
        #     timeout = 1000000000,
        # )
        if("bucelas" in text or "freixial" in text):
            for x in range(20):
                chime.error()
                time.sleep(1)
            # os.system("osascript sendMessage.scpt 914241461 'Há uma rotura de água perto de casa!!!' ")

# check_web()

schedule.every(10).minutes.do(check_web)

while True:
    schedule.run_pending()
    time.sleep(1)