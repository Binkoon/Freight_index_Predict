# 선사 접속 링크 : https://www.hmm21.com/e-service/general/schedule/ScheduleMainPost.do
# //*[@id="tabItem01"]  by Port 클릭
# //*[@id="srchByPort_area"]  클릭
# 테스트용  QINGDAO, CHINA  입력
# //*[@id="tabItem02"]/div/div/div[1]/div[3]/button    RETRIVEVE 버튼 클릭

# 19개 포트 리스트 (완전한 순회 항로 - 18개 조합 생성)  -> 중동 서비스 항로
# ["QINGDAO", "BUSAN", "SHANGHAI", "NINGBO", "KAOHSIUNG", "CHIWAN", "SINGAPORE", "JEBEL ALI", "DAMMAM", "JUBAIL", "HAMAD", "ABU DHABI", "JEBEL ALI", "SOHAR", "PORT KLANG", "SINGAPORE", "HONG KONG", "QINGDAO"]

# 또 다른 포트 리스트 (완전한 순회 항로로 가야함) -> 서인도 서비스 항로
# Busan, Kwangyang, Shanghai, Ningbo, Shekou, Kaohsiung, Singapore, Port Kelang (W), Mumbai-Nhava Sheva, Hazira, Mundra, Karachi, Port Kelang (W), Singapore, Dachan Bay, Kaohsiung, Busan

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import os
import time
from datetime import datetime
import glob
import shutil
import pandas as pd

