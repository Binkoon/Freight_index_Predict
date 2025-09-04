# https://www.msc.com/ko/search-a-schedule  접속해야하는 선사임.
# //*[@id="from"]  (출발지쪽)  (ningbo로 검색)
# //*[@id="to"]  (도착지쪽) (jebel ali로 검색)
# //*[@id="main"]/div[1]/div[2]/div/div[2]/div/div/form[1]/div[2]/div[2]/div/button  검색 버튼 클릭릭

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os
import time
from datetime import datetime
import pandas as pd
import re

def click_toggle_buttons(driver, wait):
    """
    토글 버튼들을 찾아서 클릭하는 함수
    """
    all_schedule_data = []  # 모든 스케줄 데이터를 저장할 리스트
    
    # div[1]부터 div[20]까지 확인 (충분한 범위)
    for i in range(1, 21):
        try:
            print(f"토글 버튼 {i} 확인 중...")
            # 토글 버튼 XPath (div[i]에서 시작)
            toggle_xpath = f'//*[@id="main"]/div[1]/div[3]/div/div[1]/div/div/div/div/div[{i}]/div[1]/div/div[7]/div/div/button'
            
            # 토글 버튼이 존재하는지 확인
            toggle_button = driver.find_element(By.XPATH, toggle_xpath)
            
            if toggle_button.is_displayed() and toggle_button.is_enabled():
                print(f"토글 버튼 {i} 발견, 클릭 중...")
                
                # 토글 버튼 클릭
                driver.execute_script("arguments[0].click();", toggle_button)
                time.sleep(2)  # 토글 펼쳐질 때까지 대기
                
                # 내부 토글 버튼 클릭
                inner_toggle_xpath = f'//*[@id="main"]/div[1]/div[3]/div/div[1]/div/div/div/div/div[{i}]/div[2]/div[2]/div[2]/button'
                
                try:
                    print(f"내부 토글 버튼 {i} 찾는 중...")
                    inner_toggle_button = wait.until(EC.element_to_be_clickable((By.XPATH, inner_toggle_xpath)))
                    print(f"내부 토글 버튼 {i} 클릭 중...")
                    driver.execute_script("arguments[0].click();", inner_toggle_button)
                    time.sleep(2)  # 클릭 후 대기
                    
                    # 스케줄 데이터 수집
                    print(f"스케줄 데이터 수집 중... (div[{i}])")
                    schedule_data = extract_schedule_data(driver, i)
                    if schedule_data:
                        print(f"선박명: {schedule_data['ship_name']}")
                        print(f"스케줄 행 수: {len(schedule_data['schedule_rows'])}")
                        all_schedule_data.append(schedule_data)
                    else:
                        print(f"스케줄 데이터 수집 실패 (div[{i}])")
                    
                except Exception as e:
                    print(f"내부 토글 버튼 {i} 클릭 실패: {e}")
                    continue  # 다음 토글 버튼으로 계속 진행
                    
        except Exception as e:
            # 해당 인덱스의 토글 버튼이 없으면 다음으로
            print(f"토글 버튼 {i} 없음: {e}")
            continue
    
    print("토글 버튼 클릭 완료")
    
    # 엑셀 파일 생성
    if all_schedule_data:
        print("엑셀 파일 생성 중...")
        create_excel_file(all_schedule_data)
    
    return all_schedule_data

def extract_schedule_data(driver, div_index):
    """
    스케줄 데이터를 추출하는 함수
    """
    try:
        # 선박명 추출
        ship_name_xpath = f'//*[@id="main"]/div[1]/div[3]/div/div[1]/div/div/div/div/div[{div_index}]/div[1]/div/div[3]/div/div/span[2]'
        ship_name_element = driver.find_element(By.XPATH, ship_name_xpath)
        ship_name = ship_name_element.text.strip()
        
        schedule_rows = []
        
        # 첫 번째 행 (div[2]/div[1]/div)
        try:
            first_row_cells = extract_row_cells(driver, div_index, 1)
            if first_row_cells:
                schedule_rows.append(first_row_cells)
                print(f"첫 번째 행: {first_row_cells}")
        except:
            pass
        
        # 중간 행들 (div[2]/div[2]/div/div[1]/div ~ div[2]/div[2]/div/div[n]/div)
        row_index = 1
        max_rows = 10  # 최대 10개 행까지만 확인 (무한 루프 방지)
        while row_index <= max_rows:
            try:
                print(f"중간 행 {row_index} 확인 중...")
                middle_row_cells = extract_row_cells(driver, div_index, 2, row_index)
                if middle_row_cells:
                    schedule_rows.append(middle_row_cells)
                    print(f"중간 행 {row_index}: {middle_row_cells}")
                else:
                    print(f"중간 행 {row_index} 없음")
                    break
                row_index += 1
            except Exception as e:
                print(f"중간 행 {row_index} 추출 실패: {e}")
                break
        
        # 마지막 행 (div[2]/div[3]/div)
        try:
            print(f"마지막 행 추출 시도 중... (div[{div_index}])")
            last_row_cells = extract_row_cells(driver, div_index, 3)
            if last_row_cells:
                schedule_rows.append(last_row_cells)
                print(f"마지막 행: {last_row_cells}")
            else:
                print(f"마지막 행 데이터 없음 (div[{div_index}])")
        except Exception as e:
            print(f"마지막 행 추출 실패 (div[{div_index}]): {e}")
        
        return {
            'ship_name': ship_name,
            'schedule_rows': schedule_rows
        }
        
    except Exception as e:
        print(f"스케줄 데이터 추출 실패 (div[{div_index}]): {e}")
        return None

