FROM python:3.12.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 누락된 경우 대비: xlrd 명시적 설치
RUN pip install --no-cache-dir xlrd>=2.0.1

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9002", "--reload"]
