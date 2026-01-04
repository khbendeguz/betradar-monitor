import os
import time
import ftplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_id():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://vfscigaming.aitcloud.de/vflmshop/retail/index?clientid=4997&lang=zh&style=scigamingcdn&screen=betradar_vflm_one_screen&channel=6"
    
    try:
        driver.get(url)
        time.sleep(15) # Várunk a shared.js-re
        # A nyerő parancsod:
        season_id = driver.execute_script("return app.timeline.currentChunkModel.chunk.competition.id;")
        return str(season_id)
    finally:
        driver.quit()

def upload_to_ftp(content):
    # Az adatokat a GitHub titkosított tárolójából (Secrets) vesszük
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASS = os.getenv("FTP_PASS")
    TARGET_DIRECTORY = "uj"
    with open("season.txt", "w") as f:
        f.write(content)
    
    session = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
    if TARGET_DIRECTORY:
        session.cwd(TARGET_DIRECTORY)
    with open("season.txt", "rb") as f:
        session.storbinary("STOR season.txt", f)
    session.quit()
    print("Siker! ID feltöltve.")

if __name__ == "__main__":
    sid = get_id()
    if sid and sid != "None":
        upload_to_ftp(sid)
    else:
        print("Nem sikerült kinyerni az ID-t.")
