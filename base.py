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
    
    def set_user_agent(self, chrome_options, user_agent=None):
        """
        크롬 옵션에 user-agent를 추가하는 메서드.
        user_agent를 지정하지 않으면 기본 최신 크롬 UA 사용.
        """
        if user_agent is None:
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        chrome_options.add_argument(f"--user-agent={user_agent}")

    # 접속할거임
    def Visit_Link(self, url):
        self.driver.get(url)

    # 닫을거임
    def Close(self):
        self.driver.quit()
    

    # 대충 저장경로 이리이리하겠다.
    def get_save_path(self, ext="xlsx"):
        today_str = datetime.now().strftime("%y%m%d")
        filename = f"SCFI_{today_str}.{ext}"
        return os.path.join(self.base_download_dir, filename)