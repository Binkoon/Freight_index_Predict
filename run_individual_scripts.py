"""
개별 선사 스크립트들을 순차적으로 실행하는 스크립트
팩토리 패턴 대신 검증된 개별 스크립트들을 사용
"""

import subprocess
import sys
import time
from datetime import datetime

def run_script(script_name, description):
    """개별 스크립트 실행"""
    print(f"\n{'='*60}")
    print(f"🚢 {description} 실행 중...")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        
        # 스크립트 실행
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=1800)  # 30분 타임아웃
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} 실행 성공! (소요시간: {elapsed_time/60:.1f}분)")
            return True
        else:
            print(f"❌ {description} 실행 실패!")
            print(f"오류 출력: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} 실행 시간 초과 (30분)")
        return False
    except Exception as e:
        print(f"❌ {description} 실행 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚢 개별 선사 스크립트 순차 실행 시스템")
    print("=" * 80)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 실행할 스크립트 목록 (우선순위 순)
    scripts = [
        ("emc.py", "EMC 데이터 수집 (HTTP 기반 - 안정적)"),
        ("msc.py", "MSC 데이터 수집 (Selenium 기반)"),
        ("cosco.py", "COSCO 데이터 수집 (Selenium 기반)"),
        ("hmm.py", "HMM 데이터 수집 (Selenium 기반)"),
        ("masersk.py", "Maersk 데이터 수집 (Selenium 기반)"),
    ]
    
    print(f"📋 실행 대상: {len(scripts)}개 스크립트")
    print()
    
    # 전체 실행 시작
    start_time = time.time()
    results = {}
    
    for script, description in scripts:
        success = run_script(script, description)
        results[description] = success
        
        # 다음 스크립트 실행 전 잠시 대기
        if success:
            print("⏳ 다음 스크립트 실행을 위해 5초 대기...")
            time.sleep(5)
    
    # 결과 요약
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("📊 전체 실행 결과 요약")
    print("=" * 80)
    
    success_count = 0
    total_count = len(scripts)
    
    for description, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{description[:50]:50} : {status}")
        if success:
            success_count += 1
    
    print("-" * 80)
    print(f"성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"총 소요 시간: {elapsed_time/60:.1f}분")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == total_count:
        print("\n🎉 모든 선사 데이터 수집이 성공적으로 완료되었습니다!")
    else:
        print(f"\n⚠️ {total_count - success_count}개 선사에서 오류가 발생했습니다.")
    
    print("=" * 80)

def run_selected_scripts(script_names):
    """선택된 스크립트들만 실행"""
    script_mapping = {
        "emc": ("emc.py", "EMC 데이터 수집"),
        "msc": ("msc.py", "MSC 데이터 수집"),
        "cosco": ("cosco.py", "COSCO 데이터 수집"),
        "hmm": ("hmm.py", "HMM 데이터 수집"),
        "maersk": ("masersk.py", "Maersk 데이터 수집"),
    }
    
    print(f"🚢 선택된 스크립트 실행: {', '.join(script_names)}")
    print("-" * 60)
    
    results = {}
    for name in script_names:
        if name.lower() in script_mapping:
            script, description = script_mapping[name.lower()]
            success = run_script(script, description)
            results[description] = success
        else:
            print(f"❌ 알 수 없는 스크립트: {name}")
            results[name] = False
    
    print("\n📊 실행 결과:")
    for description, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{description}: {status}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 명령행 인수로 스크립트명이 주어진 경우
        script_names = [arg.lower() for arg in sys.argv[1:]]
        run_selected_scripts(script_names)
    else:
        # 기본: 모든 스크립트 실행
        main()
