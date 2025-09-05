# seleniumbase 라는 모듈 쓸 것. 클라우드 플레어 우회를 위함.
# //*[@id="cc_dialog"]/div/div[2]/button[1]   <- 쿠키 허용 버튼임. 클릭 시키기.
# Shanghai, Ningbo, Nansha, Shekou, Singapore, Jebel Ali, Dammam, Hamad Port, Singapore, Shanghai   -> pORT LIST
# //*[@id="originInput"]  <- Origin Port인데 클릭 활성화 해주고  값넣기  그러면 뜨는 자동완성 리스트 //*[@id="mainSail"]/div[2]/div[1]/ul/li
# //*[@id="destiInput"]  <- Destination Port인데 클릭 활성화 해주고 값넣기  그러면 뜨는 자동완성 리스트 //*[@id="mainSail"]/div[2]/div[4]/ul/li
# //*[@id="sailSearch"]  검색 버튼 클릭 

from seleniumbase import SB
import time
import os
from datetime import datetime

def rcl_schedule_crawling():
    """RCL 스케줄 데이터 수집 (테스트: Shanghai -> Ningbo)"""
    
    # 테스트용 포트 조합
    origin_port = "Shanghai"
    destination_port = "Ningbo"
    
    # 다운로드 경로 설정 (middleEast/westIndia 폴더 구조)
    base_download_path = os.path.join(os.getcwd(), "RCL_DATA")
    if not os.path.exists(base_download_path):
        os.makedirs(base_download_path)
    
    # 오늘 날짜로 하위 폴더 생성
    today = datetime.now().strftime("%y%m%d")
    
    # middleEast 폴더 생성
    middle_east_path = os.path.join(base_download_path, "middleEast", today)
    if not os.path.exists(middle_east_path):
        os.makedirs(middle_east_path)
        print(f"중동 서비스 폴더 생성 완료: {middle_east_path}")
    
    # westIndia 폴더 생성
    west_india_path = os.path.join(base_download_path, "westIndia", today)
    if not os.path.exists(west_india_path):
        os.makedirs(west_india_path)
        print(f"서인도 서비스 폴더 생성 완료: {west_india_path}")
    
    # 현재는 middleEast 사용 (향후 서비스별로 분류 가능)
    download_path = middle_east_path
    
    try:
        print("RCL 사이트 접속 시도 중...")
        
        # seleniumbase를 사용하여 클라우드플레어 우회
        with SB(uc=True, test=True) as sb:
            url = "https://www.rclgroup.com/Home#sailing"
            
            # 클라우드플레어 우회를 위한 접속
            print("클라우드플레어 우회 시도 중...")
            sb.uc_open_with_reconnect(url, reconnect_time=100)
            
            # CAPTCHA 처리 건너뛰기 (수동 처리 시 이미 통과했으므로)
            print("CAPTCHA 처리 건너뛰기 - 수동 처리 시 이미 통과됨")
            
            print("RCL 사이트 접속 성공! 모든 작업을 빠르게 처리합니다.")
            
            ## 1. 쿠키 팝업 처리 (즉시 시도)
            try:
                print("쿠키 팝업 처리 중...")
                # seleniumbase의 명시적 대기 사용
                cookie_button = sb.wait_for_element_visible("//*[@id='cc_dialog']/div/div[2]/button[1]", timeout=5)
                
                # JavaScript로 클릭 시도
                try:
                    sb.execute_script("arguments[0].click();", cookie_button)
                    print("쿠키 팝업 처리 완료 (JavaScript 클릭)")
                except Exception as js_e:
                    print(f"JavaScript 클릭 실패: {js_e}")
                    # 일반 클릭으로 재시도
                    try:
                        cookie_button.click()
                        print("쿠키 팝업 처리 완료 (일반 클릭)")
                    except Exception as click_e:
                        print(f"일반 클릭도 실패: {click_e}")
                        print("쿠키 팝업 처리 실패")
            except Exception as e:
                print("쿠키 팝업이 없거나 이미 처리됨")
            
            ## 2. Origin Port 입력 (즉시 처리)
            try:
                print(f"Origin Port '{origin_port}' 입력 중...")
                origin_input = sb.wait_for_element("#originInput", timeout=5)  # ID로 변경
                origin_input.click()
                origin_input.clear()
                origin_input.send_keys(origin_port)
                print(f"Origin Port '{origin_port}' 입력 완료")
                
                # 자동완성 리스트 즉시 선택
                try:
                    autocomplete_item = sb.find_element("//*[@id='mainSail']/div[2]/div[1]/ul/li")
                    autocomplete_item.click()
                    print(f"Origin Port '{origin_port}' 자동완성 선택 완료")
                except Exception as e:
                    print("Origin Port 자동완성 없이 계속 진행")
                
            except Exception as e:
                print(f"Origin Port 입력 실패: {e}")
                return
            
            ## 3. Destination Port 입력 (즉시 처리)
            try:
                print(f"Destination Port '{destination_port}' 입력 중...")
                desti_input = sb.find_element("#destiInput")  # ID로 변경
                desti_input.click()
                desti_input.clear()
                desti_input.send_keys(destination_port)
                print(f"Destination Port '{destination_port}' 입력 완료")
                
                # 자동완성 리스트 즉시 선택
                try:
                    autocomplete_item = sb.find_element("//*[@id='mainSail']/div[2]/div[4]/ul/li")
                    autocomplete_item.click()
                    print(f"Destination Port '{destination_port}' 자동완성 선택 완료")
                except Exception as e:
                    print("Destination Port 자동완성 없이 계속 진행")
                
            except Exception as e:
                print(f"Destination Port 입력 실패: {e}")
                return
            
            ## 4. 검색 버튼 클릭
            try:
                print("검색 버튼 클릭 중...")
                search_button = sb.find_element("//*[@id='sailSearch']")
                search_button.click()
                print("검색 버튼 클릭 완료")
                time.sleep(3)  # 검색 결과 로딩 대기 (5초 → 3초)
                
                print("RCL 스케줄 검색 완료!")
                print("브라우저를 열어둔 상태로 유지합니다. 확인 후 엔터를 누르면 브라우저가 닫힙니다.")
                
                # 브라우저 유지 (데이터 확인용)
                input("엔터를 누르면 브라우저가 닫힙니다...")
                
                # 브라우저 닫기
                sb.quit()
                print("브라우저가 닫혔습니다.")
                
            except Exception as e:
                print(f"검색 버튼 클릭 실패: {e}")
                return
                
    except Exception as e:
        print(f"RCL 스케줄 크롤링 중 오류 발생: {e}")

if __name__ == '__main__':
    rcl_schedule_crawling()