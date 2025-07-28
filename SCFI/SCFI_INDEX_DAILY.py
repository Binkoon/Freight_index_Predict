from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os
from datetime import datetime

from base import Parents

class SCFI_INDEX_Crawling(Parents):
    def __init__(self): # 재사용 클래스 (base.py 같은거) 상속받을 거임. 없으면 그냥 pass로 두셈
        super().__init__

    def run(self):
        # 0. 홈페이지 접속할거임
        self.Visit_Link('https://www.ine.cn/eng/reports/statistical/daily/')