from fastapi import Body, FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
from contextlib import asynccontextmanager
import os
import logging
import json
from dotenv import load_dotenv

# ✅ 서브 라우터 임포트

from app.domain.model.service_type import ServiceType
from app.domain.model.service_proxy_factory import ServiceProxyFactory

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("gateway_api")

# ✅ 환경 변수 로드
load_dotenv()

# ✅ 라이프스팬 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    logger.info(f"서비스 URL 구성:")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

# ✅ FastAPI 앱 설정
app = FastAPI(
    title="Gateway API",
    description="Gateway API for kimdonghee.com",
    version="0.1.0",
)

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 메인 API 라우터 생성
api_router = APIRouter(prefix="/ai/v1", tags=["Gateway API"])

# ✅ 메인 라우터 실행

# ✅ GET 프록시
@api_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: ServiceType,
    path: str,
    request: Request
):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="GET",
        path=path,
        headers=dict(request.headers)
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ✅ POST 프록시 (💥 수정됨)
@api_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: ServiceType,
    path: str,
    body: dict = Body(...)  # ✅ Swagger에서 입력 가능하게 수정
):
    logger.info(f"🌈 Received POST request for service: {service}, path: {path}")
    factory = ServiceProxyFactory(service_type=service)

    response = await factory.request(
        method="POST",
        path=path,
        headers={"Content-Type": "application/json"},
        body=json.dumps(body).encode("utf-8")
    )
    if response.status_code == 200:
        try:
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except json.JSONDecodeError:
            return JSONResponse(
                content={"detail": "⚠️ Invalid JSON response from service"},
                status_code=500
            )
    else:
        return JSONResponse(
            content={"detail": f"Service error: {response.text}"},
            status_code=response.status_code
        )


# ✅ PUT 프록시
@api_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(
    service: ServiceType,
    path: str,
    request: Request
):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="PUT",
        path=path,
        headers=dict(request.headers),
        body=await request.body()
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ✅ DELETE 프록시
@api_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(
    service: ServiceType,
    path: str,
    request: Request
):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="DELETE",
        path=path,
        headers=dict(request.headers),
        body=await request.body()
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ✅ PATCH 프록시
@api_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(
    service: ServiceType,
    path: str,
    request: Request
):
    factory = ServiceProxyFactory(service_type=service)
    response = await factory.request(
        method="PATCH",
        path=path,
        headers=dict(request.headers),
        body=await request.body()
    )
    return JSONResponse(content=response.json(), status_code=response.status_code)

# ✅ 메인 라우터 등록
app.include_router(api_router)

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9000))  # 기본 9000
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)


