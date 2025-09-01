# https://www.msc.com/ko/search-a-schedule  접속해야하는 선사임.
# 그 후 클릭해야하는 탭 : //*[@id="main"]/div[1]/div[2]/div/div[2]/div/div/div/button[3]/span
# 그 후 클릭 활성화해서 입력이 가능한 상태가 되게 해야함. //*[@id="countryport"]

# port 리스트트
# Tianjin, 
# Busan, 
# Qingdao, 
# Shanghai, 
# Ningbo , 
# Xiamen, 
# shekou, 
# Singapore, 
# Jebel Ali , 
# abu dhabi, 
# qahmd, 
# sadmm,
#  Umm Qasr, 
# abu dhabi, 
# Tianjin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
from datetime import datetime

def msc_schedule_crawling():
    """MSC 스케줄 데이터 수집 (전체 포트)"""
    
    # 전체 포트 리스트
    ports = [
        "Tianjin", "Busan",
         "Qingdao", "Shanghai", "Ningbo", 
        "Xiamen", "Shekou", "Singapore", "Jebel Ali", 
        "Abu Dhabi", "Hamad", "SADMM", "Umm Qasr"
    ]
    
    # Chrome 옵션 설정 (봇 감지 방지)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 다운로드 경로 설정
    base_download_path = os.path.join(os.getcwd(), "MSC_DATA")
    if not os.path.exists(base_download_path):
        os.makedirs(base_download_path)
    
    # 오늘 날짜로 하위 폴더 생성
    today = datetime.now().strftime("%y%m%d")
    download_path = os.path.join(base_download_path, today)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"날짜 폴더 생성 완료: {download_path}")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # JavaScript 실행으로 webdriver 속성 제거
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("MSC 사이트 접속 중...")
        driver.get("https://www.msc.com/ko/search-a-schedule")
        time.sleep(5)  # 원래 대기 시간으로 복원
        
        wait = WebDriverWait(driver, 15)  # 원래 대기 시간으로 복원
        
        ## 0. 쿠키 팝업 처리 (MSC 사이트 전용)
        try:
            print("쿠키 팝업 처리 중...")
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='onetrust-accept-btn-handler']")))
            cookie_button.click()
            print("쿠키 팝업 처리 완료")
            time.sleep(2)
        except Exception as e:
            print(f"쿠키 팝업 처리 실패: {e}")
            print("쿠키 팝업이 없거나 이미 처리됨")
        
        ## 1. 스케줄 탭 클릭
        try:
            print("스케줄 탭 찾는 중...")
            schedule_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main']/div[1]/div[2]/div/div[2]/div/div/div/button[3]/span")))
            schedule_tab.click()
            print("스케줄 탭 클릭 완료")
            time.sleep(3)  # 원래 대기 시간으로 복원
        except Exception as e:
            print(f"스케줄 탭 클릭 실패: {e}")
            return
        
        ## 2. 포트별 스케줄 데이터 수집
        for port_name in ports:
            try:
                print(f"\n{'='*50}")
                print(f"포트 {port_name} 처리 시작")
                print(f"{'='*50}")
                
                                 # 포트 입력 필드 활성화 및 입력
                print("포트 입력 필드 찾는 중...")
                
                # 페이지를 맨 위로 스크롤하여 포트 입력 필드가 보이도록 함
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                
                port_input = wait.until(EC.element_to_be_clickable((By.ID, "countryport")))
                port_input.click()
                print("포트 입력 필드 활성화 완료")
                time.sleep(2)
                
                # 포트명 입력
                port_input.clear()
                port_input.send_keys(port_name)
                print(f"{port_name} 포트 입력 완료")
                time.sleep(3)
                
                # 자동완성 리스트에서 첫 번째 항목 선택
                try:
                    print("자동완성 리스트 확인 중...")
                    autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main']/div[1]/div[2]/div/div[2]/div/div/form[3]/div/div/ul/li/button")))
                    autocomplete_item.click()
                    print(f"{port_name} 자동완성 선택 완료")
                    time.sleep(2)
                except:
                    print("자동완성 리스트가 없거나 선택 실패, 계속 진행")
                
                # 스케줄 데이터 수집 및 저장
                print("스케줄 데이터 수집 시작...")
                time.sleep(8)  # 스케줄 로딩 대기
                
                # 도착(ARRIVAL) 데이터 수집
                print(f"=== {port_name} 도착(ARRIVAL) 데이터 수집 시작 ===")
                collect_schedule_data("ARRIVAL", wait, download_path, port_name)
                
                # 출항(DEPARTURE) 데이터 수집
                print(f"=== {port_name} 출항(DEPARTURE) 데이터 수집 시작 ===")
                collect_schedule_data("DEPARTURE", wait, download_path, port_name)
                
                print(f"포트 {port_name} 처리 완료!")
                time.sleep(3)  # 다음 포트 처리 전 대기
                
            except Exception as e:
                print(f"포트 {port_name} 처리 실패: {e}")
                print("다음 포트로 진행합니다.")
                continue
        
        print("MSC 스케줄 전체 포트 수집 완료!")
        
    except Exception as e:
        print(f"MSC 스케줄 크롤링 중 오류 발생: {e}")
    finally:
        # 브라우저는 열어둔 상태로 유지 (데이터 확인용)
        print("브라우저를 열어둔 상태로 유지합니다. 확인 후 수동으로 닫아주세요.")
        # driver.quit()

