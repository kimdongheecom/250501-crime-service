# 컨트롤러 패키지 초기화 
import os

# 프로젝트 경로 설정
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stored_data')
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'updated_data')

# 디렉토리가 없으면 생성
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True) 