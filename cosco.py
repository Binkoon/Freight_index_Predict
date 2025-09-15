"""
코스코 쪽 준비 (middelEast)
1. 접속 : https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByCity
2. 탭 선택 (Schedule by Service) : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/ul/span[2]/li
3. Asian Pacific Service 탭 선택 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[1]/div[5]
4. Persian Gulf 탭 선택 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[6]/div[1]/span
5. MEX4 선택 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[6]/div[2]/div/ul/li[2]
6. Ports name input 클릭 활성화 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div/form/div/div[1]/div/div/div/div[1]/input
7. Qingdao 입력하고 자동완성 리스트 선택 
8. Search 버튼 클릭 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div/form/div/div[2]/button
"""

"""
코스코 쪽 준비 (westIndia)
1. 접속 : https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByCity
2. 탭 선택 (Schedule by Service) : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/ul/span[2]/li
3. SouthEast & South Asia Service 탭 선택 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[1]/div[8]
4. Middel East 탭 선택 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[2]
5. CI1 선택 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[2]/div[2]/div/ul/li[2]
6. Ports name input 클릭 활성화 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div/form/div/div[1]/div/div/div/div[1]/input
7. Ningbo 입력하고 자동완성 리스트 선택 
8. Search 버튼 클릭 : /html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div/form/div/div[2]/button
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
import glob
from datetime import datetime

def rename_downloaded_file(download_path, new_filename, download_start_time):
    """다운로드된 파일을 찾아서 이름을 변경하는 함수"""
    try:
        # 다운로드 폴더에서 다운로드 시작 시간 이후에 생성된 PDF 파일 찾기
        downloads_folder = os.path.expanduser("~/Downloads")
        
        # PDF 파일 패턴으로 찾기
        pattern = os.path.join(downloads_folder, "*.pdf")
        files = glob.glob(pattern)
        
        if not files:
            print("다운로드된 PDF 파일을 찾을 수 없습니다.")
            return
        
        # 다운로드 시작 시간 이후에 생성된 파일들만 필터링
        new_files = []
        for file in files:
            file_creation_time = os.path.getctime(file)
            if file_creation_time > download_start_time:
                new_files.append(file)
        
        if not new_files:
            print("다운로드 시작 이후 생성된 PDF 파일을 찾을 수 없습니다.")
            return
        
        # 새로 생성된 파일 중 가장 최근 파일 선택
        latest_file = max(new_files, key=os.path.getctime)
        
        # 새 파일명 생성 (PDF 확장자)
        new_filepath = os.path.join(download_path, f"{new_filename}.pdf")
        
        # 파일 이동 및 이름 변경
        import shutil
        shutil.move(latest_file, new_filepath)
        print(f"파일 이름 변경 완료: {os.path.basename(latest_file)} → {os.path.basename(new_filepath)}")
        
    except Exception as e:
        print(f"파일 이름 변경 실패: {e}")
        print("수동으로 파일명을 변경해주세요.")

def cosco_schedule_crawling():
    """COSCO 스케줄 데이터 수집 (MEX4, MEX5, MEX 서비스)"""
    
    # 서비스별 설정 (중동 서비스)
    middle_east_services = [
        {"name": "MEX4", "xpath": "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[6]/div[2]/div/ul/li[2]", "port": "Qingdao", "route_type": "middleEast"},
        {"name": "MEX5", "xpath": "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[6]/div[2]/div/ul/li[3]", "port": "Jebel Ali", "route_type": "middleEast"},
        {"name": "MEX", "xpath": "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[6]/div[2]/div/ul/li[4]", "port": "Qingdao", "route_type": "middleEast"}
    ]
    
    # 서인도 서비스 (CI1, CI2)
    west_india_services = [
        {"name": "CI1", "xpath": "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[7]/div[2]/div/ul/li[1]", "port": "Ningbo", "route_type": "westIndia"}
    ]
    
    # 모든 서비스 통합
    all_services = middle_east_services + west_india_services
    
    # 다운로드 경로 설정 (middleEast/westIndia 폴더 구조)
    base_download_path = os.path.join(os.getcwd(), "COSCO_DATA")
    if not os.path.exists(base_download_path):
        os.makedirs(base_download_path)
    
    # 오늘 날짜로 하위 폴더 생성
    today = datetime.now().strftime("%y%m%d")
    
    # middleEast 폴더 생성 (MEX 서비스용)
    middle_east_path = os.path.join(base_download_path, "middleEast", today)
    if not os.path.exists(middle_east_path):
        os.makedirs(middle_east_path)
        print(f"중동 서비스 폴더 생성 완료: {middle_east_path}")
    
    # westIndia 폴더 생성 (향후 서인도 서비스용)
    west_india_path = os.path.join(base_download_path, "westIndia", today)
    if not os.path.exists(west_india_path):
        os.makedirs(west_india_path)
        print(f"서인도 서비스 폴더 생성 완료: {west_india_path}")
    
    # 현재는 middleEast 사용
    download_path = middle_east_path
    
    # Chrome 옵션 설정 (봇 감지 방지)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 브라우저 창 크기 설정 (다운로드 버튼이 잘 보이도록)
    driver.set_window_size(1920, 1080)  # Full HD 해상도
    driver.maximize_window()  # 최대화
    
    # JavaScript 실행으로 webdriver 속성 제거
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("COSCO 사이트 접속 중...")
        driver.get("https://elines.coscoshipping.com/ebusiness/sailingSchedule/searchByCity")
        time.sleep(5)
        
        wait = WebDriverWait(driver, 15)
        
        ## 1. Schedule by Service 탭 선택
        try:
            print("Schedule by Service 탭 선택 중...")
            schedule_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/ul/span[2]/li")))
            schedule_tab.click()
            print("Schedule by Service 탭 선택 완료")
            time.sleep(3)
        except Exception as e:
            print(f"Schedule by Service 탭 선택 실패: {e}")
            return
        
        ## 2. Asian Pacific Service 탭 선택
        try:
            print("Asian Pacific Service 탭 선택 중...")
            asian_pacific_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[1]/div[5]")))
            asian_pacific_tab.click()
            print("Asian Pacific Service 탭 선택 완료")
            time.sleep(3)
        except Exception as e:
            print(f"Asian Pacific Service 탭 선택 실패: {e}")
            return
        
        ## 3. Persian Gulf 탭 선택
        try:
            print("Persian Gulf 탭 선택 중...")
            persian_gulf_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div[2]/div/div/div/div[6]/div[1]/span")))
            persian_gulf_tab.click()
            print("Persian Gulf 탭 선택 완료")
            time.sleep(3)
        except Exception as e:
            print(f"Persian Gulf 탭 선택 실패: {e}")
            return
        
        # 서비스별 반복 처리
        for i, service in enumerate(all_services):
            print(f"\n=== {service['name']} 서비스 처리 시작 ===")
            
            if i > 0:  # 첫 번째 서비스가 아닌 경우 뒤로가기 2번
                try:
                    print("뒤로가기 버튼 클릭 중... (1/2)")
                    back_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div/div[3]/i")))
                    back_button.click()
                    print("첫 번째 뒤로가기 완료")
                    time.sleep(2)
                    
                    print("뒤로가기 버튼 클릭 중... (2/2)")
                    back_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[1]/div/div[3]/i")))
                    back_button.click()
                    print("두 번째 뒤로가기 완료")
                    time.sleep(2)
                        
                except Exception as e:
                    print(f"뒤로가기 실패: {e}")
                    continue
            
            ## 4. 서비스 선택
            try:
                print(f"{service['name']} 서비스 선택 중...")
                service_element = wait.until(EC.element_to_be_clickable((By.XPATH, service['xpath'])))
                service_element.click()
                print(f"{service['name']} 서비스 선택 완료")
                time.sleep(3)
            except Exception as e:
                print(f"{service['name']} 서비스 선택 실패: {e}")
                continue
            
            ## 5. Ports name input 클릭 활성화 및 포트 입력
            try:
                print(f"포트 '{service['port']}' 입력 중...")
                port_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div/form/div/div[1]/div/div/div/div[1]/input")))
                port_input.click()
                port_input.clear()
                port_input.send_keys(service['port'])
                print(f"포트 '{service['port']}' 입력 완료")
                time.sleep(3)
                
                # 자동완성 리스트에서 첫 번째 항목 선택 (일반적인 패턴)
                try:
                    print("자동완성 리스트 확인 중...")
                    # 자동완성 리스트의 일반적인 패턴들 시도
                    autocomplete_selectors = [
                        "//ul[@class='el-autocomplete-suggestion__list']/li[1]",
                        "//div[contains(@class, 'autocomplete')]//li[1]",
                        "//div[contains(@class, 'suggestion')]//li[1]",
                        "//ul[contains(@class, 'list')]//li[1]"
                    ]
                    
                    autocomplete_selected = False
                    for selector in autocomplete_selectors:
                        try:
                            autocomplete_item = driver.find_element(By.XPATH, selector)
                            autocomplete_item.click()
                            print(f"자동완성 선택 완료 (selector: {selector})")
                            autocomplete_selected = True
                            break
                        except:
                            continue
                    
                    if not autocomplete_selected:
                        print("자동완성 리스트를 찾을 수 없어 엔터키로 선택")
                        port_input.send_keys("\n")
                    
                except Exception as e:
                    print(f"자동완성 처리 실패: {e}")
                    print("엔터키로 선택 시도")
                    port_input.send_keys("\n")
                
            except Exception as e:
                print(f"포트 입력 실패: {e}")
                continue
            
            ## 6. Search 버튼 클릭
            try:
                print("검색 버튼 클릭 중...")
                search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/div/form/div/div[2]/button")))
                search_button.click()
                print("검색 버튼 클릭 완료")
                time.sleep(5)  # 검색 결과 로딩 대기
                
                print(f"{service['name']} 스케줄 검색 완료!")
                
            except Exception as e:
                print(f"검색 버튼 클릭 실패: {e}")
                continue
            
            ## 7. 다운로드 버튼 클릭
            try:
                print("다운로드 버튼 클릭 중...")
                download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='capture']/div[1]/div[6]/p/span[3]/i")))
                
                # 다운로드 시작 시간 기록
                download_start_time = time.time()
                
                download_button.click()
                print("다운로드 버튼 클릭 완료")
                time.sleep(3)  # 다운로드 시작 대기
                
                # route_type에 따라 적절한 다운로드 경로 설정
                if service['route_type'] == 'middleEast':
                    current_download_path = middle_east_path
                else:  # westIndia
                    current_download_path = west_india_path
                
                # 다운로드된 파일 찾기 및 이름 변경
                print("다운로드된 파일 이름 변경 중...")
                rename_downloaded_file(current_download_path, f"cosco_{service['name']}", download_start_time)
                
                print(f"{service['name']} 스케줄 다운로드 완료!")
                
            except Exception as e:
                print(f"다운로드 버튼 클릭 실패: {e}")
                continue
        
        print("\n=== 모든 서비스 처리 완료 ===")
        print("브라우저를 닫습니다...")
        driver.quit()
        print("브라우저가 닫혔습니다.")
            
    except Exception as e:
        print(f"COSCO 스케줄 크롤링 중 오류 발생: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    cosco_schedule_crawling()
