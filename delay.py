######### 공유받은 파일 ##############
# 분석 예정 #### 코랩 -> vscode 이관 위함.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os, time
from datetime import datetime
import pandas as pd

def is_garbage_row(cells):
    """쓰레기 데이터 행인지 확인하는 함수"""
    joined = ''.join(cells)
    if not joined or all(cell.strip() in ('', 'None') for cell in cells):
        return True
    garbage_keywords = ['Leaflet', 'Humidity', 'Wind', 'Sign Up']
    return any(keyword in joined for keyword in garbage_keywords)

def extract_table_with_selenium(driver):
    """Selenium을 사용해서 테이블 데이터 추출"""
    try:
        # 테이블 직접 찾기
        table = driver.find_element(By.CSS_SELECTOR, 'div.table__wrapper table')
        
        # 헤더 추출
        headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]
        
        # 데이터 추출
        data = []
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # 헤더 제외
        
        for row in rows:
            cells = [td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")]
            if cells and not is_garbage_row(cells):
                data.append(cells)
        
        return pd.DataFrame(data, columns=headers)
    except Exception as e:
        print(f"테이블 추출 중 오류: {e}")
        return None

def port_data_crawling():
    """포트 데이터 크롤링 메인 함수"""
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
        # https://www.oceanlook.net/port  <- 여기 접속하면 되고
        driver.get("https://www.oceanlook.net/port")
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        ## 2. 데이터 수집
        all_data = pd.DataFrame()
        page_num = 1
        max_page = 122  # 최대 페이지 수 (안전장치)
        
        print("포트 데이터 수집 시작...")
        
        while page_num <= max_page:
            try:
                print(f"페이지 {page_num} 데이터 수집 중...")
                
                # 페이지 로딩 대기
                time.sleep(3)
                
                # 현재 페이지의 테이블 데이터 추출
                df = extract_table_with_selenium(driver)
                if df is not None and not df.empty:
                    all_data = pd.concat([all_data, df], ignore_index=True)
                    print(f"페이지 {page_num}: {len(df)}개 행 수집")
                else:
                    print(f"페이지 {page_num}: 데이터 없음")
                
                # 다음 페이지 버튼 찾기
                try:
                    next_button = driver.find_element(By.XPATH, '//div[contains(@class,"pagination")]//button[contains(text(),">")]')
                    
                    # 다음 페이지 버튼이 비활성화되어 있는지 확인
                    if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                        print("다음 페이지가 없습니다. 데이터 수집 완료!")
                        break
                    
                    # 다음 페이지로 이동
                    next_button.click()
                    page_num += 1
                    
                except Exception as e:
                    print(f"다음 페이지 버튼을 찾을 수 없습니다. 데이터 수집 완료! (오류: {e})")
                    break
                    
            except Exception as e:
                print(f"페이지 {page_num} 처리 중 오류 발생: {e}")
                break
        
        ## 3. 데이터 전처리
        if not all_data.empty:
            # 'Waiting in port', 'Berthing in port', 'Heading to port' 열을 숫자로 변환
            # 에러 발생 시 해당 셀의 값을 NaN으로 처리 (errors='coerce' 옵션 사용)
            numeric_columns = ['Waiting in port', 'Berthing in port', 'Heading to port']
            for col in numeric_columns:
                if col in all_data.columns:
                    all_data[col] = pd.to_numeric(all_data[col], errors='coerce')
            
            # 수집일자 설정
            collection_date = datetime.today().strftime('%Y-%m-%d')
            
            # 수집일자 컬럼 추가 (맨 앞에 삽입)
            all_data.insert(0, '수집일자', collection_date)
            
            ## 4. 포트 코드 매핑
            # 포트 코드 매핑 정보
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
            
            # 해당 포트만 필터링
            if 'PORT' in all_data.columns:
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
                if 'PORT CODE' in final.columns:
                    final_filtered = final[~final['PORT CODE'].isin(['PAMIT', 'DOMAN'])]
                else:
                    final_filtered = final
                
                # 21개 포트 데이터를 별도 변수로 저장
                target_ports_data = final_filtered
            else:
                target_ports_data = pd.DataFrame()
            
            # 원본 데이터는 그대로 유지 (필터링하지 않음)
            print(f"전체 데이터: {len(all_data)}개 행")
            print(f"21개 주요 포트 데이터: {len(target_ports_data)}개 행")
            
            ## 5. 데이터 저장 (두 개 탭으로 분리)
            # DATA 폴더 생성 (없으면할거)
            if not os.path.exists('DATA'):
                os.makedirs('DATA')
            
            # 현재 날짜를 YYMMDD 형식으로 변환할거임.
            current_date = datetime.now()
            current_date_str = current_date.strftime('%y%m%d')
            filename = f'PORT_DATA_{current_date_str}.xlsx'
            filepath = os.path.join('DATA', filename)
            
            # ExcelWriter를 사용해서 두 개 탭으로 저장
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 탭 1: 전체 데이터
                all_data.to_excel(writer, sheet_name='전체_데이터', index=False)
                
                # 탭 2: 21개 주요 포트 데이터
                if not target_ports_data.empty:
                    target_ports_data.to_excel(writer, sheet_name='21개_주요포트', index=False)
                else:
                    # 빈 시트라도 생성
                    pd.DataFrame().to_excel(writer, sheet_name='21개_주요포트', index=False)
            
            print(f"데이터 수집 완료!")
            print(f"전체 데이터: {len(all_data)}개 행")
            print(f"21개 주요 포트: {len(target_ports_data)}개 행")
            print(f"엑셀로 저장때렸음: {filepath}")
            print(f"  - 탭1: 전체_데이터")
            print(f"  - 탭2: 21개_주요포트")
        else:
            print("수집된 데이터가 없습니다.")
            
    except Exception as e:
        print(f"오류뜸: {e}")
    
    finally:
        # 드라이버 꺼버림
        driver.quit()

if __name__ == '__main__':
    port_data_crawling()