def extract_row_cells(driver, div_index, row_type, middle_row_index=None):
    """
    각 행의 셀들을 개별적으로 추출하는 함수
    row_type: 1(첫번째행), 2(중간행), 3(마지막행)
    middle_row_index: 중간행일 때만 사용
    """
    try:
        cells = []
        cell_index = 1
        
        max_cells = 10  # 최대 10개 셀까지만 확인 (무한 루프 방지)
        while cell_index <= max_cells:
            try:
                if row_type == 1:  # 첫 번째 행
                    cell_xpath = f'//*[@id="main"]/div[1]/div[3]/div/div[1]/div/div/div/div/div[{div_index}]/div[2]/div[2]/div[1]/div/div[{cell_index}]'
                elif row_type == 2:  # 중간 행
                    cell_xpath = f'//*[@id="main"]/div[1]/div[3]/div/div[1]/div/div/div/div/div[{div_index}]/div[2]/div[2]/div[2]/div/div[{middle_row_index}]/div/div[{cell_index}]'
                elif row_type == 3:  # 마지막 행
                    cell_xpath = f'//*[@id="main"]/div[1]/div[3]/div/div[1]/div/div/div/div/div[{div_index}]/div[2]/div[2]/div[3]/div/div[{cell_index}]'
                
                print(f"셀 {cell_index} XPath 확인: {cell_xpath}")
                cell_element = driver.find_element(By.XPATH, cell_xpath)
                cell_text = cell_element.text.strip()
                cells.append(cell_text)
                print(f"셀 {cell_index} 추출 성공: {cell_text}")
                cell_index += 1
                
            except Exception as e:
                print(f"셀 {cell_index} 추출 실패: {e}")
                # 더 이상 셀이 없으면 break
                break
        
        return cells if cells else None
        
    except Exception as e:
        print(f"행 셀 추출 실패: {e}")
        return None

def format_date_time(date_time_str):
    """
    날짜/시간 문자열을 한국어 형식으로 변환
    예: "Wed 3rd Sep 15:00" -> "2025-09-03-수-15:00"
    """
    try:
        if not date_time_str or date_time_str.strip() == '':
            return ''
        
        # 요일 매핑
        day_mapping = {
            'Mon': '월', 'Tue': '화', 'Wed': '수', 'Thu': '목', 
            'Fri': '금', 'Sat': '토', 'Sun': '일'
        }
        
        # 월 매핑
        month_mapping = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        
        # 정규식으로 날짜/시간 파싱
        # 예: "Wed 3rd Sep 15:00" 또는 "Wed 3 Sep 15:00"
        pattern = r'(\w{3})\s+(\d{1,2})(?:st|nd|rd|th)?\s+(\w{3})\s+(\d{1,2}):(\d{2})'
        match = re.search(pattern, date_time_str)
        
        if match:
            day_name = match.group(1)
            day_num = match.group(2).zfill(2)
            month_name = match.group(3)
            hour = match.group(4).zfill(2)
            minute = match.group(5)
            
            # 한국어 요일
            korean_day = day_mapping.get(day_name, day_name)
            
            # 월 번호
            month_num = month_mapping.get(month_name, month_name)
            
            # 현재 연도 사용 (또는 2025년으로 고정)
            year = "2025"
            
            return f"{year}-{month_num}-{day_num}-{korean_day}-{hour}:{minute}"
        else:
            # 파싱 실패 시 원본 반환
            return date_time_str
            
    except Exception as e:
        print(f"날짜 형식 변환 실패: {e}")
        return date_time_str

