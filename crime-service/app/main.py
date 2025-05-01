from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
from contextlib import asynccontextmanager
import os
import logging
import json
from dotenv import load_dotenv
from app.api.crime_router import router as crime_api_router

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("crime_service")

# ✅ 환경 변수 로드
load_dotenv()

# ✅ 라이프스팬 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚨 범죄 예측 서비스 시작")
    yield
    logger.info("🛑 범죄 예측 서비스 종료")

# ✅ FastAPI 앱 설정
app = FastAPI(
    title="Crime Prediction Service",
    description="Crime Prediction Service API",
    version="0.1.0",
    lifespan=lifespan
)

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 서브 라우터 생성
crime_router = APIRouter(prefix="/crime", tags=["Finance API"])

# ✅ 서브 라우터와 엔드포인트를 연결함
app.include_router(crime_api_router, prefix="/crime")


# ✅ 서브 라우터 등록
app.include_router(crime_router)

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9002))  # Crime 서비스는 9002 포트 사용
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