def hmm_schedule_crawling():
    """HMM 스케줄 데이터 수집 - 새로운 URL 사용"""
    
    # 중동 서비스 항로 포트 리스트 (19개 포트 - 18개 조합 생성)
    middle_east_ports = ["XINGANG", "BUSAN", "SHANGHAI", "NINGBO", "KAOHSIUNG", "CHIWAN", "SINGAPORE", "JEBEL ALI", "DAMMAM", "JUBAIL", "HAMAD", "ABU DHABI", "JEBEL ALI", "SOHAR", "PORT KLANG", "SINGAPORE", "HONG KONG", "Xingang"]
    
    # 서인도 서비스 항로 포트 리스트
    west_india_ports = ["Busan", "Gwangyang", "SHANGHAI", "NINGBO", "Shekou", "Kaohsiung", "Singapore", "PORT KLANG", "Nhava Sheva", "Hazira", "Mundra", "Karachi", "PORT KLANG", "Singapore", "Da chan Bay", "Kaohsiung", "Busan"]
    
    # 두 항로 모두 처리
    route_configs = [
        {"ports": middle_east_ports, "folder": "middleEast", "name": "중동서비스"},
        {"ports": west_india_ports, "folder": "westIndia", "name": "서인도서비스"}
    ]
    
    # Chrome 옵션 설정 (봇 감지 방지)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 다운로드 경로 설정
    base_download_path = os.path.join(os.getcwd(), "HMM_DATA")
    if not os.path.exists(base_download_path):
        os.makedirs(base_download_path)
    
    # 오늘 날짜로 하위 폴더 생성
    today = datetime.now().strftime("%y%m%d")
    
    # 다운로드 경로를 기본 HMM_DATA로 설정 (항로별 폴더는 나중에 생성)
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": base_download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 브라우저 창 최대화
    driver.maximize_window()
    
    # JavaScript 실행으로 webdriver 속성 제거
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("HMM 스케줄 페이지 접속 중...")
        driver.get("https://www.hmm21.com/e-service/general/schedule/ScheduleMainPost.do")
        time.sleep(5)
        
        wait = WebDriverWait(driver, 10)
        
        # tabItem01 클릭
        print("tabItem01 클릭 중...")
        tab_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="tabItem01"]')))
        tab_button.click()
        print("tabItem01 클릭 완료!")
        time.sleep(3)
        
        # 두 항로 모두 처리
        for route_config in route_configs:
            print(f"\n=== {route_config['name']} 항로 크롤링 시작 ===")
            process_route_new(driver, wait, route_config, today)
        
        print("\n모든 HMM 항로 크롤링이 완료되었습니다!")
        
    except Exception as e:
        print(f"HMM 크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()

def process_route_new(driver, wait, route_config, today):
    """새로운 방식으로 특정 항로의 포트 조합들을 처리하는 함수"""
    ports = route_config["ports"]
    folder_name = route_config["folder"]
    route_name = route_config["name"]
    
    # 항로별 폴더 생성
    base_download_path = os.path.join(os.getcwd(), "HMM_DATA")
    route_folder = os.path.join(base_download_path, folder_name)
    if not os.path.exists(route_folder):
        os.makedirs(route_folder)
        print(f"{route_name} 폴더 생성: {route_folder}")
    
    # 날짜 폴더 생성
    download_path = os.path.join(route_folder, today)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"날짜 폴더 생성: {download_path}")
    
    # 다운로드 순서 추적을 위한 카운터
    download_counter = 1
    
    # Chrome 다운로드 경로 동적 변경
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': download_path
    })
    
    try:
        # 포트 조합들을 순차적으로 처리
        for i in range(len(ports) - 1):
            from_port_name = ports[i]      # 현재 FROM 포트
            to_port_name = ports[i + 1]    # 다음 TO 포트
            
            print(f"\n=== {from_port_name} → {to_port_name} 조합 처리 시작 ===")
            
            try:
                # 1. 출발지 입력
                print(f"출발지 입력 중: {from_port_name}")
                from_port = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="srchPointFrom"]')))
                from_port.click()
                from_port.clear()
                from_port.send_keys(from_port_name)
                time.sleep(1)
                
                # 자동완성 리스트에서 첫 번째 항목 선택
                try:
                    # 자동완성 리스트가 나타날 때까지 대기
                    time.sleep(2)
                    autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[9]/ul/li')))
                    
                    # JavaScript로 클릭 시도 (더 안정적)
                    try:
                        driver.execute_script("arguments[0].click();", autocomplete_item)
                        print(f"{from_port_name} 자동완성 선택 완료 (JavaScript)")
                    except:
                        # JavaScript 실패 시 일반 클릭
                        autocomplete_item.click()
                        print(f"{from_port_name} 자동완성 선택 완료 (일반 클릭)")
                    
                    time.sleep(1)
                    
                    # PORT KLANG 모달 팝업 처리 (자동완성 선택 후 확인)
                    handle_port_klang_modal(driver, wait, from_port_name, route_name)
                    
                except Exception as e:
                    print(f"{from_port_name} 자동완성 선택 실패: {e}")
                    # 자동완성 실패 시 Enter 키로 선택 시도
                    try:
                        from_port.send_keys("\n")
                        print(f"{from_port_name} Enter 키로 선택 시도")
                        time.sleep(1)
                        # Enter 키 선택 후에도 모달 확인
                        handle_port_klang_modal(driver, wait, from_port_name, route_name)
                    except:
                        print(f"{from_port_name} Enter 키 선택도 실패")
                        continue
                
                # 2. 도착지 입력
                print(f"도착지 입력 중: {to_port_name}")
                to_port = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="srchPointTo"]')))
                to_port.click()
                to_port.clear()
                to_port.send_keys(to_port_name)
                time.sleep(1)
                
                # 자동완성 리스트에서 첫 번째 항목 선택
                try:
                    # 자동완성 리스트가 나타날 때까지 대기
                    time.sleep(2)
                    autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[10]/ul/li')))
                    
                    # JavaScript로 클릭 시도 (더 안정적)
                    try:
                        driver.execute_script("arguments[0].click();", autocomplete_item)
                        print(f"{to_port_name} 자동완성 선택 완료 (JavaScript)")
                    except:
                        # JavaScript 실패 시 일반 클릭
                        autocomplete_item.click()
                        print(f"{to_port_name} 자동완성 선택 완료 (일반 클릭)")
                    
                    time.sleep(1)
                    
                    # PORT KLANG 모달 팝업 처리 (자동완성 선택 후 확인)
                    handle_port_klang_modal(driver, wait, to_port_name, route_name)
                    
                except Exception as e:
                    print(f"{to_port_name} 자동완성 선택 실패: {e}")
                    # 자동완성 실패 시 Enter 키로 선택 시도
                    try:
                        to_port.send_keys("\n")
                        print(f"{to_port_name} Enter 키로 선택 시도")
                        time.sleep(1)
                        # Enter 키 선택 후에도 모달 확인
                        handle_port_klang_modal(driver, wait, to_port_name, route_name)
                    except:
                        print(f"{to_port_name} Enter 키 선택도 실패")
                        continue
                
                # 3. 4주 선택 (Select 드롭다운)
                print("4주 선택 중...")
                try:
                    week_select = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="srchSelWeeks"]')))
                    select = Select(week_select)
                    select.select_by_value("4")
                    print("4주 선택 완료")
                    time.sleep(1)
                except Exception as e:
                    print(f"4주 선택 실패: {e}")
                    continue
                
                # 4. 검색 버튼 클릭
                print("검색 버튼 클릭 중...")
                try:
                    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnRetrieve"]')))
                    search_button.click()
                    print("검색 버튼 클릭 완료")
                    time.sleep(3)  # 검색 결과 로딩 대기
                except Exception as e:
                    print(f"검색 버튼 클릭 실패: {e}")
                    continue
                
                # 5. 엑셀 다운로드
                print("엑셀 다운로드 중...")
                try:
                    excel_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnSub01Excel"]')))
                    excel_button.click()
                    print("엑셀 다운로드 버튼 클릭 완료")
                    time.sleep(2)  # 다운로드 완료 대기
                    
                    # 6. 파일명 변경
                    rename_downloaded_file(download_path, from_port_name, to_port_name, download_counter)
                    download_counter += 1
                    
                except Exception as e:
                    print(f"엑셀 다운로드 실패: {e}")
                    continue
                
            except Exception as e:
                print(f"{from_port_name} → {to_port_name} 조합 처리 실패: {e}")
                continue
        
        print(f"\n{route_name} 항로 크롤링 완료! 총 {download_counter-1}개 파일 다운로드됨")
        
    except Exception as e:
        print(f"{route_name} 항로 처리 중 오류 발생: {e}")