def create_excel_file(schedule_data_list):
    """
    수집한 스케줄 데이터를 엑셀 파일로 저장하는 함수
    """
    try:
        # 오늘 날짜 폴더명 생성 (YYMMDD 형식)
        today = datetime.now()
        date_folder = today.strftime("%y%m%d")
        
        # MSC_DATA 폴더 경로
        msc_data_path = "MSC_DATA"
        
        # 날짜 폴더 경로
        date_folder_path = os.path.join(msc_data_path, date_folder)
        
        # 날짜 폴더가 없으면 생성
        if not os.path.exists(date_folder_path):
            os.makedirs(date_folder_path)
            print(f"날짜 폴더 생성: {date_folder_path}")
        
        # 엑셀 데이터 준비
        excel_data = []
        
        for schedule_data in schedule_data_list:
            ship_name = schedule_data['ship_name']
            schedule_rows = schedule_data['schedule_rows']
            
            # 각 스케줄 행을 엑셀 행으로 변환
            for row_cells in schedule_rows:
                if row_cells and len(row_cells) >= 4:  # 최소 4개 셀이 있는 경우만 처리
                    # 컬럼 구조: 선박명, Port, ETA, ETD
                    row_data = {
                        '선박명': ship_name,
                        'Port': row_cells[1] if len(row_cells) > 1 else '',  # 컬럼2
                        'ETA': format_date_time(row_cells[2] if len(row_cells) > 2 else ''),    # 컬럼3 (날짜 형식 변환)
                        'ETD': format_date_time(row_cells[3] if len(row_cells) > 3 else '')     # 컬럼4 (날짜 형식 변환)
                    }
                    excel_data.append(row_data)
        
        # DataFrame 생성
        df = pd.DataFrame(excel_data)
        
        # 엑셀 파일명 생성 (FALCON 서비스 구분)
        excel_filename = f"MSC_Schedule_FALCON_{date_folder}.xlsx"
        excel_filepath = os.path.join(date_folder_path, excel_filename)
        
        # 엑셀 파일 저장
        df.to_excel(excel_filepath, index=False, engine='openpyxl')
        
        print(f"엑셀 파일 생성 완료: {excel_filepath}")
        print(f"총 {len(excel_data)}개의 스케줄 데이터 저장됨")
        
        return excel_filepath
        
    except Exception as e:
        print(f"엑셀 파일 생성 실패: {e}")
        return None

def msc_search():
    """
    MSC 웹사이트에서 출발지(ningbo)와 도착지(jebel ali) 검색
    """
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gcm")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # WebDriver 초기화
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # 브라우저 창 최대화
    driver.maximize_window()
    
    try:
        # MSC 웹사이트 접속
        print("MSC 웹사이트 접속 중...")
        driver.get("https://www.msc.com/ko/search-a-schedule")
        
        # 페이지 로딩 대기
        wait = WebDriverWait(driver, 10)
        
        # 쿠키 허용 버튼 클릭 (있는 경우)
        try:
            print("쿠키 허용 버튼 확인 중...")
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
            cookie_button.click()
            print("쿠키 허용 버튼 클릭 완료")
            time.sleep(2)  # 쿠키 팝업 사라질 때까지 대기
        except:
            print("쿠키 허용 버튼이 없거나 이미 처리됨")
        
        # 출발지 입력 (ningbo)
        print("출발지 입력 중...")
        from_input = wait.until(EC.presence_of_element_located((By.ID, "from")))
        from_input.clear()
        from_input.send_keys("ningbo")
        
        # 자동완성 리스트 대기 및 선택
        time.sleep(2)  # 자동완성 리스트 로딩 대기
        from_input.send_keys(Keys.ARROW_DOWN)  # 첫 번째 자동완성 항목 선택
        from_input.send_keys(Keys.ENTER)  # 선택 확정
        
        print("출발지 선택 완료")
        
        # 도착지 입력 (jebel ali)
        print("도착지 입력 중...")
        to_input = wait.until(EC.presence_of_element_located((By.ID, "to")))
        to_input.clear()
        to_input.send_keys("jebel ali")
        
        # 자동완성 리스트 대기 및 선택
        time.sleep(2)  # 자동완성 리스트 로딩 대기
        to_input.send_keys(Keys.ARROW_DOWN)  # 첫 번째 자동완성 항목 선택
        to_input.send_keys(Keys.ENTER)  # 선택 확정
        
        print("도착지 선택 완료")
        
        # 검색 버튼 클릭
        print("검색 버튼 클릭 중...")
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div[1]/div[2]/div/div[2]/div/div/form[1]/div[2]/div[2]/div/button')))
        search_button.click()
        
        print("검색 완료!")
        
        # 결과 페이지 로딩 대기
        time.sleep(5)
        
        # 토글 버튼들 클릭
        print("토글 버튼들 클릭 중...")
        schedule_data_list = click_toggle_buttons(driver, wait)
        
        # 현재 URL 확인
        current_url = driver.current_url
        print(f"현재 페이지: {current_url}")
        
        return driver
        
    except Exception as e:
        print(f"오류 발생: {e}")
        driver.quit()
        return None

if __name__ == "__main__":
    driver = msc_search()
    if driver:
        print("모든 작업이 완료되었습니다. 브라우저를 닫습니다...")
        driver.quit()