def collect_schedule_data(schedule_type, wait, download_path, port_name):
    """스케줄 데이터 수집 함수 (도착/출항)"""
    
    try:
        # 도착/출항 선택 버튼 클릭
        print(f"{schedule_type} 선택 버튼 클릭 중...")
        select_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main']/div[1]/div[3]/div/div[1]/div/div/div/div/div[1]/div/div/div[2]/div[1]/div/div/div/button")))
        select_button.click()
        time.sleep(3)
        
        # 도착/출항 옵션 선택
        if schedule_type == "ARRIVAL":
            option_xpath = "//*[@id='main']/div[1]/div[3]/div/div[1]/div/div/div/div/div[1]/div/div/div[2]/div[1]/div/div/div/div/ul/li[1]"
        else:  # DEPARTURE
            option_xpath = "//*[@id='main']/div[1]/div[3]/div/div[1]/div/div/div/div/div[1]/div/div/div[2]/div[1]/div/div/div/div/ul/li[2]"
        
        option_element = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        option_element.click()
        print(f"{schedule_type} 옵션 선택 완료")
        time.sleep(5)  # 스케줄 로딩 대기
        
        # 헤더 데이터 수집 (MSC 사이트의 CSS Grid 구조에 맞춤)
        print("테이블 헤더 수집 중...")
        thead = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main']/div[1]/div[3]/div/div[1]/div/div/div/div/div[2]")))
        
        # MSC 사이트의 CSS Grid 구조에 맞춰 헤더 수집
        # msc-search-schedule__result-heading 클래스 내의 cell 클래스를 가진 div들을 찾기
        header_elements = thead.find_elements(By.XPATH, ".//div[contains(@class, 'cell')]")
        
        if not header_elements:
            # cell 클래스가 없는 경우 다른 방법으로 시도
            header_elements = thead.find_elements(By.XPATH, ".//div[contains(@class, 'small-')]")
        
        headers = []
        for header in header_elements:
            text = header.text.strip()
            if text:
                headers.append(text)
        
        if not headers:
            # 헤더를 찾을 수 없는 경우 기본 헤더 사용
            headers = ["Port", "Vessel", "Voyage", "ETA/ETD", "Status"]
            print("기본 헤더 사용")
        else:
            print(f"수집된 헤더: {headers}")
        
        print(f"헤더 수집 완료: {len(headers)}개 컬럼")
        
        # 행 데이터 수집 (MSC 사이트의 CSS Grid 구조에 맞춤)
        print("행 데이터 수집 중...")
        table_data = []
        row_index = 3  # div[3]부터 시작
        
        while True:
            try:
                # 행 요소 찾기
                row_xpath = f"//*[@id='main']/div[1]/div[3]/div/div[1]/div/div/div/div/div[{row_index}]"
                row_element = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
                
                # MSC 사이트의 CSS Grid 구조에 맞춰 셀 수집
                # 각 행 내의 cell 클래스를 가진 div들을 찾기
                cells = row_element.find_elements(By.XPATH, ".//div[contains(@class, 'cell')]")
                
                if not cells:
                    # cell 클래스가 없는 경우 다른 방법으로 시도
                    cells = row_element.find_elements(By.XPATH, ".//div[contains(@class, 'small-')]")
                
                if not cells:
                    # 여전히 셀을 찾을 수 없는 경우 행 전체 텍스트 사용
                    row_text = row_element.text.strip()
                    if row_text:
                        # 텍스트를 공백이나 줄바꿈으로 분리하여 셀 데이터로 만들기
                        row_data = [text.strip() for text in row_text.split('\n') if text.strip()]
                        # 헤더 개수에 맞춰 조정
                        while len(row_data) < len(headers):
                            row_data.append("")
                        if len(row_data) > len(headers):
                            row_data = row_data[:len(headers)]
                    else:
                        row_data = [""] * len(headers)
                else:
                    row_data = []
                    for cell in cells:
                        cell_text = cell.text.strip()
                        if cell_text:  # 빈 셀이 아닌 경우만 추가
                            row_data.append(cell_text)
                        else:
                            row_data.append("")
                    
                    # 헤더 개수에 맞춰 데이터 조정
                    while len(row_data) < len(headers):
                        row_data.append("")
                    if len(row_data) > len(headers):
                        row_data = row_data[:len(headers)]
                
                if any(cell.strip() for cell in row_data):  # 빈 행이 아닌 경우만 추가
                    table_data.append(row_data)
                    print(f"행 {row_index-2} 수집 완료: {len(row_data)}개 셀")
                    # 디버깅을 위해 첫 번째 행의 내용 출력
                    if row_index == 3:
                        print(f"첫 번째 행 데이터 샘플: {row_data}")
                else:
                    print(f"행 {row_index-2}는 빈 데이터로 건너뜀")
                
                row_index += 1
                
            except Exception as e:
                # 더 이상 행이 없으면 종료
                print(f"행 {row_index-2}에서 데이터 수집 종료: {e}")
                break
        
        print(f"데이터 수집 완료: {len(table_data)}개 행")
        
        # 엑셀 파일로 저장
        if table_data:
            save_to_excel(table_data, headers, download_path, port_name, schedule_type)
        else:
            print(f"{schedule_type} 데이터가 없습니다.")
            
    except Exception as e:
        print(f"{schedule_type} 데이터 수집 실패: {e}")

