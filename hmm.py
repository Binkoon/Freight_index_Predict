# 선사 접속 링크 : https://www.hmm21.com/e-service/general/schedule/ScheduleMainPost.do
# //*[@id="tabItem02"]  by Port 클릭
# //*[@id="srchByPort_area"]  클릭
# 테스트용  QINGDAO, CHINA  입력
# //*[@id="tabItem02"]/div/div/div[1]/div[3]/button    RETRIVEVE 버튼 클릭

# 19개 포트 리스트 (완전한 순회 항로 - 18개 조합 생성)
# ["QINGDAO", "BUSAN", "SHANGHAI", "NINGBO", "KAOHSIUNG", "CHIWAN", "SINGAPORE", "JEBEL ALI", "DAMMAM", "JUBAIL", "HAMAD", "ABU DHABI", "JEBEL ALI", "SOHAR", "PORT KLANG", "SINGAPORE", "HONG KONG", "QINGDAO"]

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
from datetime import datetime

def hmm_schedule_crawling():
    """HMM 스케줄 데이터 수집 (Point to Point 방식 - 모든 포트 조합)"""
    
    # 19개 포트 리스트 (완전한 순회 항로 - 18개 조합 생성)
    ports = ["QINGDAO", "BUSAN", "SHANGHAI", "NINGBO", "KAOHSIUNG", "CHIWAN", "SINGAPORE", "JEBEL ALI", "DAMMAM", "JUBAIL", "HAMAD", "ABU DHABI", "JEBEL ALI", "SOHAR", "PORT KLANG", "SINGAPORE", "HONG KONG", "QINGDAO"]
    
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
    download_path = os.path.join(base_download_path, today)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"날짜 폴더 생성 완료: {download_path}")
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # JavaScript 실행으로 webdriver 속성 제거
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("HMM 사이트 접속 중...")
        driver.get("https://www.hmm21.com/e-service/general/DashBoard.do")
        time.sleep(3)
        
        wait = WebDriverWait(driver, 10)
        
        ## 1. 팝업 닫기
        try:
            popup_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[1]/div[1]/button")))
            popup_button.click()
            print("팝업 닫기 완료")
            time.sleep(3)
        except Exception as e:
            print(f"팝업 닫기 실패: {e}")
            return
        
        ## 2. 첫 번째 조합: QINGDAO → BUSAN (메인 대시보드에서)
        try:
            # From Port 선택 및 QINGDAO 입력
            from_port = wait.until(EC.element_to_be_clickable((By.ID, "fromPt")))
            from_port.click()
            from_port.clear()
            from_port.send_keys("QINGDAO")
            print("From Port에 QINGDAO 입력 완료")
            time.sleep(3)
            
            # 자동완성 리스트에서 첫 번째 항목 선택
            autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[9]/ul/li")))
            autocomplete_item.click()
            print("QINGDAO 자동완성 선택 완료")
            time.sleep(3)
            
            # To Port 선택 및 BUSAN 입력
            to_port = wait.until(EC.element_to_be_clickable((By.ID, "toPt")))
            to_port.click()
            to_port.clear()
            to_port.send_keys("BUSAN")
            print("To Port에 BUSAN 입력 완료")
            time.sleep(3)
            
            # 자동완성 리스트에서 첫 번째 항목 선택
            autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[10]/ul/li")))
            autocomplete_item.click()
            print("BUSAN 자동완성 선택 완료")
            time.sleep(3)
            
            # Sail Week 선택 (option value="4")
            sail_week = wait.until(EC.element_to_be_clickable((By.ID, "sailWk")))
            from selenium.webdriver.support.ui import Select
            select = Select(sail_week)
            select.select_by_value("4")
            print("Sail Week 4 선택 완료")
            time.sleep(3)
            
            # 검색 버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[2]/div[2]/div/div[4]/div/div[2]/div/div/ul/li[1]/div/div[4]/button")))
            search_button.click()
            print("검색 버튼 클릭 완료")
            time.sleep(5)
            
            # 첫 번째 조합 데이터 수집 및 저장
            collect_and_save_data("QINGDAO", "BUSAN", wait, download_path)
            
        except Exception as e:
            print(f"첫 번째 조합 처리 실패: {e}")
            return
        
        # 나머지 포트 조합들을 라우팅된 화면에서 처리
        for i in range(1, len(ports) - 1 ): # 
            from_port_name = ports[i]      # 현재 FROM 포트
            to_port_name = ports[i + 1]    # 다음 TO 포트
            
            print(f"\n=== {from_port_name} → {to_port_name} 조합 처리 시작 ===")
            
            try:
                ## 3. From Port 클리어 및 설정
                from_port = wait.until(EC.element_to_be_clickable((By.ID, "srchPointFrom")))
                from_port.click()
                from_port.clear()
                from_port.send_keys(from_port_name)
                print(f"From Port에 {from_port_name} 입력 완료")
                time.sleep(3)
                
                # 자동완성 리스트에서 첫 번째 항목 선택
                try:
                    autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[9]/ul/li")))
                    
                    # 일반 클릭 시도
                    try:
                        autocomplete_item.click()
                    except:
                        # 클릭이 실패하면 JavaScript로 클릭
                        driver.execute_script("arguments[0].click();", autocomplete_item)
                    
                    print(f"{from_port_name} 자동완성 선택 완료")
                    time.sleep(3)
                except Exception as e:
                    print(f"{from_port_name} 자동완성 선택 실패: {e}")
                    continue
                
                ## 4. To Port 클리어 및 설정
                try:
                    # To Port 필드가 클릭 가능한 상태가 될 때까지 대기
                    to_port = wait.until(EC.element_to_be_clickable((By.ID, "srchPointTo")))
                    
                    # JavaScript로 클릭 시도 (더 안전함)
                    try:
                        driver.execute_script("arguments[0].click();", to_port)
                        print("JavaScript로 To Port 클릭 완료")
                    except:
                        # JavaScript 실패 시 일반 클릭 시도
                        to_port.click()
                        print("일반 클릭으로 To Port 클릭 완료")
                    
                    to_port.clear()
                    to_port.send_keys(to_port_name)
                    print(f"To Port에 {to_port_name} 입력 완료")
                    time.sleep(3)
                except Exception as e:
                    print(f"To Port 입력 실패: {e}")
                    # 추가 대기 후 재시도
                    time.sleep(3)
                    to_port = wait.until(EC.element_to_be_clickable((By.ID, "srchPointTo")))
                    driver.execute_script("arguments[0].click();", to_port)
                    to_port.clear()
                    to_port.send_keys(to_port_name)
                    print(f"To Port 재시도로 {to_port_name} 입력 완료")
                    time.sleep(3)
                
                # 자동완성 리스트에서 첫 번째 항목 선택
                try:
                    autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[12]/ul/li")))
                    
                    # 일반 클릭 시도
                    try:
                        autocomplete_item.click()
                    except:
                        # 클릭이 실패하면 JavaScript로 클릭
                        driver.execute_script("arguments[0].click();", autocomplete_item)
                    
                    print(f"{to_port_name} 자동완성 선택 완료")
                    time.sleep(3)
                except Exception as e:
                    print(f"{to_port_name} 자동완성 선택 실패: {e}")
                    continue
                
                ## 5. PORT KLANG 모달 팝업 처리 (있는 경우)
                try:
                    # 모달 팝업이 있는지 확인
                    modal_element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='popup_facility_guide_list']/div[2]/div/div/div/table/tbody/tr[1]/td[2]/div/div/div/div/div/div/label/span[1]")))
                    if modal_element:
                        print("PORT KLANG 모달 팝업 감지, 처리 중...")
                        # 모달 팝업 요소 클릭
                        modal_element.click()
                        time.sleep(2)
                        
                        # Apply 버튼 클릭
                        apply_button = wait.until(EC.element_to_be_clickable((By.ID, "btnApply")))
                        apply_button.click()
                        print("모달 팝업 Apply 버튼 클릭 완료")
                        time.sleep(3)
                        
                        # 모달 팝업이 완전히 사라질 때까지 대기
                        try:
                            wait.until(EC.invisibility_of_element_located((By.ID, "popup_facility_guide_list")))
                            print("모달 팝업 완전히 닫힘 확인")
                        except:
                            print("모달 팝업 닫힘 확인 실패, 추가 대기")
                            time.sleep(2)
                except Exception as e:
                    print("모달 팝업이 없거나 처리 실패, 계속 진행: {e}")
                
                # 팝업이나 모달이 완전히 사라질 때까지 추가 대기
                time.sleep(2)
                
                ## 6. 검색 버튼 클릭
                search_button = wait.until(EC.element_to_be_clickable((By.ID, "btnRetrieve")))
                search_button.click()
                print("검색 버튼 클릭 완료")
                time.sleep(5)
                
                # 데이터 수집 및 저장
                collect_and_save_data(from_port_name, to_port_name, wait, download_path)
                
            except Exception as e:
                print(f"{from_port_name} → {to_port_name} 조합 처리 실패: {e}")
                continue

        print("모든 포트 조합 HMM 스케줄 데이터 수집 완료!")
        
    except Exception as e:
        print(f"HMM 스케줄 데이터 수집 중 오류 발생: {e}")
    finally:
        driver.quit()

