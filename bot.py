import os
import time
import ftplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_data():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Fontos a kamu User-Agent, hogy ne blokkoljon a Betradar
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # A videó linkje (csatorna 6)
        driver.get("https://vfscigaming.aitcloud.de/vflmshop/retail/index?clientid=4997&lang=zh&style=scigamingcdn&screen=betradar_vflm_one_screen&channel=6")
        
        # Többet várunk, mert a Betradar app lassan indul el a virtuális gépen
        time.sleep(25) 
        
        # A te parancsod lefuttatása
        script = "return app.timeline.currentChunkModel.chunk.competition.id;"
        season_id = driver.execute_script(script)
        
        return str(season_id)
    except Exception as e:
        print(f"Hiba a kinyerésnél: {e}")
        return None
    finally:
        driver.quit()

def upload_ftp(sid):
    try:
        host = os.getenv("FTP_HOST")
        user = os.getenv("FTP_USER")
        pw = os.getenv("FTP_PASS")
        
        # Létrehozzuk helyben a season.txt-t
        with open("season.txt", "w") as f:
            f.write(sid)
            
        session = ftplib.FTP(host, user, pw)
        
        # IDE ÍRD A MAPPA NEVÉT, ha nem a főkönyvtárba megy
        # session.cwd("public_html/valami") 
        
        with open("season.txt", "rb") as f:
            session.storbinary("STOR season.txt", f)
        session.quit()
        print(f"Siker! Season ID {sid} feltöltve.")
    except Exception as e:
        print(f"FTP Hiba: {e}")

if __name__ == "__main__":
    sid = get_data()
    if sid and sid != "None" and sid != "undefined":
        upload_ftp(sid)
    else:
        print("Nem sikerült kinyerni az ID-t (lehet még tölt az oldal).")
