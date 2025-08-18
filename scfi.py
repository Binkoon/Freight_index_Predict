# 코드 작성 날짜 : 2025/08/01 (완료) - 디지털전략팀 강현빈 사원
# 로직 좀 수정할게 보이면  kanghb@ekmtc.com 이메일 or 행아웃 주시면 감사하겠습니다.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os,time
from datetime import datetime, timedelta

import pandas as pd

########### 여긴 주간 #############
# 매주 금요일 기준으로 긁어오기. 
# -> 다만, 금요일로 긁어올 경우 오전에는 아직 좀 비어있는 값들이 있어서 오후에 세팅하거나 토요일날 긁어와야 할 듯
def Week_SCFI_Crawling():
    pass

############# 여긴 데일리 ############
def Daily_SCFI_Crawling():
    ## 0. 사전 세팅
    # 화면을 띄울 때, 해상도는 Full로 해놓고 크롬을 사용할 것임.
    # user-agent 세팅 해놓을거임
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized") # 일단 걍 무조건 최대사이즈 박음.
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    try:
        ## 1. 사이트 방문
        # https://www.ine.cn/eng/reports/statistical/daily/
        driver.get("https://www.ine.cn/eng/reports/statistical/daily/")
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 스크롤을 내려서 캘린더 영역 보이게 하기
        driver.execute_script("window.scrollBy(0,400);")
        time.sleep(1)

        ## 2. 캘린더 선택을 해야함. 날짜는 현재 날짜 기준으로 1일 전을 클릭해야함
        # XPATH : //*[@id="home_calendar_cont"]/div[2]/table/tbody/tr[1] ~ //*[@id="home_calendar_cont"]/div[2]/table/tbody/tr[6]
        # tr[1]부터해서 무조건 tr[6]까지만 있음. 
        # tr의 하위 태그는 //*[@id="home_calendar_cont"]/div[2]/table/tbody/tr[1]/td[5]/div/p[1]  이런 형태인데,  tr[1] 아래에 td[?]/div/p[1] 안의 innerHTML 값이 일을 뜻함.
        # 일 표기 방식은 01, 02, 03, 04, ..... 10,11 ... 이런식의 문자열임.
        # 예를 들어 오늘이 2025년 8월 1일인 경우 하루전은 2025년 7월 31일이니, 이걸 선택하면 된다.

        # 좀 더 쉬운 방법은  td의 클래스명인데  오늘을 뜻하는 td 클래스명은 class="current is-selected is-today" 이므로 이거의 바로 1줄 위에 있는 td 클래스를 선택하면 될듯하다.
        
        # 어제날짜부터 시작해서 데이터가 있는 날짜를 찾을 때까지 하루씩 뒤로 가기
        # -> 다만, 평일에만 데이터가 업데이트되고 주말이나 공휴일에는 데이터가 없어서 에러가 발생함
        # -> "No data available" 메시지를 체크해서 데이터가 없으면 하루씩 뒤로 가면서 데이터가 있는 날짜를 찾음
        current_date = datetime.now()
        days_back = 1  # 어제부터 시작
        max_days_back = 30  # 최대 30일까지 뒤로 가기 (안전장치)
        
        print("데이터가 있는 날짜를 찾는 중...")
        
        while days_back <= max_days_back:
            try:
                # 현재 날짜에서 days_back만큼 뒤로 간 날짜 계산
                target_date = current_date - timedelta(days=days_back)
                target_day = str(target_date.day).zfill(2)
                
                print(f"{days_back}일 전 날짜 ({target_date.strftime('%Y-%m-%d')}) 확인 중...")
                
                # 오늘 날짜 td부터 찾기
                today_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.current.is-selected.is-today")))
                
                # 캘린더에서 target_date 날짜 찾기
                calendar_tbody = driver.find_element(By.XPATH, '//*[@id="home_calendar_cont"]/div[2]/table/tbody')
                
                # tr[1]부터 tr[6]까지 순회하면서 target_date 날짜 찾기
                date_found = False
                for tr_num in range(1, 7):
                    tr_xpath = f'//*[@id="home_calendar_cont"]/div[2]/table/tbody/tr[{tr_num}]'
                    tr_element = driver.find_element(By.XPATH, tr_xpath)
                    
                    # 해당 tr의 모든 td 찾기
                    td_elements = tr_element.find_elements(By.TAG_NAME, "td")
                    
                    for td in td_elements:
                        try:
                            # td 안의 div/p[1] 요소에서 날짜 텍스트 가져와야함. 꽁꽁 숨겨놓음 얘네
                            day_element = td.find_element(By.XPATH, "./div/p[1]")
                            day_text = day_element.get_attribute("innerHTML").strip()
                            
                            if day_text == target_day + '<br>':  # 사이트 만든놈이 캘린더에 쓸데없이 <br> 쳐 박아놔서 헤맴. 포함시킬것.
                                print(f"날짜 {target_day} 찾음. 클릭 시도...")
                                td.click()
                                date_found = True
                                break
                        except:
                            continue
                    
                    if date_found:
                        break
                
                if not date_found:
                    print(f"날짜 {target_day}를 캘린더에서 찾을 수 없습니다.")
                    days_back += 1
                    continue
                
                # 날짜 클릭 후 잠시 대기
                time.sleep(2)
                
                # "No data available" 메시지가 있는지 확인
                try:
                    no_data_element = driver.find_element(By.CSS_SELECTOR, "p.tiS")
                    no_data_text = no_data_element.text.strip()
                    
                    if "No data available" in no_data_text:
                        print(f"날짜 {target_date.strftime('%Y-%m-%d')}: 데이터 없음. 하루 더 뒤로...")
                        days_back += 1
                        continue
                    else:
                        print(f"날짜 {target_date.strftime('%Y-%m-%d')}: 데이터 발견! 크롤링 시작...")
                        break
                        
                except:
                    # "No data available" 메시지가 없다면 데이터가 있다는 뜻
                    print(f"날짜 {target_date.strftime('%Y-%m-%d')}: 데이터 발견! 크롤링 시작...")
                    break
                    
            except Exception as e:
                print(f"날짜 {target_date.strftime('%Y-%m-%d')} 확인 중 오류 발생: {e}")
                days_back += 1
                continue
        
        if days_back > max_days_back:
            print(f"최대 {max_days_back}일까지 뒤로 갔지만 데이터를 찾을 수 없습니다.")
            return
        
        print(f"최종 선택된 날짜: {target_date.strftime('%Y-%m-%d')}")
        time.sleep(2)

        ## 이어서 짤 로직 계획 
        # 3. 현재 y축으로 이동한 총량은 400임. 여기서 4400만큼 추가로 더 내려가야함.
        # 헤더는 ['Delivery month','Pre settle','Open','High','Low','close','Settle','ch1','ch2','volume','Turnover','0.I','Change']
        # //*[@id="export-table"]/div[1]/div[2]/div[6]/div/div[3]/table/tbody/tr[2] <- 일단 tr인덱스 타면서 row 따오는건 여기서부터 시작하는게 맞는데 break 조건이 있음.
        # 브레이크 조건같은 경우는 By.CLASS_NAME 으로 필터링 해야함.
        # el-table__row el-table__row--striped isTotal  혹은 el-table__row isTotal   이렇게 클래스명에 'isTotal' 이 포함되어있으면 멈추고 루핑 끝내야함.
        # 루핑 끝나면 헤더랑 따온 tr값들을 엑셀에 저장해주셈. 저장 경로는 루트 디렉토리 아래에 DATA폴더 안에다 넣으면 되고, 파일명은 DAILY_SCFI_어제날짜  로 저장하자.  (Ex. 어제날짜 250731)
        
        # 테이블 영역까지 스크롤 이동 추가로 더해야함. speices : ec_f인가 뭔가 대충 y축으로 4800px 이동해야 있음.
        driver.execute_script("window.scrollBy(0,4400);")
        time.sleep(2)

        # 헤더값 이리 가져올거임. (사이트랑 똑같이 가져올거임)
        headers = ['Delivery month','Pre settle','Open','High','Low','close','Settle','ch1','ch2','volume','Turnover','0.I','Change']

        # 데이터 수집할 리스트 쳐담을거임
        table_data = []

        # tr[2]부터 시작해서 데이터 수집
        tr_index = 2
        while True:
            try:
                tr_xpath = f'//*[@id="export-table"]/div[1]/div[2]/div[6]/div/div[3]/table/tbody/tr[{tr_index}]'
                tr_element = driver.find_element(By.XPATH, tr_xpath)
                
                # 클래스명에 'isTotal'이 포함되어 있으면 루핑 종료시킬거임.
                tr_class = tr_element.get_attribute("class")
                if 'isTotal' in tr_class:
                    print(f"tr[{tr_index}] isTotal 클래스 발견함, ㅃㅇㅃㅇ 퇴근함")
                    break
                
                # tr 안에 있는 td 싹 담아재낌
                td_elements = tr_element.find_elements(By.TAG_NAME, "td")
                row_data = []
                for td in td_elements:
                    row_data.append(td.text.strip())
                
                table_data.append(row_data)
                tr_index += 1
                
            except Exception as e:
                print(f"tr[{tr_index}] 오류 또는 데이터 없음: {e}")
                break

            # DATA 폴더 생성 (없으면할거)
            if not os.path.exists('DATA'):
                os.makedirs('DATA')

            # 어제 날짜를 YYMMDD 형식으로 변환할거임.
            yesterday_str = target_date.strftime('%y%m%d') # 최종 선택된 날짜를 사용
            filename = f'DAILY_SCFI_{yesterday_str}.xlsx'
            filepath = os.path.join('DATA', filename)

            df = pd.DataFrame(table_data, columns=headers)
            df.to_excel(filepath, index=False)

            print(f"데이터 수집 중: {len(table_data)}개 행")
            print(f"엑셀로 저장때렸음: {filepath}")

    except Exception as e:
        print(f"오류뜸: {e}")
    
    finally:
        # 드라이버 꺼버림
        driver.quit()

if __name__ == '__main__':
    Daily_SCFI_Crawling()