def collect_and_save_data(from_port, to_port, wait, download_path):
    """데이터 수집 및 엑셀 저장 함수"""
    
    ## 7. 테이블 헤더 수집
    try:
        thead = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='lsitContentArea']/div/table/thead")))
        header_rows = thead.find_elements(By.TAG_NAME, "tr")
        
        headers = []
        for row in header_rows:
            th_elements = row.find_elements(By.TAG_NAME, "th")
            for th in th_elements:
                headers.append(th.text.strip())
        
        print(f"헤더 수집 완료: {len(headers)}개 컬럼")
    except Exception as e:
        print(f"헤더 수집 실패: {e}")
        return

    ## 8. 테이블 데이터 수집 (tr[1], tr[3], tr[5]... 패턴)
    try:
        table_data = []
        row_index = 1  # 1부터 시작
        
        while True:
            try:
                # tr[row_index] 요소 찾기
                row_xpath = f"//*[@id='scheduleListRow']/tr[{row_index}]"
                row_element = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
                
                # 행의 모든 td 셀 데이터 수집
                cells = row_element.find_elements(By.TAG_NAME, "td")
                row_data = []
                for cell in cells:
                    row_data.append(cell.text.strip())
                
                if row_data:  # 빈 행이 아닌 경우만 추가
                    table_data.append(row_data)
                    print(f"행 {row_index} 수집 완료")
                
                row_index += 2  # +2씩 증가
                
            except Exception:
                # 더 이상 행이 없으면 종료
                print(f"행 {row_index}에서 데이터 수집 종료")
                break
        
        print(f"데이터 수집 완료: {len(table_data)}개 행")
    except Exception as e:
        print(f"데이터 수집 실패: {e}")
        return

    ## 9. 엑셀 파일로 저장
    try:
        import pandas as pd
        from datetime import datetime
        
        # 데이터프레임 생성
        df = pd.DataFrame(table_data, columns=headers)
        
        # 파일명 생성 (from_to 형식, 날짜는 폴더에 포함됨)
        filename = f"{from_port}_{to_port}.xlsx"
        filepath = os.path.join(download_path, filename)
        
        # 엑셀 파일로 저장
        df.to_excel(filepath, index=False)
        print(f"엑셀 파일 저장 완료: {filepath}")
        
    except Exception as e:
        print(f"엑셀 파일 저장 실패: {e}")
        return

    print(f"=== {from_port} → {to_port} 조합 처리 완료 ===\n")

if __name__ == '__main__':
    hmm_schedule_crawling()