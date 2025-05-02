FROM python:3.12.7-slim



WORKDIR /app

# 의존성 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# 명시적으로 python-multipart 패키지 먼저 설치
RUN pip install python-multipart==0.0.15

# 나머지 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# NLTK 패키지 설치 및 데이터 다운로드
RUN pip install nltk
RUN python -m nltk.downloader punkt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 7070

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7070"]