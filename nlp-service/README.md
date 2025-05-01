# 삼성 레포트 NLP 서비스

삼성 레포트를 분석하기 위한 NLP 서비스입니다.

## 기능

- 삼성 레포트 목록 조회
- 특정 레포트 상세 정보 조회
- 레포트 내 키워드 추출
- 레포트 감성 분석

## 개발 환경 설정

### 요구사항

- Python 3.9+
- Docker 및 Docker Compose

### 로컬 개발 환경 설정

1. 가상 환경 생성 및 활성화
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

3. 애플리케이션 실행
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 7000
   ```

### Docker를 이용한 실행

```bash
docker-compose up -d
```

## 테스트

테스트를 실행하는 방법:

```bash
python run_tests.py
```

또는 unittest 직접 사용:

```bash
python -m unittest discover app/test
```

## API 문서

서버 실행 후, 다음 URL에서 API 문서 확인 가능:

- Swagger UI: http://localhost:7000/docs
- ReDoc: http://localhost:7000/redoc

## 주요 엔드포인트

- `GET /samsung/test`: 테스트 엔드포인트 ("test파일입니다" 메시지 출력)
- `GET /samsung/reports`: 삼성 레포트 목록 조회
- `GET /samsung/reports/{report_id}`: 특정 레포트 상세 정보 조회
- `POST /samsung/reports/{report_id}/keywords`: 레포트에서 키워드 추출
- `POST /samsung/reports/{report_id}/sentiment`: 레포트 감성 분석 