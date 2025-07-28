from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import os
from datetime import datetime

class Parents:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080") # 해상도는 이거로 고정

        self.set_user_agent(chrome_options)  # 얘네 없으면 일부 선사는 차단함
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # ScheduleData 상위 폴더만 생성할거임 (SCFI 지수 DAY 단위로 가져올거라 그럼)
        self.base_download_dir = os.path.join(os.getcwd(), "scheduleData")
        if not os.path.exists(self.base_download_dir):
            os.makedirs(self.base_download_dir)

        # 오늘 날짜 폴더명 (YYMMDD)
        self.today_folder = datetime.now().strftime("%y%m%d")
        self.today_download_dir = os.path.join(self.base_download_dir, self.today_folder)
        if not os.path.exists(self.today_download_dir):
            os.makedirs(self.today_download_dir)

        prefs = {"download.default_directory": self.today_download_dir}
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    # 접속할거임
    def Visit_Link(self, url):
        self.driver.get(url)

    # 닫을거임
    def Close(self):
        self.driver.quit()
    

    # 대충 저장경로 이리이리하겠다.
    def get_save_path(self, carrier_name, vessel_name, ext="xlsx"):
        """
        저장 경로 생성 (예: scheduleData/250714/)
        """
        # 파일명에 들어가면 안 되는 문자 제거
        safe_vessel = vessel_name.replace("/", "_").replace("\\", "_")
        safe_carrier = carrier_name.replace("/", "_").replace("\\", "_")
        filename = f"{safe_carrier}_{safe_vessel}.{ext}"
        return os.path.join(self.today_download_dir, filename)