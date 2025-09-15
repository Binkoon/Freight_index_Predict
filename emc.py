"""
EMC (Evergreen Marine Corporation) 데이터 수집 스크립트
1. EMC 데이터 URL에서 txt 파일 다운로드
2. txt 파일을 CSV 형태로 변환
3. EMC_DATA 폴더 안에 저장
4. 파일명은 EMC_CIX2_250915 형식으로 저장
"""

import requests
import pandas as pd
import os
import re
from datetime import datetime
from urllib.parse import urljoin

def download_emc_data(url, filename):
    """
    EMC 데이터 URL에서 txt 파일 다운로드
    """
    try:
        print(f"EMC 데이터 다운로드 시작: {url}")
        
        # HTTP 요청으로 데이터 다운로드
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 응답 내용 확인
        content = response.text
        print(f"다운로드된 데이터 크기: {len(content)} 문자")
        
        # 파일 저장
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"파일 저장 완료: {filename}")
        return True
        
    except Exception as e:
        print(f"다운로드 실패: {e}")
        return False

def parse_txt_to_csv(txt_content):
    """
    txt 파일 내용을 파싱하여 CSV 형태로 변환
    """
    try:
        lines = txt_content.strip().split('\n')
        
        # 데이터 파싱
        parsed_data = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 탭이나 공백으로 구분된 데이터 파싱
            # 일반적인 EMC 스케줄 데이터 형식에 맞게 파싱
            if '\t' in line:
                # 탭으로 구분된 경우
                parts = line.split('\t')
            else:
                # 공백으로 구분된 경우 (연속된 공백도 처리)
                parts = re.split(r'\s{2,}', line)
            
            # 빈 부분 제거
            parts = [part.strip() for part in parts if part.strip()]
            
            if len(parts) >= 2:  # 최소 2개 컬럼이 있는 경우만 처리
                parsed_data.append(parts)
        
        return parsed_data
        
    except Exception as e:
        print(f"텍스트 파싱 실패: {e}")
        return []

def create_emc_data_folder():
    """
    EMC_DATA 폴더 생성
    """
    emc_data_path = "EMC_DATA"
    if not os.path.exists(emc_data_path):
        os.makedirs(emc_data_path)
        print(f"EMC_DATA 폴더 생성 완료: {emc_data_path}")
    return emc_data_path

def save_to_csv(data, filename):
    """
    파싱된 데이터를 CSV 파일로 저장
    """
    try:
        if not data:
            print("저장할 데이터가 없습니다.")
            return False
        
        # DataFrame 생성
        # 컬럼 수가 일정하지 않을 수 있으므로 최대 컬럼 수 찾기
        max_columns = max(len(row) for row in data) if data else 0
        
        # 컬럼명 생성
        columns = [f'Column_{i+1}' for i in range(max_columns)]
        
        # 데이터 정규화 (모든 행을 같은 컬럼 수로 맞춤)
        normalized_data = []
        for row in data:
            normalized_row = row + [''] * (max_columns - len(row))
            normalized_data.append(normalized_row[:max_columns])
        
        # DataFrame 생성
        df = pd.DataFrame(normalized_data, columns=columns)
        
        # CSV 파일 저장
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"CSV 파일 저장 완료: {filename}")
        print(f"총 {len(data)}개의 데이터 행 저장됨")
        
        return True
        
    except Exception as e:
        print(f"CSV 저장 실패: {e}")
        return False

def process_single_service(service_name, url, emc_data_path):
    """
    단일 서비스 데이터 처리 함수
    """
    try:
        print(f"\n=== {service_name} 서비스 처리 시작 ===")
        
        # 오늘 날짜로 파일명 생성
        today = datetime.now().strftime("%y%m%d")
        filename = f"EMC_{service_name}_{today}"
        txt_filepath = os.path.join(emc_data_path, f"{filename}.txt")
        csv_filepath = os.path.join(emc_data_path, f"{filename}.csv")
        
        # 데이터 다운로드
        if not download_emc_data(url, txt_filepath):
            print(f"{service_name} 데이터 다운로드에 실패했습니다.")
            return False
        
        # txt 파일 내용 읽기
        try:
            with open(txt_filepath, 'r', encoding='utf-8') as f:
                txt_content = f.read()
        except UnicodeDecodeError:
            # UTF-8로 읽기 실패 시 다른 인코딩 시도
            try:
                with open(txt_filepath, 'r', encoding='cp949') as f:
                    txt_content = f.read()
            except:
                with open(txt_filepath, 'r', encoding='latin-1') as f:
                    txt_content = f.read()
        
        # txt 내용을 CSV 형태로 변환
        parsed_data = parse_txt_to_csv(txt_content)
        
        if not parsed_data:
            print(f"{service_name} 데이터 파싱에 실패했습니다.")
            return False
        
        # CSV 파일로 저장
        if save_to_csv(parsed_data, csv_filepath):
            # txt 파일 삭제
            try:
                os.remove(txt_filepath)
                print(f"임시 txt 파일 삭제 완료: {txt_filepath}")
            except Exception as e:
                print(f"txt 파일 삭제 실패: {e}")
            
            print(f"=== {service_name} 서비스 처리 완료 ===")
            print(f"CSV 파일: {csv_filepath}")
            return True
        else:
            print(f"{service_name} CSV 저장에 실패했습니다.")
            return False
        
    except Exception as e:
        print(f"{service_name} 서비스 처리 중 오류 발생: {e}")
        return False

def emc_data_processing():
    """
    EMC 데이터 수집 및 처리 메인 함수 (모든 서비스 처리)
    """
    try:
        # 1. EMC_DATA 폴더 생성
        emc_data_path = create_emc_data_folder()
        
        # 2. 처리할 서비스 목록 정의
        services = [
            {
                "name": "CIX2",
                "url": "https://ss.shipmentlink.com/tvs2/download_txt/CIX2_9.txt",
                "description": "China - India Express Service (CIX2)"
            },
            {
                "name": "CIX8", 
                "url": "https://ss.shipmentlink.com/tvs2/download_txt/CIX8_9.txt",
                "description": "China - India Express Service 8(CIX8)"
            },
            {
                "name": "CIX",
                "url": "https://ss.shipmentlink.com/tvs2/download_txt/CIX_9.txt", 
                "description": "China - India Express Service(CIX)"
            }
        ]
        
        # 3. 각 서비스별로 데이터 처리
        success_count = 0
        total_count = len(services)
        
        for i, service in enumerate(services, 1):
            print(f"\n{'='*60}")
            print(f"서비스 {i}/{total_count}: {service['description']}")
            print(f"{'='*60}")
            
            if process_single_service(service['name'], service['url'], emc_data_path):
                success_count += 1
                print(f"✅ {service['name']} 서비스 처리 성공")
            else:
                print(f"❌ {service['name']} 서비스 처리 실패")
        
        # 4. 전체 결과 요약
        print(f"\n{'='*60}")
        print(f"EMC 전체 서비스 처리 완료")
        print(f"{'='*60}")
        print(f"성공: {success_count}/{total_count} 서비스")
        
        if success_count == total_count:
            print("🎉 모든 EMC 서비스 데이터 수집이 완료되었습니다!")
            return True
        else:
            print(f"⚠️ {total_count - success_count}개 서비스에서 오류가 발생했습니다.")
            return False
        
    except Exception as e:
        print(f"EMC 데이터 처리 중 전체 오류 발생: {e}")
        return False

if __name__ == '__main__':
    emc_data_processing()