# https://www.maersk.com/schedules/portCalls  이 선사에 접속
# [A,B] 형태로 내가 리스트를 던져줄거임,  A는 국가고  B는 Port임
# ex. [[A,B],[A,B],[A,B].....]

# 해당 사이트 접속 시, 국가/지역 선택하는 Xpath //*[@id="mc-input-countryRegion"]  <- 드랍다운 박스인데 input이 가능하고 국가 입력하면 자동완성 된다. 리스트가 여러개일 경우 제일 위에거를 선택하면 된다.
# 다음으로는 항구 선택이다 //*[@id="mc-input-port"]  <- 국가/지역 이랑 똑같음. 
# 일  클릭 //*[@id="numberOfDays-input"]  <- 이건데 얘는 셀렉트박스임. 무조건 14를 선택해라.
# 검색 클릭  //*[@id="schedules_app"]/main/div/div[1]/form/div[5]/mc-button//div/button/div
# 검색 후 리스트가 뜨면  //*[@id="mi-tray-arrow-down"]/path  <- 이거 클릭하게 하셈. 엑셀 다운로드 버튼이라 다운로드 동안 기다려 줘야함.
"""
[국가/지역 , 항구] 리스트업 ->  [['China','Ningbo'] ,['China','Shanghai'], ['China','Shekou'],['Malaysia','Tanjung Pelepas'],
    ['Malaysia','Port Klang'],['United Arab Emirates','Jebel Ali'],['Sri Lanka','Colombo'],['Singapore','Singapore'],['China','Ningbo']]
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time
from datetime import datetime, timedelta
from pyshadow.main import Shadow

def maersk_schedule_crawling():
    ## 0. 사전 세팅
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized") # 무조건 최대사이즈로 박음
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # 다운로드 경로 설정
    download_path = os.path.join(os.getcwd(), 'MASERSK_DATA')
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    # Shadow 객체 선언 -> 진짜 개빡ㅊㅣㅁ 이거
    shadow = Shadow(driver)

    try:
        ## 1. URL 파라미터로 직접 접근 (이미 선택된 상태)
        # 날짜 계산: 오늘 날짜
        current_date = datetime.now()
        date_str = current_date.strftime('%Y-%m-%d')
        
        ## 3. URL 리스트 순회 + 다운로드
        # 각 portGeoId에 해당하는 URL들을 직접 방문하여 다운로드
        
        url_list = [
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=104T898SJZ6GU&fromDate={date_str}&numberOfDays=14",
                'nation': 'china',
                'port': 'ningbo'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=2IW9P6J7XAW72&fromDate={date_str}&numberOfDays=14",
                'nation': 'china',
                'port': 'shanghai'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=1PLJHUYRVY2ZD&fromDate={date_str}&numberOfDays=14",
                'nation': 'china',
                'port': 'shekou'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=2DTLIHUG9YN7S&fromDate={date_str}&numberOfDays=14",
                'nation': 'malaysia',
                'port': 'tanjung_pelepas'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=3EX2D23UHZ8GS&fromDate={date_str}&numberOfDays=14",
                'nation': 'malaysia',
                'port': 'port_klang'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=31RTK5H2BLBS3&fromDate={date_str}&numberOfDays=14",
                'nation': 'uae',
                'port': 'jebel_ali'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=00A29CXK4A8PL&fromDate={date_str}&numberOfDays=14",
                'nation': 'sri_lanka',
                'port': 'colombo'
            },
            {
                'url': f"https://www.maersk.com/schedules/portCalls?portGeoId=0XOP5ISJZK0HR&fromDate={date_str}&numberOfDays=14",
                'nation': 'singapore',
                'port': 'singapore'
            }
        ]
        
        print(f"=== {len(url_list)}개 URL 순회 + 다운로드 시작 ===")
        
        for i, url_info in enumerate(url_list, 1):
            try:
                print(f"\n=== {i}/{len(url_list)}: {url_info['nation']} - {url_info['port']} ===")
                
                # 1단계: URL 방문
                print(f"1. URL 방문 중: {url_info['nation']} - {url_info['port']}")
                driver.get(url_info['url'])
                time.sleep(10)  # 페이지 로딩 대기
                
                # 2단계: 팝업 처리 (있다면)
                try:
                    cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="coiPage-1"]/div[1]/div/div[2]/div/button[2]')))
                    cookie_button.click()
                    print("쿠키 팝업 처리 완료")
                    time.sleep(3)
                except Exception as e:
                    print("쿠키 팝업 없음")
                
                # 3단계: 다운로드 버튼 클릭 (JavaScript만)
                print("2. 다운로드 버튼 클릭 중...")
                
                # 페이지 로딩을 위한 추가 대기
                time.sleep(5)
                
                try:
                    # mc-button[2] 요소를 먼저 찾고, JavaScript로 내부 button 찾기
                    mc_button = driver.find_element(By.XPATH, '//*[@id="schedules_app"]/main/div/div[2]/div[1]/div[2]/mc-button[2]')
                    
                    # JavaScript로 mc-button 내부의 Shadow DOM에서 button 찾기
                    download_button = driver.execute_script("""
                        var mcButton = arguments[0];
                        var shadowRoot = mcButton.shadowRoot;
                        var button = shadowRoot.querySelector('button[aria-label="다운로드"]');
                        return button;
                    """, mc_button)
                    
                    if download_button:
                        driver.execute_script("arguments[0].click();", download_button)
                        print("✅ 다운로드 시작!")
                    else:
                        print("❌ 다운로드 button을 찾을 수 없음")
                        continue
                        
                except Exception as e:
                    print(f"❌ 다운로드 버튼 클릭 실패: {e}")
                    continue
                
                # 4단계: 다운로드 완료 대기
                print("3. 다운로드 완료 대기 중...")
                time.sleep(30)  # 다운로드 완료 대기
                
                # 5단계: 파일명 변경
                print("4. 파일명 변경 중...")
                current_date_str = datetime.now().strftime('%y%m%d')
                new_filename = f"{url_info['nation']}_{url_info['port']}_{current_date_str}.xlsx"
                new_filepath = os.path.join(download_path, new_filename)
                
                # 다운로드된 파일 찾기 (가장 최근 파일)
                downloaded_files = [f for f in os.listdir(download_path) if f.endswith('.xlsx')]
                if downloaded_files:
                    # 가장 최근 파일을 새 이름으로 변경
                    latest_file = max([os.path.join(download_path, f) for f in downloaded_files], key=os.path.getctime)
                    os.rename(latest_file, new_filepath)
                    print(f"✅ 파일명 변경 완료: {new_filename}")
                else:
                    print("❌ 다운로드된 파일을 찾을 수 없음")
                
                print(f"✅ {url_info['nation']} - {url_info['port']} 완료!")
                
                # 다음 URL 방문 전 대기
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ {url_info['nation']} - {url_info['port']} 처리 중 오류: {e}")
                continue
        
        print(f"\n=== 모든 {len(url_list)}개 URL 다운로드 완료! ===")

    except Exception as e:
        print(f"오류뜸: {e}")
    
    finally:
        # 드라이버 꺼버림
        driver.quit()

if __name__ == '__main__':
    maersk_schedule_crawling()