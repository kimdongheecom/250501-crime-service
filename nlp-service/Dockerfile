FROM python:3.12.7-slim


# 2. Java 설치 (KoNLPy용)
RUN apt-get update && \
    apt-get install -y wget curl gnupg2 openjdk-17-jdk && \
    apt-get clean

# 3. Java 환경변수 설정
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

# Python 모듈 경로 설정
ENV PYTHONPATH="/app:${PYTHONPATH}"

# 의존성 설치를 위한 requirements.txt 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK 데이터 다운로드
RUN python -m nltk.downloader punkt

# 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 7000

# 실행 명령
CMD ["uvicorn", "app.test.test_samsung_report:app", "--host", "0.0.0.0", "--port", "7000"]