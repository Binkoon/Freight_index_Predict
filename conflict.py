from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os,time
from datetime import datetime, timedelta

import pandas as pd

def conflict_Crawling():
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
        # https://acleddata.com/platform/weekly-conflict-index  <- 여기 접속하면 되고
        driver.get("https://acleddata.com/platform/weekly-conflict-index")
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # scrollBy(0,700)만큼 내려주고
        driver.execute_script("window.scrollBy(0,700);")
        time.sleep(2)

        ## 2. 테이블 헤더 수집
        # //*[@id="root"]/div/div[1]/table/thead  -> 얜 나중에 엑셀파일로 생성할때 한번만 제일 윗 row에 박아주면 되고
        try:
            thead_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/table/thead')))
            th_elements = thead_element.find_elements(By.TAG_NAME, "th")
            
            headers = []
            for th in th_elements:
                headers.append(th.text.strip())
            
            print(f"테이블 헤더 수집 완료: {len(headers)}개 컬럼")
            print(f"헤더: {headers}")
            
        except Exception as e:
            print(f"테이블 헤더 수집 중 오류 발생: {e}")
            return

        ## 3. 데이터 수집
        # //*[@id="root"]/div/div[1]/table/tbody/tr[1] ~ //*[@id="root"]/div/div[1]/table/tbody/tr[9] <- 중요한건 이거지.  인덱스 1부터 9까지 row 싹 긁어주고
        # 그 다음 페이지네이션 딸깎 해주고  //*[@id="root"]/div/div[2]/div/div[3]/button[2]
        # 계속 해서 진행해. 그러다가 페이지네이션 xpath를 못찾는다 == 더 이상 다음 페이지가 존재하지 않는다는 뜻으로, 거기서 멈추고  긁어온 row들을 엑셀파일로 생성함.
        
        # 데이터 수집할 리스트 쳐담을거임
        all_table_data = []
        page_num = 1
        
        while True:
            try:
                print(f"페이지 {page_num} 데이터 수집 중...")
                
                # 현재 페이지의 tbody 찾기
                tbody_element = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[1]/table/tbody')
                
                # tr[1]부터 tr[10]까지 순회하면서 데이터 수집
                for tr_num in range(1, 11):
                    try:
                        tr_xpath = f'//*[@id="root"]/div/div[1]/table/tbody/tr[{tr_num}]'
                        tr_element = driver.find_element(By.XPATH, tr_xpath)
                        
                        # tr 안에 있는 td 싹 담아재낌
                        td_elements = tr_element.find_elements(By.TAG_NAME, "td")
                        row_data = []
                        for td in td_elements:
                            row_data.append(td.text.strip())
                        
                        # 빈 행이 아닌 경우만 추가
                        if any(cell.strip() for cell in row_data):
                            all_table_data.append(row_data)
                            
                    except Exception as e:
                        print(f"tr[{tr_num}] 수집 중 오류: {e}")
                        continue
                
                print(f"페이지 {page_num}: {len([row for row in all_table_data if any(cell.strip() for cell in row)])}개 행 수집")
                
                # 다음 페이지 버튼 찾기
                try:
                    next_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div[3]/button[2]')
                    
                    # 다음 페이지 버튼이 비활성화되어 있는지 확인
                    if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                        print("다음 페이지가 없습니다. 데이터 수집 완료!")
                        break
                    
                    # 다음 페이지로 이동
                    next_button.click()
                    time.sleep(2)  # 페이지 로딩 대기
                    page_num += 1
                    
                except Exception as e:
                    print(f"다음 페이지 버튼을 찾을 수 없습니다. 데이터 수집 완료! (오류: {e})")
                    break
                    
            except Exception as e:
                print(f"페이지 {page_num} 처리 중 오류 발생: {e}")
                break

        ## 4. 데이터 저장
        # 수집된 데이터가 있는지 확인
        if not all_table_data:
            print("수집된 데이터가 없습니다.")
            return

        # DATA 폴더 생성 (없으면할거)
        if not os.path.exists('DATA'):
            os.makedirs('DATA')

        # 현재 날짜를 YYMMDD 형식으로 변환할거임.
        current_date = datetime.now()
        current_date_str = current_date.strftime('%y%m%d')
        filename = f'CONFLICT_{current_date_str}.xlsx'
        filepath = os.path.join('DATA', filename)

        # DataFrame 생성 및 저장
        df = pd.DataFrame(all_table_data, columns=headers)
        df.to_excel(filepath, index=False)

        print(f"데이터 수집 완료: 총 {len(all_table_data)}개 행")
        print(f"엑셀로 저장때렸음: {filepath}")

    except Exception as e:
        print(f"오류뜸: {e}")
    
    finally:
        # 드라이버 꺼버림
        driver.quit()

if __name__ == '__main__':
    conflict_Crawling()