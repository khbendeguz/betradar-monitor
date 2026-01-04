def ftp_upload(content):
    # Beállítások a Secrets-ből
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASS = os.getenv("FTP_PASS")
    
    # IDE ÍRD A MAPPA NEVÉT (pl: "public_html/adatok" vagy "monitor")
    # Ha a főkönyvtárba akarod, hagyd üresen: ""
    TARGET_DIRECTORY = "uj" 

    with open("season.txt", "w") as f: 
        f.write(str(content))
    
    session = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
    
    # Belépés a megadott mappába
    if TARGET_DIRECTORY:
        session.cwd(TARGET_DIRECTORY)
        
    with open("season.txt", "rb") as f: 
        session.storbinary("STOR season.txt", f)
    
    session.quit()
    print(f"Siker! ID feltöltve a(z) {TARGET_DIRECTORY} mappába.")