def handle_port_klang_modal(driver, wait, port_name, route_name):
    """PORT KLANG 모달 팝업 처리 함수"""
    try:
        # 모달 팝업이 나타나는지 확인 (1초 대기)
        time.sleep(1)
        
        # 항로에 따라 다른 라디오 버튼 선택
        if "서인도" in route_name:
            # 서인도 서비스: tr[3] 라디오 버튼
            radio_xpath = '//*[@id="popup_facility_guide_list"]/div[2]/div/div/div/table/tbody/tr[3]/td[2]/div/div/div/div/div/div/label/span[1]'
        else:
            # 중동 서비스: tr[1] 라디오 버튼
            radio_xpath = '//*[@id="popup_facility_guide_list"]/div[2]/div/div/div/table/tbody/tr[1]/td[2]/div/div/div/div/div/div/label/span[1]'
        
        # 모달 팝업의 라디오 버튼이 나타나는지 확인
        radio_button = wait.until(EC.element_to_be_clickable((By.XPATH, radio_xpath)))
        
        # 라디오 버튼 클릭
        radio_button.click()
        print(f"{port_name} PORT KLANG 모달 - 라디오 버튼 선택 완료 ({route_name})")
        time.sleep(0.5)
        
        # Apply 버튼 클릭
        apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnApply"]')))
        apply_button.click()
        print(f"{port_name} PORT KLANG 모달 - Apply 버튼 클릭 완료")
        time.sleep(1)
        
    except Exception as e:
        # 모달이 나타나지 않으면 무시 (PORT KLANG이 아닌 경우)
        pass

def rename_downloaded_file(download_path, from_port, to_port, download_counter):
    """다운로드된 파일의 이름을 변경하고 CSV로 변환하는 함수"""
    try:
        # 다운로드 폴더에서 가장 최근에 생성된 .xls 또는 .xlsx 파일 찾기
        excel_files = glob.glob(os.path.join(download_path, "*.xls*"))
        
        if not excel_files:
            print(f"다운로드된 엑셀 파일을 찾을 수 없습니다: {from_port} → {to_port}")
            return
        
        # 가장 최근 파일 선택 (수정 시간 기준)
        latest_file = max(excel_files, key=os.path.getmtime)
        
        # 새 파일명 생성 (원본 확장자 유지)
        original_ext = os.path.splitext(latest_file)[1]  # .xls 또는 .xlsx
        new_filename = f"{download_counter:02d}_{from_port}_{to_port}{original_ext}"
        new_filepath = os.path.join(download_path, new_filename)
        
        # 파일명 변경
        if os.path.exists(latest_file):
            shutil.move(latest_file, new_filepath)
            print(f"파일명 변경 완료: {new_filename}")
            
            # XLS를 CSV로 변환
            convert_xls_to_csv(new_filepath, from_port, to_port, download_counter)
        else:
            print(f"파일을 찾을 수 없습니다: {latest_file}")
            
    except Exception as e:
        print(f"파일명 변경 실패 ({from_port} → {to_port}): {e}")

def convert_xls_to_csv(xls_filepath, from_port, to_port, download_counter):
    """XLS 파일을 CSV로 변환하는 함수"""
    try:
        # XLS 파일 읽기
        df = pd.read_excel(xls_filepath, engine='xlrd')
        
        # CSV 파일명 생성
        csv_filename = f"{download_counter:02d}_{from_port}_{to_port}.csv"
        csv_filepath = os.path.join(os.path.dirname(xls_filepath), csv_filename)
        
        # CSV로 저장 (UTF-8 인코딩, 한글 지원)
        df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
        print(f"CSV 변환 완료: {csv_filename}")
        
        # 원본 XLS 파일 삭제 (선택사항)
        # os.remove(xls_filepath)
        # print(f"원본 XLS 파일 삭제: {os.path.basename(xls_filepath)}")
        
    except Exception as e:
        print(f"CSV 변환 실패: {e}")

if __name__ == "__main__":
    hmm_schedule_crawling()