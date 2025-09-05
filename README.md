# BSA Index Predict - Shipping Schedule Crawling Project

이 프로젝트는 다양한 선사들의 스케줄 데이터를 자동으로 수집하는 웹 스크래핑 도구입니다.

## 🚢 지원 선사

- **MSC** (Mediterranean Shipping Company) - `msc.py`
- **HMM** (Hyundai Merchant Marine) - `hmm.py`  
- **Maersk** - `masersk.py`
- **COSCO** - `cosco.py`
- **RCL** - `rcl.py`
- **SCFI** (Shanghai Containerized Freight Index) - `scfi.py`
- **Delay Analysis** - `delay.py`

## 📁 프로젝트 구조

```
BSA_IndexPredict/
├── MSC_DATA/           # MSC 스케줄 데이터
│   └── YYMMDD/        # 날짜별 폴더
├── HMM_DATA/          # HMM 스케줄 데이터
│   ├── middleEast/    # 중동 서비스
│   └── westIndia/     # 서인도 서비스
├── COSCO_DATA/        # COSCO 스케줄 데이터
├── MASERSK_DATA/      # Maersk 스케줄 데이터
├── RCL_DATA/          # RCL 스케줄 데이터
├── DATA/              # 기타 데이터 파일
└── downloaded_files/  # 임시 다운로드 파일
```

## 🛠️ 설치 방법

### 1. Python 환경 설정
```bash
# Python 3.8 이상 필요
python --version
```

### 2. 의존성 설치
```bash
# 모든 의존성 한번에 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install selenium pandas openpyxl xlrd pyshadow seleniumbase
```

### 3. Chrome 브라우저 설치
- Chrome 브라우저가 설치되어 있어야 합니다
- ChromeDriver는 자동으로 관리됩니다

## 🚀 사용 방법

### MSC 스케줄 크롤링
```bash
python msc.py
```
- 3개 항로 지원: FALCON, Shikra, Clanga
- 자동으로 Excel 파일 생성

### HMM 스케줄 크롤링
```bash
python hmm.py
```
- 중동 서비스, 서인도 서비스 지원
- XLS → CSV 자동 변환

### 기타 선사 스케줄 크롤링
```bash
python cosco.py
python masersk.py
python rcl.py
python scfi.py
```

## 📊 출력 파일 형식

### MSC
- 파일명: `MSC_Schedule_{서비스명}_YYMMDD.xlsx`
- 컬럼: Port, ETA, ETD
- 날짜 형식: `2025-09-27-토-15:00`

### HMM
- 파일명: `XX_FROM_PORT_TO_PORT.xls` + `.csv`
- 자동으로 CSV 변환 제공
- UTF-8 인코딩 지원

## ⚙️ 주요 기능

- **자동 브라우저 제어**: Selenium WebDriver 사용
- **봇 감지 방지**: 다양한 Chrome 옵션 적용
- **자동 파일 관리**: 날짜별 폴더 자동 생성
- **데이터 변환**: XLS → CSV 자동 변환
- **에러 처리**: 안정적인 예외 처리
- **다국어 지원**: 한글 포트명 지원

## 🔧 설정 옵션

### Chrome 옵션
- 봇 감지 방지 설정
- 백그라운드 서비스 비활성화
- 사용자 에이전트 설정

### 대기 시간 최적화
- 자동완성: 2초
- 검색 결과: 3초
- 다운로드: 2초

## 📝 주의사항

1. **네트워크 연결**: 안정적인 인터넷 연결 필요
2. **브라우저 업데이트**: Chrome 브라우저 최신 버전 권장
3. **파일 권한**: 다운로드 폴더 쓰기 권한 필요
4. **포트명 정확성**: 정확한 포트명 입력 필요

## 🐛 문제 해결

### ChromeDriver 오류
```bash
# ChromeDriver 재설치
pip install --upgrade selenium
```

### 파일 다운로드 실패
- 다운로드 폴더 권한 확인
- Chrome 다운로드 설정 확인

### 포트명 인식 실패
- 포트명 대소문자 확인
- 특수문자 제거

## 📞 지원

프로젝트 관련 문의사항이 있으시면 이슈를 등록해 주세요.

---

**Last Updated**: 2025-01-09
**Version**: 1.0.0
