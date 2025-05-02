from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
from contextlib import asynccontextmanager
import os
import logging
import json
from dotenv import load_dotenv

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("tf_service")

# ✅ 환경 변수 로드
try:
    load_dotenv()
except:
    logger.info("dotenv 로드 실패, 계속 진행합니다.")

# ✅ 라이프스팬 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚨 TensorFlow 서비스 시작")
    yield
    logger.info("🛑 TensorFlow 서비스 종료")

# ✅ FastAPI 앱 설정
app = FastAPI(
    title="TensorFlow Service",
    description="TensorFlow Service API",
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

# ✅ 서브 라우터 등록
from app.api.file_router import router as file_router
app.include_router(
    file_router, 
    prefix="/api", 
    tags=["File Router"],
    responses={404: {"description": "Not found"}}
)

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7070))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)





