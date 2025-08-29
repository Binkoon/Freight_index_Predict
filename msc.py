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
    """MSC 스케줄 데이터 수집 (테스트: Tianjin 포트만)"""
    
    # 테스트용 포트 리스트 (Tianjin만)
    ports = ["Tianjin"]
    
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
        time.sleep(5)
        
        wait = WebDriverWait(driver, 15)
        
        ## 1. 스케줄 탭 클릭
        try:
            schedule_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main']/div[1]/div[2]/div/div[2]/div/div/div/button[3]/span")))
            schedule_tab.click()
            print("스케줄 탭 클릭 완료")
            time.sleep(3)
        except Exception as e:
            print(f"스케줄 탭 클릭 실패: {e}")
            return
        
        ## 2. 포트 입력 필드 활성화 및 입력
        try:
            # 포트 입력 필드 클릭하여 활성화
            port_input = wait.until(EC.element_to_be_clickable((By.ID, "countryport")))
            port_input.click()
            print("포트 입력 필드 활성화 완료")
            time.sleep(2)
            
            # 포트명 입력
            port_input.clear()
            port_input.send_keys("Tianjin")
            print("Tianjin 포트 입력 완료")
            time.sleep(3)
            
            # 자동완성 리스트에서 첫 번째 항목 선택 (있다면)
            try:
                autocomplete_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul/li[1]")))
                autocomplete_item.click()
                print("Tianjin 자동완성 선택 완료")
                time.sleep(2)
            except:
                print("자동완성 리스트가 없거나 선택 실패, 계속 진행")
            
        except Exception as e:
            print(f"포트 입력 실패: {e}")
            return
        
        ## 3. 검색 버튼 클릭 (검색 버튼의 XPath를 찾아야 함)
        try:
            # 검색 버튼 찾기 시도 (일반적인 검색 버튼 패턴)
            search_button = None
            
            # 여러 가능한 검색 버튼 패턴 시도
            search_patterns = [
                "//button[contains(text(), 'Search')]",
                "//button[contains(text(), '검색')]",
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(@class, 'search')]",
                "//button[contains(@class, 'btn')]"
            ]
            
            for pattern in search_patterns:
                try:
                    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, pattern)))
                    print(f"검색 버튼 발견: {pattern}")
                    break
                except:
                    continue
            
            if search_button:
                search_button.click()
                print("검색 버튼 클릭 완료")
                time.sleep(5)
            else:
                print("검색 버튼을 찾을 수 없음")
                return
                
        except Exception as e:
            print(f"검색 버튼 클릭 실패: {e}")
            return
        
        ## 4. 스케줄 데이터 확인
        try:
            print("스케줄 데이터 확인 중...")
            
            # 페이지 소스에서 스케줄 관련 정보 찾기
            page_source = driver.page_source
            
            # 스케줄 테이블이나 리스트 요소 찾기
            schedule_elements = driver.find_elements(By.XPATH, "//table | //div[contains(@class, 'schedule')] | //div[contains(@class, 'route')]")
            
            if schedule_elements:
                print(f"스케줄 요소 {len(schedule_elements)}개 발견")
                for i, element in enumerate(schedule_elements[:3]):  # 처음 3개만 확인
                    print(f"요소 {i+1}: {element.text[:200]}...")
            else:
                print("스케줄 요소를 찾을 수 없음")
            
            # 현재 페이지 URL과 제목 확인
            print(f"현재 페이지 URL: {driver.current_url}")
            print(f"페이지 제목: {driver.title}")
            
        except Exception as e:
            print(f"스케줄 데이터 확인 실패: {e}")
        
        print("MSC 스케줄 테스트 완료!")
        
    except Exception as e:
        print(f"MSC 스케줄 크롤링 중 오류 발생: {e}")
    finally:
        # 브라우저는 열어둔 상태로 유지 (데이터 확인용)
        print("브라우저를 열어둔 상태로 유지합니다. 확인 후 수동으로 닫아주세요.")
        # driver.quit()

if __name__ == '__main__':
    msc_schedule_crawling()