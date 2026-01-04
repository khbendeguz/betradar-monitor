import os
import time
import ftplib
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def upload_to_ftp(data_dict):
    try:
        FTP_HOST = os.getenv("FTP_HOST")
        FTP_USER = os.getenv("FTP_USER")
        FTP_PASS = os.getenv("FTP_PASS")
        
        # A fájl neve az FTP-n
        filename = "season_info.json"
        with open(filename, "w") as f:
            json.dump(data_dict, f)
        
        session = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        # Ha alkönyvtárba tennéd: session.cwd("monitor_mappa")
        with open(filename, "rb") as f:
            session.storbinary(f"STOR {filename}", f)
        session.quit()
        return True
    except Exception as e:
        print(f"FTP Hiba: {e}")
        return False

if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://vfscigaming.aitcloud.de/vflmshop/retail/index?clientid=4997&lang=zh&style=scigamingcdn&screen=betradar_vflm_one_screen&channel=6"
    
    try:
        driver.get(url)
        time.sleep(15) # Vár az oldal betöltésére
        
        # 30 PERCES CIKLUS: Percenként frissít
        for i in range(30):
            try:
                # Lekérjük az adatokat a te nyerő parancsoddal
                data = driver.execute_script("""
                    try {
                        return {
                            "seasonId": app.timeline.currentChunkModel.chunk.competition.id,
                            "round": app.timeline.currentChunkModel.chunk.nr,
                            "timestamp": Math.floor(Date.now() / 1000)
                        };
                    } catch(e) { return null; }
                """)

                if data:
                    upload_to_ftp(data)
                    print(f"Frissítve ({i+1}/30): Season {data['seasonId']}, Round {data['round']}")
                else:
                    print("Hiba: Az app objektum nem elérhető.")
            except Exception as e:
                print(f"Hiba a ciklusban: {e}")
            
            time.sleep(60) # Vár 1 percet a következő frissítésig
            
    finally:
        driver.quit()
