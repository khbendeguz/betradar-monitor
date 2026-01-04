import os
import time
import ftplib
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_live_data():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://vfscigaming.aitcloud.de/vflmshop/retail/index?clientid=4997&lang=zh&style=scigamingcdn&screen=betradar_vflm_one_screen&channel=6"
    
    try:
        driver.get(url)
        time.sleep(15) # Megvárjuk, amíg az app felépül
        
        # Ez a parancs egyszerre kéri le a Szezon ID-t és az aktuális fordulót (chunk nr)
        nyero_parancs = """
        return [
            app.timeline.currentChunkModel.chunk.competition.id,
            app.timeline.currentChunkModel.chunk.nr
        ];
        """
        data = driver.execute_script(nyero_parancs)
        return {"seasonId": str(data[0]), "round": str(data[1])}
    except Exception as e:
        print(f"Hiba a kiolvasásnál: {e}")
        return None
    finally:
        driver.quit()

def upload_to_ftp(data_dict):
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASS = os.getenv("FTP_PASS")
    
    # IDE ÍRD A MAPPA NEVÉT, ha szükséges (pl: "public_html/adatok")
    TARGET_DIRECTORY = "" 

    # JSON-be csomagoljuk az adatokat, hogy a HTML könnyen olvassa
    with open("season_info.json", "w") as f:
        json.dump(data_dict, f)
    
    try:
        session = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        if TARGET_DIRECTORY:
            session.cwd(TARGET_DIRECTORY)
            
        with open("season_info.json", "rb") as f:
            session.storbinary("STOR season_info.json", f)
        session.quit()
        print(f"Siker! Adatok feltöltve: {data_dict}")
    except Exception as e:
        print(f"FTP hiba: {e}")

if __name__ == "__main__":
    live_data = get_live_data()
    if live_data and live_data['seasonId'] != "None":
        upload_to_ftp(live_data)
    else:
        print("Nem sikerült adatot kinyerni.")
