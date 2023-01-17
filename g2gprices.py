import requests
import schedule 
import sys
import time
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from discord_webhook import DiscordWebhook, DiscordEmbed
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# discord webhook
disc_url = 'https://discord.com/api/webhooks/927659893178130492/OYbIenE8hJoQiYuUzqBfYq_N_s2foDIWHwtd4Xthg_dBBqib4V0iwTpe1vNvwrDADDaP'
not_url = 'https://discord.com/api/webhooks/875373041301979176/e35tViKLXyECqrFZgnZevBSyah0NpnuffoCeJK8Jd47qUaR62zMVcBln8ZSPkH40XAhK'
result = {}

def send_disc_notification(user, price, platform):
    webhook = DiscordWebhook(url=disc_url, rate_limit_retry=True)
    embed = DiscordEmbed(title=user, color='03b2f8', description=platform)
    embed.set_timestamp()
    embed.add_embed_field(name='Price', value=price)

    webhook.add_embed(embed)
    webhook.execute()

def updateValuesG2G():
    # Start a chromedrive and load lxml
    url='https://www.g2g.com/categories/wow-classic-tbc-gold-for-sale?region_id=ac3f85c1-7562-437e-b125-e89576b9a38e&fa=lgc_29076_server%3Algc_29076_server_40972,lgc_29076_server_41021,lgc_29076_server_41023&sort=lowest_price'
    options = FirefoxOptions()
    options.add_argument("--headless") 
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    timeout = 30
    try:
        element_present = EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[5]/div/div[2]/div[2]/div[1]/div'))
        WebDriverWait(driver, timeout).until(element_present)
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source,'lxml')
        driver.quit()
        rows = soup.find_all('div', {"class": "row q-col-gutter-md-md q-px-md-md"})
        servers = rows[0].find_all('div', {"class": "text-body1 ellipsis-2-lines"})
        prices = rows[0].find_all('div', {"class": "row items-baseline q-gutter-xs text-body1"})
        for i in range(len(servers)):
            result[servers[i].text.strip()] = prices[i].contents[1].text.strip()
            send_disc_notification(servers[i].text.strip(), prices[i].contents[1].text.strip(), "G2G")
    except TimeoutException:
        print("Timed out waiting for page to load")

def updateValuesMMO():
    # Start a chromedrive and load lxml
    url='https://www.mmobuyer.com/'
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    timeout = 30
    try:
        element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[2]/div[2]/div[1]/div[4]/table/tbody'))
        WebDriverWait(driver, timeout).until(element_present)
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source,'lxml')
        driver.quit()
        table = soup.find("table", attrs={"class": "table table-striped order-table"})
        table_data = table.tbody.find_all("tr")
        i = 0
        while i<len(table_data):
            line = table_data[i].find_all("td")
            if "TBC Classic EU" in line[1].text[:14]:
                if "Gehennas TBC [EU] - Alliance" in line[1].text[14:]:
                    price = float(line[2].text[1:8])
                    string = "Need " + line[3].text + " @ " + str(price)
                    send_disc_notification(line[1].text[14:], string, "MMOBuyer")

                if "Gehennas TBC [EU] - Horde" in line[1].text[14:]:
                    price = float(line[2].text[1:8])
                    string = "Need " + line[3].text + " @ " + str(price)
                    send_disc_notification(line[1].text[14:], string, "MMOBuyer")
            
                if "Auberdine TBC [FR] - Alliance" in line[1].text[14:]:
                    price = float(line[2].text[1:8])
                    string = "Need " + line[3].text + " @ " + str(price)
                    send_disc_notification(line[1].text[14:], string, "MMOBuyer")
            
            if "EU WoW Classic: Season of Mastery" in line[1].text[:33]:
                if "Dreadnaught - Alliance" in line[1].text[33:]:
                    price = float(line[2].text[1:8])
                    string = "Need " + line[3].text + " @ " + str(price)
                    send_disc_notification("SoM " + line[1].text[33:], string, "MMOBuyer")

                if "Kingsfall - Alliance" in line[1].text[33:]:
                    price = float(line[2].text[1:8])
                    string = "Need " + line[3].text + " @ " + str(price)
                    send_disc_notification("SoM " + line[1].text[33:], string, "MMOBuyer")

            i+=1
    except TimeoutException:
        print("Timed out waiting for page to load")

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def jobs():
    schedule.every(290).seconds.do(run_threaded, updateValuesG2G)
    schedule.every(310).seconds.do(run_threaded, updateValuesMMO)

if __name__ == '__main__':
    jobs()
    while True:
        schedule.run_pending()
        time.sleep(1)