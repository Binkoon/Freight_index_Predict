from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os,time
from datetime import datetime

from base import Parents

class SCFI_INDEX_Crawling(Parents):
    def __init__(self): # 재사용 클래스 (base.py 같은거) 상속받을 거임. 없으면 그냥 pass로 두셈
        super().__init__()
        self.carrier_name = 'SCFI'

    def run(self):
        # 0. 홈페이지 접속할거임
        self.Visit_Link('https://www.ine.cn/eng/reports/statistical/daily/')
        driver = self.driver
        wait = self.wait
        time.sleep(1)

        # 1. 스크롤 Y로 쫙 내리자.
        driver.execute_script("window.scrollTo(0, 6500);")
        time.sleep(1)
        
        # 2. 엑셀 다운로드 클릭  //*[@id="export-table"]/div[1]/div[4]/div[3]
        excel_download_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH , '//*[@id="export-table"]/div[1]/div[4]/div[3]'
        )))
        excel_download_btn.click()
        time.sleep(1)

        save_path = self.get_save_path(ext="xlsx")
        print("저장할 경로:", save_path)

        self.Close()