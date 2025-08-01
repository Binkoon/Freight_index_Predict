######### 공유받은 파일 ##############
# 분석 예정 #### 코랩 -> vscode 이관 위함.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from time import sleep
from bs4 import BeautifulSoup
import requests
import re
import os

# Dataframe
import pandas as pd

def is_garbage_row(cells):
    joined = ''.join(cells)
    if not joined or all(cell.strip() in ('', 'None') for cell in cells):
        return True
    garbage_keywords = ['Leaflet', 'Humidity', 'Wind', 'Sign Up']
    return any(keyword in joined for keyword in garbage_keywords)

def extract_table_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    wrapper = soup.select_one('div.table__wrapper')
    table = wrapper.find('table') if wrapper else None
    if not table:
        return None

    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    data = []

    for row in table.find_all('tr')[1:]:
        cells = []
        for td in row.find_all('td'):
            for tag in td.find_all(['span', 'i', 'img', 'script']):
                tag.decompose()
            cells.append(td.get_text(strip=True))
        if cells and not is_garbage_row(cells):
            data.append(cells)

    return pd.DataFrame(data, columns=headers)

from tqdm.notebook import tqdm

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Open Google and print the title of the page
driver.get("https://www.oceanlook.net/port")

all_data = pd.DataFrame()
max_page = 122
for _ in tqdm(range(max_page), desc="페이지 수집 진행"):
    time.sleep(3)  # 페이지 로딩 대기
    html = driver.page_source
    df = extract_table_from_html(html)
    if df is not None:
        all_data = pd.concat([all_data, df], ignore_index=True)

    try:
        next_button = driver.find_element(By.XPATH, '//div[contains(@class,"pagination")]//button[contains(text(),">")]')
        next_button.click()
    except:
        print("더 이상 다음 페이지 없음.")
        break

driver.quit()

# prompt: all_data 의 Waiting in port	Berthing in port	Heading to port 열들의 값은 숫자 형식이어야 해.

# 'Waiting in port', 'Berthing in port', 'Heading to port' 열을 숫자로 변환
# 에러 발생 시 해당 셀의 값을 NaN으로 처리 (errors='coerce' 옵션 사용)
all_data['Waiting in port'] = pd.to_numeric(all_data['Waiting in port'], errors='coerce')
all_data['Berthing in port'] = pd.to_numeric(all_data['Berthing in port'], errors='coerce')
all_data['Heading to port'] = pd.to_numeric(all_data['Heading to port'], errors='coerce')

from datetime import datetime

# 수집일자 설정
collection_date = datetime.today().strftime('%Y-%m-%d')

# 수집일자 컬럼 추가 (맨 앞에 삽입)
all_data.insert(0, '수집일자', collection_date)

# 엑셀로 저장
all_data.to_excel("port_data.xlsx", index=False)

import pandas as pd

# 예시 데이터를 생성 (실제 코랩에서는 사용자가 all_data를 이미 보유하고 있어야 함)
# 아래는 포트 코드 매핑 정보
port_mapping = {
    "LONG BEACH": "LGB",
    "LOS ANGELES": "LA",
    "MANZANILLO": "ZLO",
    "BUSAN": "PUS",
    "CHENNAI": "MAA",
    "CHATTOGRAM": "CGP",
    "COLOMBO": "CMB",
    "HO CHI MINH CITY": "SGN",
    "LAEM CHABANG": "LCH",
    "MANILA": "MNL",
    "MUNDRA": "MUN",
    "NINGBO": "NBO",
    "PORT KLANG": "PKG",
    "QINGDAO": "TAO",
    "SHANGHAI PT": "SHA",
    "SHEKOU PT": "SHK",
    "SINGAPORE": "SIN",
    "XIAMEN": "XMN",
    "SURABAYA": "SUB",
    "TOKYO": "TYO",
    "YANTIAN PT": "YTN"
}

# 포트 리스트 대문자로
target_ports_upper = list(port_mapping.keys())

# all_data가 존재한다고 가정하고 해당 포트만 필터링
filtered = all_data[all_data['PORT'].str.upper().isin(target_ports_upper)].copy()

# Yantian 처리: YANTIAN PT → YANTIAN 으로 이름 매칭
filtered['PORT_UPPER'] = filtered['PORT'].str.upper()
filtered.loc[filtered['PORT_UPPER'] == 'YANTIAN PT', 'PORT_UPPER'] = 'YANTIAN PT'
filtered.loc[filtered['PORT_UPPER'] == 'SHEKOU PT', 'PORT_UPPER'] = 'SHEKOU PT'
filtered.loc[filtered['PORT_UPPER'] == 'SHANGHAI PT', 'PORT_UPPER'] = 'SHANGHAI PT'

# 매핑을 기준으로 PORT CODE 추가
filtered['PORT CODE (FROM MAPPING)'] = filtered['PORT_UPPER'].map(port_mapping)

# 원래 순서를 보장하기 위해 순서 정보 DataFrame 생성
ordered_ports = pd.DataFrame({
    'PORT_UPPER': list(port_mapping.keys()),
    'ORDER': range(len(port_mapping))
})

# 정렬을 위한 병합
final = pd.merge(filtered, ordered_ports, on='PORT_UPPER', how='left').sort_values('ORDER')


# PAMIT와 DOMAN 코드 제외
final_filtered = final[~final['PORT CODE'].isin(['PAMIT', 'DOMAN'])]
final_filtered