def save_to_excel(table_data, headers, download_path, port_name, schedule_type):
    """엑셀 파일로 저장하는 함수 (데이터 전처리 포함)"""
    
    try:
        import pandas as pd
        import re
        from datetime import datetime
        
        # 데이터프레임 생성
        df = pd.DataFrame(table_data, columns=headers)
        
        print(f"전처리 전 데이터: {df.shape[0]}행 x {df.shape[1]}열")
        print(f"전처리 전 컬럼: {list(df.columns)}")
        
        # 데이터 전처리: A, C, E 컬럼만 선택 (0, 2, 4 인덱스)
        if df.shape[1] >= 5:  # 최소 5개 컬럼이 있는 경우
            # A, C, E 컬럼 선택 (0, 2, 4 인덱스)
            selected_columns = [0, 2, 4]
            df_processed = df.iloc[:, selected_columns].copy()
            
            # ARRIVAL과 DEPARTURE에 따른 헤더명 설정
            if schedule_type == "ARRIVAL":
                new_headers = ["Port", "Vessel/Voyage", "ETA"]
            else:  # DEPARTURE
                new_headers = ["Port", "Vessel/Voyage", "ETD"]
            
            # 헤더명 변경
            df_processed.columns = new_headers
            
            # 날짜 형식 변환 처리 (요일 제거)
            print("날짜 형식 변환 처리 중...")
            date_column_index = 2  # ETA/ETD 컬럼 (3개 컬럼 중 마지막)
            
            for idx, row in df_processed.iterrows():
                date_cell = str(row.iloc[date_column_index])
                
                # MSC 날짜 형식 패턴 매칭 (예: "Tue 26th Aug 2025 12:18")
                date_pattern = r'(\w{3})\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\w{3})\s+(\d{4})\s+(\d{1,2}):(\d{2})'
                match = re.search(date_pattern, date_cell)
                
                if match:
                    day_name, day, month, year, hour, minute = match.groups()
                    
                    # 월 이름을 숫자로 변환
                    month_map = {
                        'Jan': '1', 'Feb': '2', 'Mar': '3', 'Apr': '4',
                        'May': '5', 'Jun': '6', 'Jul': '7', 'Aug': '8',
                        'Sep': '9', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    
                    month_num = month_map.get(month, month)
                    
                    # 한국식 날짜 형식으로 변환: Y/M/D HH:MM (요일 제거)
                    new_date_format = f"{year}/{month_num}/{day} {hour}:{minute}"
                    df_processed.iloc[idx, date_column_index] = new_date_format
                    
                    print(f"날짜 변환: {date_cell} → {new_date_format}")
            
            print(f"전처리 후 데이터: {df_processed.shape[0]}행 x {df_processed.shape[1]}열")
            print(f"전처리 후 컬럼: {list(df_processed.columns)}")
            
            # 전처리된 데이터로 저장
            df_to_save = df_processed
        else:
            print("컬럼이 5개 미만이므로 전처리 없이 저장")
            df_to_save = df
        
        # 파일명 생성 (Port명_ARRIVAL 또는 Port명_DEPARTURE)
        filename = f"{port_name}_{schedule_type}.xlsx"
        filepath = os.path.join(download_path, filename)
        
        # 엑셀 파일로 저장
        df_to_save.to_excel(filepath, index=False)
        print(f"엑셀 파일 저장 완료: {filepath}")
        
    except Exception as e:
        print(f"엑셀 파일 저장 실패: {e}")
        return

if __name__ == '__main__':
    msc_schedule_crawling()